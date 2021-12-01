from __future__ import annotations

import functools
import typing
import uuid

import sqlalchemy
import sqlalchemy.orm

from . import Base
from .group import Group
from .helpers import (
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
	UUID
)
from .user import user_groups

__all__ = [
	"Forum",
	"ForumParsedPermissions",
	"ForumPermissionsGroup",
	"ForumPermissionsUser",
	"forum_subscribers"
]


forum_subscribers = sqlalchemy.Table(
	"forum_subscribers",
	Base.metadata,
	sqlalchemy.Column(
		"forum_id",
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	),
	sqlalchemy.Column(
		"user_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
)


@sqlalchemy.orm.declarative_mixin
class ForumPermissionMixin:
	"""A `Forum` helper mixin with columns corresponding to all permissions
	relevant in forums, as well as their default values and a `to_permissions`
	method.
	"""

	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_lock_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_lock_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_pin = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)

	DEFAULT_PERMISSIONS = {
		"forum_create": None,
		"forum_delete_own": None,
		"forum_delete_any": None,
		"forum_edit_own": None,
		"forum_edit_any": None,
		"forum_merge_own": None,
		"forum_merge_any": None,
		"forum_move_own": None,
		"forum_move_any": None,
		"forum_view": None,
		"post_create": None,
		"post_delete_own": None,
		"post_delete_any": None,
		"post_edit_own": None,
		"post_edit_any": None,
		"post_edit_vote": None,
		"post_move_own": None,
		"post_move_any": None,
		"post_view": None,
		"thread_create": None,
		"thread_delete_own": None,
		"thread_delete_any": None,
		"thread_edit_own": None,
		"thread_edit_any": None,
		"thread_edit_lock_own": None,
		"thread_edit_lock_any": None,
		"thread_edit_pin": None,
		"thread_edit_vote": None,
		"thread_merge_own": None,
		"thread_merge_any": None,
		"thread_move_own": None,
		"thread_move_any": None,
		"thread_view": None
	}

	def to_permissions(self: ForumPermissionMixin) -> typing.Dict[
		str,
		typing.Union[
			None,
			bool
		]
	]:
		"""Transforms the values in this instance to the standard format for
		permissions. (A dictionary, where string keys represent permissions,
		and their value represents whether or not they're granted.)
		"""

		return {
			permission_name: getattr(self, permission_name)
			for permission_name in self.DEFAULT_PERMISSIONS
		}


class ForumParsedPermissions(
	CDWMixin,
	ForumPermissionMixin,
	ReprMixin,
	Base
):
	"""A `Forum` helper model to store cached parsed permissions for specific
	users. Not meant to be exposed directly.
	"""

	__tablename__ = "forum_parsed_permissions"

	forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)

	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	post_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_lock_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_lock_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_pin = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	thread_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)

	def __repr__(self: ForumParsedPermissions) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			forum_id=self.forum_id,
			user_id=self.user_id
		)


class ForumPermissionsGroup(
	ForumPermissionMixin,
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""A `Forum` helper mixin to store permissions for specific `Group`s."""

	__tablename__ = "forum_permissions_group"

	forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	group_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"groups.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)

	def write(
		self: ForumPermissionsGroup,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Deletes the parent forum's `parsed_permissions` for the members of
		this instance's `group_id`.
		Adds this instance to the `session`.
		"""

		session.execute(
			sqlalchemy.select(ForumParsedPermissions).
			where(
				sqlalchemy.and_(
					ForumParsedPermissions.forum_id == self.forum_id,
					ForumParsedPermissions.user_id.in_(
						sqlalchemy.select(user_groups.c.user_id).
						where(user_groups.c.group_id == self.group_id)
					)
				)
			)
		)

		CDWMixin.write(self, session)

	def __repr__(self: ForumPermissionsGroup) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			forum_id=self.forum_id,
			group_id=self.group_id
		)


