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
from .thread import Thread

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
		typing.Union[None, bool]
	]:
		"""Transforms the values in this instance to the standard format for
		permissions. (A dictionary, where string keys represent permissions,
		and their value represents whether or not they're granted.
		"""

		return {
			"forum_create": self.forum_create,
			"forum_delete_own": self.forum_delete_own,
			"forum_delete_any": self.forum_delete_any,
			"forum_edit_own": self.forum_edit_own,
			"forum_edit_any": self.forum_edit_any,
			"forum_merge_own": self.forum_merge_own,
			"forum_merge_any": self.forum_merge_any,
			"forum_move_own": self.forum_move_own,
			"forum_move_any": self.forum_move_any,
			"forum_view": self.forum_view,
			"post_create": self.post_create,
			"post_delete_own": self.post_delete_own,
			"post_delete_any": self.post_delete_any,
			"post_edit_own": self.post_edit_own,
			"post_edit_any": self.post_edit_any,
			"post_edit_vote": self.post_edit_vote,
			"post_move_own": self.post_move_own,
			"post_move_any": self.post_move_any,
			"post_view": self.post_view,
			"thread_create": self.thread_create,
			"thread_delete_own": self.thread_delete_own,
			"thread_delete_any": self.thread_delete_any,
			"thread_edit_own": self.thread_edit_own,
			"thread_edit_any": self.thread_edit_any,
			"thread_edit_lock_own": self.thread_edit_lock_own,
			"thread_edit_lock_any": self.thread_edit_lock_any,
			"thread_edit_pin": self.thread_edit_pin,
			"thread_edit_vote": self.thread_edit_vote,
			"thread_merge_own": self.thread_merge_own,
			"thread_merge_any": self.thread_merge_any,
			"thread_move_own": self.thread_move_own,
			"thread_move_any": self.thread_move_any,
			"thread_view": self.thread_view
		}


