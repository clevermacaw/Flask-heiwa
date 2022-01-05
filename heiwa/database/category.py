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

	static_actions = {
		"create": lambda user: user.parsed_permissions["category_create"],
		"delete": lambda user: user.parsed_permissions["category_delete"],
		"edit": lambda user: user.parsed_permissions["category_edit"],
		"view": lambda user: user.parsed_permissions["forum_view"]
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
		Whether or not a user can view categories. This depends on the
		``forum_view`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	.. seealso::
		:attr:`.Group.instance_actions`

		:attr:`.Group.action_queries`
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
			user.parsed_permissions["forum_view"]
			if self.forum_id is None
			else self.forum.instance_actions["view"](self, user)
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
		associated with any forum, always :data:`True` by default as long as
		the user has permission to view forums. If it is associated with one,
		it depends on the user being able to view that forum.

	.. seealso::
		:attr:`.Group.static_actions`

		:attr:`.Group.action_queries`
	"""

	@staticmethod
	def _action_query_delete(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user``
		is allowed to delete categories.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Category.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					ForumParsedPermissions.category_delete.is_(True),
					~Category.forum_id.is_(None)
				),
				user.parsed_permissions["category_delete"]
			)
		)

	@staticmethod
	def _action_query_edit(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to edit categories.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Category.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					ForumParsedPermissions.category_edit.is_(True),
					~Category.forum_id.is_(None)
				),
				user.parsed_permissions["category_delete"]
			)
		)

	@staticmethod
	def _action_query_view(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to view categories.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.or_(
			sqlalchemy.and_(
				ForumParsedPermissions.forum_view.is_(True),
				~Category.forum_id.is_(None)
			),
			user.parsed_permissions["forum_view"]
		)

	action_queries = {
		"delete": _action_query_delete,
		"edit": _action_query_edit,
		"view": _action_query_view
	}
	"""Actions and their required permissions translated to be evaluable within
	SQL queries. Unless arbitrary additional attributes come into play, these
	permissions will generally be the same as
	:attr:`instance_actions <.Group.instance_actions>`.

	.. seealso::
		:attr:`.Category.instance_actions`

		:attr:`.Category.static_actions`
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
		order_by: typing.Union[
			None,
			sqlalchemy.sql.elements.UnaryExpression
		] = None,
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
			perform on categories, other than the default ``view`` action.
		:param conditions: Any additional conditions. :data:`True` by default,
			meaning there are no conditions.
		:param order_by: An expression to order by.
		:param limit: A limit.
		:param offset: An offset.
		:param ids_only: Whether or not to only return a query for IDs.

		:returns: The query.
		"""

		from .forum import Forum, ForumParsedPermissions

		inner_conditions = (
			sqlalchemy.and_(
				~cls.forum_id.is_(None),
				ForumParsedPermissions.forum_id == cls.forum_id,
				ForumParsedPermissions.user_id == user.id
			)
		)

		first_iteration = True
		category_without_parsed_forum_permissions_exists = False

		while (first_iteration or category_without_parsed_forum_permissions_exists):
			first_iteration = False

			rows = session.execute(
				sqlalchemy.select(
					cls.id,
					cls.forum_id,
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
										cls.action_queries["view"](user),
										sqlalchemy.and_(
											cls.action_queries[action](user)
											for action in additional_actions
										) if additional_actions is not None else True
									)
								).
								exists()
							)
						)
					)
				).
				order_by(order_by).
				limit(limit).
				offset(offset)
			).all()

			if len(rows) == 0:
				# No need to hit the database with a complicated query twice
				return (
					sqlalchemy.select(cls if not ids_only else cls.id).
					where(False)
				)

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

				session.commit()

			if ids_only:
				return sqlalchemy.select(category_ids)

			return (
				sqlalchemy.select(cls).
				where(cls.id.in_(category_ids)).
				order_by(order_by)
			)