class ForumPermissionsUser(
	ForumPermissionMixin,
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""A `Forum` helper mixin to store permissions for specific `User`s."""

	__tablename__ = "forum_permissions_user"

	forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)

	def write(
		self: ForumPermissionsUser,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Deletes the parent forum's `parsed_permissions` for
		the associated user.
		Adds this instance to the `session`.
		"""

		session.execute(
			sqlalchemy.delete(ForumParsedPermissions).
			where(
				sqlalchemy.and_(
					ForumParsedPermissions.forum_id == self.forum_id,
					ForumParsedPermissions.user_id == self.user_id
				)
			)
		)

		CDWMixin.write(self, session)

	def __repr__(self: ForumPermissionsUser) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			forum_id=self.forum_id,
			user_id=self.user_id
		)


class Forum(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Forum model. Contains:
		- A nullable `parent_forum_id` column that corresponds to this forum's
		parent. This can later be used for nested permissions.
		- A `user_id` column, corresponding to the forum's owner.
		- `name` and `description` columns.
		- An `order` column, used for default ordering.
		- A dynamic `last_thread_timestamp` column, corresponding to the latest
		thread in this forum's `creation_timestamp`.
		- A dynamic `subscriber_count` column, corresponding to how many users
		have subscribed to this forum.
		- A dynamic `thread_count` column, corresponding to how many threads exist
		with this forum's `id` defined as their `forum_id`.
	"""

	__tablename__ = "forums"

	parent_forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=True
	)
	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=False
	)

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	description = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)

	order = sqlalchemy.Column(
		sqlalchemy.Integer,
		default=0,
		nullable=False
	)

	last_thread_timestamp = sqlalchemy.orm.column_property(
		sqlalchemy.select(sqlalchemy.text("threads.creation_timestamp")).
		select_from(sqlalchemy.text("threads")).
		where(
			sqlalchemy.text("threads.forum_id = forums.id")
		).
		order_by(
			sqlalchemy.desc(sqlalchemy.text("threads.creation_timestamp"))
		).
		limit(1).
		scalar_subquery()
	)

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(forum_subscribers.c.forum_id)
		).
		where(forum_subscribers.c.forum_id == sqlalchemy.text("forums.id")).
		scalar_subquery()
	)

	thread_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("threads.id"))
		).
		select_from(sqlalchemy.text("threads")).
		where(
			sqlalchemy.text("threads.forum_id = forums.id")
		).
		scalar_subquery()
	)

	parsed_permissions = sqlalchemy.orm.relationship(
		ForumParsedPermissions,
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)

	permissions_groups = sqlalchemy.orm.relationship(
		ForumPermissionsGroup,
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
		order_by=sqlalchemy.desc(ForumPermissionsGroup.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)

	permissions_users = sqlalchemy.orm.relationship(
		ForumPermissionsUser,
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
		order_by=sqlalchemy.desc(ForumPermissionsUser.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)

	child_forums = sqlalchemy.orm.relationship(
		lambda: Forum,
		backref=sqlalchemy.orm.backref(
			"parent_forum",
			uselist=False,
			remote_side=lambda: Forum.id
		),
		order_by=lambda: sqlalchemy.desc(Forum.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)

	class_actions = {
		"create": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_create"]
		),
		"create_subforum": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_create"]
		),
		"create_thread": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["thread_view"] and
			user.parsed_permissions["thread_create"]
		),
		"create_thread_locked": lambda cls, user: (
			cls.get_class_permission(user, "create_thread") and
			user.parsed_permissions["thread_edit_lock_own"]
		),
		"create_thread_pinned": lambda cls, user: (
			cls.get_class_permission(user, "create_thread") and
			user.parsed_permissions["thread_edit_pin"]
		),
		"delete": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_delete_own"] or
				user.parsed_permissions["forum_delete_any"]
			)
		),
		"edit": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_edit_own"] or
				user.parsed_permissions["forum_edit_any"]
			)
		),
		"edit_permissions_group": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_edit_own"] or
				user.parsed_permissions["forum_edit_any"]
			)
		),
		"edit_permissions_user": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_edit_own"] or
				user.parsed_permissions["forum_edit_any"]
			)
		),
		"edit_subscription": lambda cls, user: (
			cls.get_class_permission(user, "view")
		),
		"merge": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_merge_own"] or
				user.parsed_permissions["forum_merge_any"]
			)
		),
		"move": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["forum_move_own"] or
				user.parsed_permissions["forum_move_any"]
			)
		),
		"view": lambda cls, user: user.parsed_permissions["forum_view"],
		"view_permissions_group": lambda cls, user: (
			cls.get_class_permission(user, "view")
		),
		"view_permissions_user": lambda cls, user: (
			cls.get_class_permission(user, "view")
		)
	}

	instance_actions = {
		"create_subforum": lambda self, user: (
			self.get_parsed_permissions(user.id).forum_create
		),
		"create_thread": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user.id).thread_view and
			self.get_parsed_permissions(user.id).thread_create
		),
		"create_thread_locked": lambda self, user: (
			self.get_instance_permission(user, "create_thread") and
			self.get_parsed_permissions(user.id).thread_edit_lock_own
		),
		"create_thread_pinned": lambda self, user: (
			self.get_instance_permission(user, "create_thread") and
			self.get_parsed_permissions(user.id).thread_edit_pin
		),
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_delete_own
				) or
				self.get_parsed_permissions(user.id).forum_delete_any
			)
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_edit_own
				) or
				self.get_parsed_permissions(user.id).forum_edit_any
			)
		),
		"edit_permissions_group": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_edit_own
				) or
				self.get_parsed_permissions(user.id).forum_edit_any
			)
		),
		"edit_permissions_user": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_edit_own
				) or
				self.get_parsed_permissions(user.id).forum_edit_any
			)
		),
		"edit_subscription": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"merge": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_merge_own
				) or
				self.get_parsed_permissions(user.id).forum_merge_any
			) and (
				not hasattr(self, "future_forum") or
				(
					(
						self.future_forum.user_id == user.id and
						self.future_forum.get_parsed_permissions(user.id).forum_merge_own
					) or
					self.future_forum.get_parsed_permissions(user.id).forum_merge_any
				)
			)
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.get_parsed_permissions(user.id).forum_move_own
				) or
				self.get_parsed_permissions(user.id).forum_move_any
			) and (
				not hasattr(self, "future_forum") or
				(
					(
						self.future_forum.user_id == user.id and
						self.future_forum.get_parsed_permissions(user.id).forum_move_own
					) or
					self.future_forum.get_parsed_permissions(user.id).forum_move_any
				)
			)
		),
		"view": lambda self, user: self.get_parsed_permissions(user.id).forum_view,
		"view_permissions_group": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"view_permissions_user": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}

	def _parse_child_level(
		self: Forum,
		current_id: uuid.UUID,
		session: sqlalchemy.orm.Session,
		child_level: int = 0,
	) -> int:
		"""Recursively obtains the current forum's child level."""

		parent_forum_id = session.execute(
			sqlalchemy.select(Forum.parent_forum_id).
			where(Forum.id == current_id)
		).scalars().one_or_none()

		if parent_forum_id is not None:
			child_level += 1

			return self._parse_child_level(
				parent_forum_id,
				child_level
			)

		return child_level

	def get_child_level(
		self: Forum,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Returns the child level of this forum. For example, if there is a parent
		forum which is itself the child of another forum, the level will be 2.
		"""

		if self.parent_forum_id is None:
			return 0

		return self._parse_child_level(
			self.id,
			session if session is not None else sqlalchemy.orm.object_session(self)
		)

	def _get_permissions_group(
		self: Forum,
		group_id: uuid.UUID,
		session: sqlalchemy.orm.Session
	) -> typing.Dict[str, bool]:
		"""Gets this forum's permissions for the group with the given `group_id`,
		as well as the parent forums'. This forum's permissions will take
		precedence.
		"""

		parsed_group_permissions = {}

		own_group_permissions = session.execute(
			sqlalchemy.select(ForumPermissionsGroup).
			where(
				sqlalchemy.and_(
					ForumPermissionsGroup.group_id == group_id,
					ForumPermissionsGroup.forum_id == self.id
				)
			)
		).scalars().one_or_none()

		if own_group_permissions is not None:
			parsed_group_permissions = own_group_permissions.to_permissions()

		if self.parent_forum_id is not None:
			for permission_name, permission_value in (
				self.parent_forum._get_permissions_group(group_id, session).items()
			):
				if (
					permission_value is None or
					parsed_group_permissions.get(permission_name) is not None
				):
					continue

				parsed_group_permissions[permission_name] = permission_value

		return parsed_group_permissions

	def _get_permissions_user(
		self: Forum,
		user_id: uuid.UUID,
		session: sqlalchemy.orm.Session
	) -> typing.Dict[str, bool]:
		"""Gets this forum's permissions for the user with the given `user_id`,
		as well as the parent forums'. This forum's permissions will take
		precedence.
		"""

		parsed_user_permissions = {}

		own_user_permissions = session.execute(
			sqlalchemy.select(ForumPermissionsUser).
			where(
				sqlalchemy.and_(
					ForumPermissionsUser.user_id == user_id,
					ForumPermissionsUser.forum_id == self.id
				)
			)
		).scalars().one_or_none()

		if own_user_permissions is not None:
			parsed_user_permissions = own_user_permissions.to_permissions()

		if self.parent_forum_id is not None:
			for permission_name, permission_value in (
				self.parent_forum._get_permissions_user(user_id, session).items()
			):
				if (
					permission_value is None or
					parsed_user_permissions.get(permission_name) is not None
				):
					continue

				parsed_user_permissions[permission_name] = permission_value

		return parsed_user_permissions

	@functools.lru_cache()
	def get_parsed_permissions(
		self: Forum,
		user_id: uuid.UUID,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> typing.Union[
		None,
		ForumParsedPermissions
	]:
		"""Returns this forum's parsed permissions for user with the given
		`user_id`.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		return session.execute(
			sqlalchemy.select(ForumParsedPermissions).
			where(
				sqlalchemy.and_(
					ForumParsedPermissions.forum_id == self.id,
					ForumParsedPermissions.user_id == user_id
				)
			)
		).scalars().one_or_none()

	def reparse_permissions(
		self: Forum,
		user,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Sets the given user's `ForumParsedPermissions` to:
			- The given `user`'s `parsed_permissions`.
			- Any defined permissions for groups that this `user` is part of for
			this forum, as well as the parent forum(s),
			where the group with the highest level is most important.
			- Any permissions specific to the given `user` defined for this forum,
			as well as the parent forum(s).
		This instance of `ForumParsedPermissions` is created if inexistent,
		then filled with the calculated values.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		self.get_parsed_permissions.cache_clear()

		parsed_permissions = {}

		for group_id in session.execute(
			sqlalchemy.select(user_groups.c.group_id).
			where(user_groups.c.user_id == user.id).
			order_by(
				sqlalchemy.desc(
					sqlalchemy.select(Group.level).
					where(Group.id == user_groups.c.group_id).
					scalar_subquery()
				)
			)
		).scalars().all():
			for permission_name, permission_value in self._get_permissions_group(
				group_id,
				session
			):
				if (
					permission_value is None or
					parsed_permissions.get(permission_name) is not None
				):
					continue

				parsed_permissions[permission_name] = permission_value

		for permission_name, permission_value in self._get_permissions_user(
			user.id,
			session
		):
			if permission_value is None:
				continue

			parsed_permissions[permission_name] = permission_value

		for permission_name in ForumPermissionMixin.DEFAULT_PERMISSIONS:
			if parsed_permissions.get(permission_name) is None:
				parsed_permissions[
					permission_name
				] = user.parsed_permissions[
					permission_name
				]

		existing_parsed_permissions = self.get_parsed_permissions(user.id)

		if existing_parsed_permissions is None:
			ForumParsedPermissions.create(
				session,
				forum_id=self.id,
				user_id=user.id,
				**parsed_permissions
			)
		else:
			for permission_name, permission_value in parsed_permissions.items():
				setattr(
					existing_parsed_permissions,
					permission_name,
					permission_value
				)