class ForumParsedPermissions(
	CDWMixin,
	ForumPermissionMixin,
	ReprMixin,
	Base
):
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

	user = sqlalchemy.orm.relationship(
		"User",
		uselist=False,
		lazy=True
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

	group = sqlalchemy.orm.relationship(
		"Group",
		uselist=False,
		lazy=True
	)

	def write(
		self: ForumPermissionsGroup,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Reparses the parent forum's `parsed_permissions`.
		Adds this instance to the `session`.
		"""

		self.forum.reparse_permissions()

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

	user = sqlalchemy.orm.relationship(
		"User",
		uselist=False,
		lazy=True
	)

	def write(
		self: ForumPermissionsUser,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Reparses the parent forum's `parsed_permissions`.
		Adds this instance to the `session`.
		"""

		self.forum.reparse_permissions()

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
	"""Heiwa forum model.
	Supports (effectively) infinite levels of child forums and subscriptions.
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
		sqlalchemy.select(Thread.creation_timestamp).
		where(Thread.forum_id == sqlalchemy.text("forums.id")).
		order_by(
			sqlalchemy.desc(Thread.creation_timestamp)
		).
		limit(1).
		scalar_subquery()
	)

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(
				forum_subscribers.c.forum_id
			)
		).
		where(forum_subscribers.c.forum_id == sqlalchemy.text("forums.id")).
		scalar_subquery()
	)

	thread_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Thread.id)
		).
		where(Thread.forum_id == sqlalchemy.text("forums.id")).
		scalar_subquery()
	)

	child_forums = sqlalchemy.orm.relationship(
		lambda: Forum,
		backref=sqlalchemy.orm.backref(
			"parent_forum",
			uselist=False,
			remote_side=lambda: Forum.id
		),
		passive_deletes="all",
		lazy=True
	)

	subscribers = sqlalchemy.orm.relationship(
		"User",
		secondary=forum_subscribers,
		order_by="desc(User.creation_timestamp)",
		lazy=True
	)
	threads = sqlalchemy.orm.relationship(
		"Thread",
		order_by="desc(Thread.creation_timestamp)",
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
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
	permissions_group = sqlalchemy.orm.relationship(
		ForumPermissionsGroup,
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)
	permissions_user = sqlalchemy.orm.relationship(
		ForumPermissionsUser,
		uselist=False,
		backref=sqlalchemy.orm.backref(
			"forum",
			uselist=False
		),
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
			Thread.get_class_permission(user, "view") and
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
			Thread.get_class_permission(user, "view") and
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
		child_level: int = 0
	) -> int:
		parent_forum_id = sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.select(Forum.parent_forum_id).
			where(Forum.id == current_id)
		).scalars().one_or_none()

		if parent_forum_id is not None:
			child_level += 1

			return self._parse_child_level(
				parent_forum_id,
				child_level
			)
		else:
			return child_level

	def get_child_level(self: Forum) -> None:
		"""Returns how "deep" this forum is. For example, if there is a parent
		forum which is itself the child of another forum, the level will be 2.
		"""

		if self.parent_forum_id is None:
			return 0

		return self._parse_child_level(self.id)

	def _get_parent_permissions_group(
		self: Forum,
		group_id: uuid.UUID
	) -> typing.Dict[str, bool]:
		if self.parent_forum is not None:
			parent_permissions = sqlalchemy.orm.object_session(self).execute(
				sqlalchemy.select(ForumPermissionsGroup).
				where(
					sqlalchemy.and_(
						ForumPermissionsGroup.group_id == group_id,
						ForumPermissionsGroup.forum_id == self.parent_forum_id
					)
				)
			).scalars().one_or_none()

			parsed_group_permissions = self.parent_forum._get_parent_permissions_group(
				group_id
			)

			if parent_permissions is None:
				return parsed_group_permissions

			for key, value in parent_permissions.to_permissions().items():
				if value is None:
					continue

				parsed_group_permissions[key] = value

			return parsed_group_permissions
		else:
			return {}

	def _get_parent_permissions_user(
		self: Forum,
		user_id: uuid.UUID
	) -> typing.Dict[str, bool]:
		if self.parent_forum is not None:
			parent_permissions = sqlalchemy.orm.object_session(self).execute(
				sqlalchemy.select(ForumPermissionsUser).
				where(
					sqlalchemy.and_(
						ForumPermissionsUser.user_id == user_id,
						ForumPermissionsUser.forum_id == self.parent_forum.id
					)
				)
			).scalars().one_or_none()

			parsed_user_permissions = self.parent_forum._get_parent_permissions_user(
				user_id
			)

			if parent_permissions is None:
				return parsed_user_permissions

			for key, value in parent_permissions.to_permissions().items():
				if value is None:
					continue

				parsed_user_permissions[key] = value

			return parsed_user_permissions
		else:
			return {}

	@functools.lru_cache()
	def get_parsed_permissions(
		self: Forum,
		user_id: uuid.UUID
	) -> typing.Union[
		None,
		ForumParsedPermissions
	]:
		return sqlalchemy.orm.object_session(self).execute(
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
		user
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

		self.get_parsed_permissions.cache_clear()

		group_ids = sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.select(Group.id).
			where(
				Group.users.any(id=user.id)
			).
			order_by(
				sqlalchemy.asc(Group.level)
			)
		).scalars().all()

		group_permission_sets = sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.select(ForumPermissionsGroup).
			where(
				sqlalchemy.and_(
					ForumPermissionsGroup.group_id.in_(group_ids),
					ForumPermissionsGroup.forum_id == self.id
				)
			).
			join(ForumPermissionsGroup.group).
			order_by(
				sqlalchemy.desc(Group.level)
			)
		).scalars().all()

		permissions_to_add = {}

		for group_id in group_ids:
			permissions_to_add = {
				**permissions_to_add,
				**self._get_parent_permissions_group(group_id)
			}

		permissions_to_add = {
			**permissions_to_add,
			**self._get_parent_permissions_user(user.id)
		}

		for permissions in group_permission_sets:
			for key, value in permissions.to_permissions().items():
				if key in permissions or key is None:
					continue

				permissions_to_add[key] = value

		if permissions_to_add == {}:
			permissions_to_add = ForumPermissionMixin.DEFAULT_PERMISSIONS

		user_permissions = sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.select(ForumPermissionsUser).
			where(
				sqlalchemy.and_(
					ForumPermissionsUser.user_id == user.id,
					ForumPermissionsUser.forum_id == self.id
				)
			)
		).scalars().one_or_none()

		if user_permissions is not None:
			for key, value in user_permissions.to_permissions().items():
				if value is None:
					continue

				permissions_to_add[key] = value

		parsed_permissions = {}

		for key, value in permissions_to_add.items():
			parsed_permissions[key] = (
				value
				if value is not None
				else user.parsed_permissions[key]
			)

		existing_parsed_permissions = self.get_parsed_permissions(user.id)

		if existing_parsed_permissions is None:
			ForumParsedPermissions.create(
				sqlalchemy.orm.object_session(self),
				forum_id=self.id,
				user_id=user.id,
				**parsed_permissions
			)
		else:
			# TODO: PEP 584

			for key, value in parsed_permissions.items():
				setattr(existing_parsed_permissions, key, value)
