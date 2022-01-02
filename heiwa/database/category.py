""""Models for categories."""

from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from . import Base
from .utils import (
	UUID,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin
)

__all__ = ["Category"]


class Category(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Category model.

	.. note::
		Like forums, categories have no owners.
	"""

	__tablename__ = "categories"

	forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=True
	)
	"""The :attr:`id <.Forum.id>` of the :class:`.Forum` a category falls under.
	Works almost identically to :attr:`.Forum.parent_forum_id`.

	.. note::
		The original purpose of this was dealing with forum-based permissions. An
		unintended side-effect was also establishing a relationship with forum
		parents and greatly simplifying categorization of subforums.
	"""

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	"""A category's name."""

	description = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=False
	)
	"""A category's description."""

	forum = sqlalchemy.orm.relationship(
		"Forum",
		uselist=False,
		passive_deletes="all",
		foreign_keys=[forum_id],
		lazy=True
	)
	"""The :class:`.Forum` a category falls under."""

	class_actions = {
		"create": lambda cls, user: user.parsed_permissions["category_create"],
		"delete": lambda cls, user: user.parsed_permissions["category_delete"],
		"edit": lambda cls, user: user.parsed_permissions["category_edit"],
		"view": lambda cls, user: True
	}
	r"""Actions :class:`User`\ s are allowed to perform on all categories, without
	any indication of which thread it is.

	``create``:
		Whether or not a user can create categories. This depends on the
		``category_create`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``delete``:
		Whether or not a user can delete categories. This depends on the
		``category_delete`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit``:
		Whether or not a user can edit categories. This depends on the
		``category_edit`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view``:
		Whether or not a user can view categories. Since we don't know whether
		or not they're attached to forums, this will always be :data:`True` by
		default.
	"""

	instance_actions = {
		"delete": lambda self, user: (
			user.parsed_permissions["category_delete"]
			if self.forum_id is None
			else self.forum.get_parsed_permissions(user).category_delete
		),
		"edit": lambda self, user: (
			user.parsed_permissions["category_edit"]
			if self.forum_id is None
			else self.forum.get_parsed_permissions(user).category_edit
		),
		"view": lambda self, user: (
			True
			if self.forum_id is None
			else self.forum.get_instance_permission(user, "view")
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on all categories, without
	any indication of which thread it is.

	``delete``:
		Whether or not a user can delete this category. This depends on the
		``category_delete`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>` if this category is
		not associated with any forum, otherwise it depends on the same value in
		the forum's permissions for them.

	``edit``:
		Whether or not a user can edit this category. This depends on the
		``category_edit`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>` if this category is
		not associated with any forum, otherwise it depends on the same value in
		the forum's permissions for them.

	``view``:
		Whether or not a user can view this category. If this category is not
		associated with any forum, always :data:`True` by default. If it is, it
		depends on the user being able to view the forum.
	"""

	@classmethod
	def get(
		cls: Category,
		user,
		session: sqlalchemy.orm.Session,
		additional_actions: typing.Union[
			None,
			typing.Iterable[str]
		] = None,
		conditions: typing.Union[
			bool,
			sqlalchemy.sql.expression.BinaryExpression,
			sqlalchemy.sql.expression.ClauseList
		] = True,
		limit: typing.Union[
			None,
			int
		] = None,
		offset: typing.Union[
			None,
			int
		] = None,
		ids_only: bool = False
	) -> sqlalchemy.sql.Select:
		"""Generates a selection query with permissions already handled.

		Since this category's :class:`.Forum`'s permissions may not be parsed,
		this will emit additional queries to check, as long there is a forum
		attached.

		:param user: The user whose permissions should be evaluated.
		:param session: The SQLAlchemy session to execute additional queries with.
		:param additional_actions: Additional actions that a user must be able to
			perform on this category, other than the default ``view`` action.
		:param conditions: Any additional conditions. :data:`True` by default,
			meaning there are no conditions.
		:param limit: A limit.
		:param offset: An offset.
		:param ids_only: Whether or not to only return a query for IDs.

		:returns: The query.
		"""

		from .forum import Forum, ForumParsedPermissions

		inner_conditions = (
			sqlalchemy.and_(
				~Category.forum_id.is_(None),
				ForumParsedPermissions.forum_id == Category.forum_id,
				ForumParsedPermissions.user_id == user.id
			)
		)

		first_iteration = True
		category_without_parsed_forum_permissions_exists = False

		while (first_iteration or category_without_parsed_forum_permissions_exists):
			first_iteration = False

			rows = session.execute(
				sqlalchemy.select(
					Category.id,
					Category.forum_id,
					(
						sqlalchemy.select(ForumParsedPermissions.forum_id).
						where(inner_conditions).
						exists()
					)
				).
				where(
					sqlalchemy.and_(
						conditions,
						sqlalchemy.or_(
							~(
								sqlalchemy.select(ForumParsedPermissions.forum_id).
								where(inner_conditions).
								exists()
							),
							(
								sqlalchemy.select(ForumParsedPermissions.forum_id).
								where(
									sqlalchemy.and_(
										inner_conditions,
										# TODO: Translate permissions
										ForumParsedPermissions.category_view.is_(True),
										sqlalchemy.and_(
											self.action_queries[action]
											for action in additional_actions
										) if additional_actions is not None else True
									)
								).
								exists()
							)
						)
					)
				).
				limit(limit).
				offset(offset)
			).all()

			if len(rows) == 0:
				# No need to select twice
				return sqlalchemy.select(None)

			category_ids = []
			unparsed_permission_forum_ids = []

			for row in rows:
				(
					category_id,
					forum_id,
					parsed_permissions_exist
				) = row

				if (
					forum_id is not None and
					not parsed_permissions_exist
				):
					category_without_parsed_forum_permissions_exists = True
					unparsed_permission_forum_ids.append(forum_id)

					continue

				category_ids.append(category_id)

			if category_without_parsed_forum_permissions_exists:
				for forum in (
					session.execute(
						sqlalchemy.select(Forum).
						where(Forum.id.in_(unparsed_permission_forum_ids))
					).scalars()
				):
					forum.reparse_permissions(user)

			return (
				sqlalchemy.select(
					Category if not ids_only else Category.id
				).
				where(
					sqlalchemy.and_(
						Category.id.in_(category_ids),
						conditions
					)
				).
				limit(limit).
				offset(offset)
			)
