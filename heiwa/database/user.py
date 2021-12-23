from __future__ import annotations

import datetime
import operator
import os
import typing

import flask
import sqlalchemy
import sqlalchemy.ext.hybrid
import sqlalchemy.orm

from . import Base
from .group import Group, GroupPermissions
from .helpers import (
	UUID,
	BasePermissionMixin,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
)
from .message import Message
from .notification import Notification

__all__ = [
	"User",
	"UserBan",
	"UserPermissions",
	"user_blocks",
	"user_follows",
	"user_groups"
]


user_blocks = sqlalchemy.Table(
	"user_blocks",
	Base.metadata,
	sqlalchemy.Column(
		"blocker_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	),
	sqlalchemy.Column(
		"blockee_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
)


user_groups = sqlalchemy.Table(
	"user_groups",
	Base.metadata,
	sqlalchemy.Column(
		"user_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	),
	sqlalchemy.Column(
		"group_id",
		UUID,
		sqlalchemy.ForeignKey(
			"groups.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
)


user_follows = sqlalchemy.Table(
	"user_follows",
	Base.metadata,
	sqlalchemy.Column(
		"follower_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	),
	sqlalchemy.Column(
		"followee_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
)


class UserBan(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""``User`` ban helper model.

	Contains:

	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A ``user_id`` foreign key column, associating this instance with its
	   ``User``.
	#. An ``expiration_timestamp`` column, signifying the time of this ban's
	   expiry.
	#. A nullable ``reason`` column.
	"""

	__tablename__ = "user_bans"

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)

	expiration_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		nullable=False
	)

	reason = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)


class UserPermissions(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	BasePermissionMixin,
	Base
):
	"""``User`` permission helper model.

	Contains:

	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. All columns from the ``BasePermissionMixin``.
	#. A ``user_id`` foreign key column, associating this instance with its
	   ``User``.
	"""

	__tablename__ = "user_permissions"

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)


class User(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""User model.

	Contains:

	#. An ``id`` column from the ``IdMixin``.
	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A nullable ``registered_by`` column that contains the service this user
	   was registered by. Groups whose ``default_for`` is at the start of it will
	   automatically be assigned to this user. By default, the only two services
	   that can register users are ``'/openid'`` and ``'/guest'`` APIs.
	#. A nullable ``external_id`` column, the service this user was registered
	   by's identifier for them.
	#. An ``avatar_type`` column, containing the MIME type of this user's
	   avatar, if there is one.
	#. An ``is_banned`` column, specifying whether or not this user has been
	   banned.
	#. A JSON ``parsed_permissions`` column, containing this user's parsed
	   permissions. This is a combination of this user's group's permissions
	   (where groups with the highest ``level`` take precedence), and this user's
	   specific permissions.
	#. An ``encrypted_private_key`` column, optionally used to store an encrypted
	#. A ``public_key`` column, containing this user's raw RSA public key.
	   version of this user's RSA private key. If desired, this can be left empty
	   with a public key still present.
	#. Nullable ``name`` and ``status`` columns.
	#. A dynamic, deferred ``followee_count`` column, corresponding to how many
	   users this user has followed.
	#. A dynamic, deferred ``follower_count`` column, corresponding to how many
	   users have followed this user.
	#. A dynamic, deferred ``forum_count`` column, corresponding to how many
	   forums with this user's ``id`` in their ``user_id`` column exist.
	#. A dynamic, deferred ``message_received_count`` coulumn corresponding to
	   how many messages this user has received.
	#. A dynamic, deferred ``message_received_unread_count`` column corresponding
	   to how many messages this user has received, and hasn't read yet.
	#. A dynamic, deferred ``message_sent_count`` coulumn corresponding to
	   how many messages this user has sent.
	#. A dynamic, deferred ``notification_count`` column corresponding to how
	   many notifications with this user's ``id`` in their ``user_id`` column
	   exist.
	#. A dynamic, deferred ``notification_unread_count`` column corresponding to
	   how many unread notifications this user has.
	#. A dynamic, deferred ``post_count`` column, corresponding to how many
	   posts with this user's ``id`` in their ``user_id`` column exist.
	#. A dynamic, deferred ``thread_count`` column, corresponding to how many
	   thread with this user's ``id`` in their ``user_id`` column exist.
	"""

	__tablename__ = "users"

	registered_by = sqlalchemy.Column(
		sqlalchemy.String(128),
		index=True,
		nullable=True
	)
	external_id = sqlalchemy.Column(
		sqlalchemy.String(64),
		index=True,
		nullable=True
	)
	# ^ Can't make a unique constraint on ``registered_by`` and ``external_id``
	# together, due to the possibility of multiple guest accounts being
	# made from the same IP address.

	avatar_type = sqlalchemy.Column(
		sqlalchemy.String(256),
		default=None,
		nullable=True
	)
	is_banned = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)
	parsed_permissions = sqlalchemy.Column(
		sqlalchemy.JSON,
		nullable=False
	)

	encrypted_private_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=True
	)
	public_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=True
	)
	# Don't set a specific length, so users can use different key sizes

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=True
	)
	status = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)

	followee_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(user_follows.c.follower_id)
		).
		where(sqlalchemy.text("user_follows.follower_id = users.id")).
		scalar_subquery(),
		deferred=True
	)

	follower_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(user_follows.c.followee_id)
		).
		where(sqlalchemy.text("user_follows.followee_id = users.id")).
		scalar_subquery(),
		deferred=True
	)

	forum_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("forums.id"))
		).
		select_from(sqlalchemy.text("forums")).
		where(sqlalchemy.text("forums.user_id = users.id")).
		scalar_subquery(),
		deferred=True
	)

	message_received_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Message.id)
		).
		where(
			Message.receiver_id == sqlalchemy.text("users.id")
		).
		scalar_subquery(),
		deferred=True
	)
	message_received_unread_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Message.id)
		).
		where(
			sqlalchemy.and_(
				sqlalchemy.text("messages.receiver_id = users.id"),
				Message.is_read.is_(False)
			)
		).
		scalar_subquery(),
		deferred=True
	)
	message_sent_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Message.id)
		).
		where(
			sqlalchemy.text("messages.sender_id = users.id")
		).
		scalar_subquery(),
		deferred=True
	)

	notification_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Notification.id)
		).
		where(sqlalchemy.text("notifications.user_id = users.id")).
		scalar_subquery(),
		deferred=True
	)
	notification_unread_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Notification.id)
		).
		where(
			sqlalchemy.and_(
				sqlalchemy.text("notifications.user_id = users.id"),
				Notification.is_read.is_(False)
			)
		).
		scalar_subquery(),
		deferred=True
	)

	post_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("posts.id"))
		).
		select_from(sqlalchemy.text("posts")).
		where(
			sqlalchemy.text("posts.user_id = users.id")
		).
		scalar_subquery(),
		deferred=True
	)

	thread_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("threads.id"))
		).
		select_from(sqlalchemy.text("threads")).
		where(
			sqlalchemy.text("threads.user_id = users.id")
		).
		scalar_subquery(),
		deferred=True
	)

	blockees = sqlalchemy.orm.relationship(
		lambda: User,
		secondary=user_blocks,
		primaryjoin=lambda: User.id == user_blocks.c.blocker_id,
		secondaryjoin=lambda: User.id == user_blocks.c.blockee_id,
		backref="blockers",
		order_by=lambda: sqlalchemy.desc(User.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)
	followees = sqlalchemy.orm.relationship(
		lambda: User,
		secondary=user_follows,
		primaryjoin=lambda: User.id == user_follows.c.follower_id,
		secondaryjoin=lambda: User.id == user_follows.c.followee_id,
		backref="followers",
		order_by=lambda: sqlalchemy.desc(User.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)

	ban = sqlalchemy.orm.relationship(
		UserBan,
		uselist=False,
		backref=sqlalchemy.orm.backref(
			"user",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)
	permissions = sqlalchemy.orm.relationship(
		UserPermissions,
		uselist=False,
		backref=sqlalchemy.orm.backref(
			"user",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)

	class_actions = {
		"delete": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["user_delete"]
		),
		"delete_self": lambda cls, user: True,
		"edit": lambda cls, user: cls.get_class_permission(user, "view"),
		"edit_ban": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["user_edit_ban"]
		),
		"edit_block": lambda cls, user: cls.get_class_permission(user, "view"),
		"edit_follow": lambda cls, user: cls.get_class_permission(user, "view"),
		"edit_group": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["user_edit_groups"]
		),
		"edit_permissions": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["user_edit_permissions"]
		),
		"view": lambda cls, user: True,
		"view_ban": lambda cls, user: cls.get_class_permission(user, "view"),
		"view_groups": lambda cls, user: cls.get_class_permission(user, "view"),
		"view_permissions": lambda cls, user: cls.get_class_permission(user, "view")
	}

	instance_actions = {
		"delete": lambda self, user: (
			self.id == user.id or (
				self.get_instance_permission(user, "view") and
				user.parsed_permissions["user_delete"] and
				user.highest_group.level > self.highest_group.level
			)
		),
		"delete_self": lambda self, user: True,
		"edit": lambda self, user: (
			self.id == user.id or (
				self.get_instance_permission(user, "view") and
				user.parsed_permissions["user_edit"] and
				user.highest_group.level > self.highest_group.level
			)
		),
		"edit_ban": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["user_edit_ban"] and (
				self.id == user.id or
				user.highest_group.level > self.highest_group.level
			)
		),
		"edit_block": lambda self, user: (
			self.id != user.id and
			self.get_instance_permission(user, "view")
		),
		"edit_follow": lambda self, user: (
			self.id != user.id and
			self.get_instance_permission(user, "view")
		),
		"edit_group": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["user_edit_groups"] and
			user.highest_group.level > self.highest_group.level and
			(
				not hasattr(self, "edited_group") or
				user.highest_group.level > self.edited_group.level
			)
		),
		"edit_permissions": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["user_edit_permissions"] and
			user.highest_group.level > self.highest_group.level
		),
		"view": lambda self, user: True,
		"view_ban": lambda self, user: self.get_instance_permission(user, "view"),
		"view_groups": lambda self, user: self.get_instance_permission(user, "view"),
		"view_permissions": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}

	viewable_columns = {
		"id": lambda self, user: True,
		"creation_timestamp": lambda self, user: True,
		"edit_timestamp": lambda self, user: True,
		"edit_count": lambda self, user: True,
		"registered_by": lambda self, user: self.id == user.id,
		"external_id": lambda self, user: self.id == user.id,
		"avatar_type": lambda self, user: True,
		"is_banned": lambda self, user: True,
		"parsed_permissions": lambda self, user: True,
		"encrypted_private_key": lambda self, user: self.id == user.id,
		"public_key": lambda self, user: True,
		"name": lambda self, user: True,
		"status": lambda self, user: True,
		"followee_count": lambda self, user: True,
		"follower_count": lambda self, user: True,
		"forum_count": lambda self, user: True,
		"message_received_count": lambda self, user: self.id == user.id,
		"message_sent_count": lambda self, user: self.id == user.id,
		"notification_count": lambda self, user: self.id == user.id,
		"notification_unread_count": lambda self, user: self.id == user.id,
		"post_count": lambda self, user: True,
		"thread_count": lambda self, user: True
	}

	def write(
		self: User,
		session: sqlalchemy.orm.Session,
		bypass_first_user_check: bool = False
	) -> None:
		r"""If no groups are specified, sets this user's groups to all ``Group``\ s
		where ``default_for`` contains the service this user was registered by,
		or ``'*'``. If the current app is not configured (presumably, no users
		exist), and ``bypass_first_user_check`` is ``False``, ``Group``\ s specified
		in the ``GROUPS_FIRST_USER`` config key will be added as well. If no
		``parsed_permissions`` are specified, they are automatically parsed.
		"""

		if self.parsed_permissions is None:
			self.parsed_permissions = {}

		# Premature session add and flush. We have to access the ID later.
		CDWMixin.write(self, session)
		session.flush()

		if not session.execute(
			sqlalchemy.select(Group).
			where(
				Group.id.in_(
					sqlalchemy.select(user_groups.c.group_id).
					where(user_groups.c.user_id == self.id)
				)
			).
			exists().
			select()
		).scalars().one():
			group_conditions = sqlalchemy.or_(
				Group.default_for.any(
					"*",
					operator=operator.eq
				),
				Group.default_for.any(
					self.registered_by,
					operator=sqlalchemy.sql.expression.ColumnOperators.startswith
				)
			)

			if not flask.current_app.configured and not bypass_first_user_check:
				group_conditions = sqlalchemy.or_(
					group_conditions,
					Group.name.in_(flask.current_app.config["GROUPS_FIRST_USER"])
				)

				flask.current_app.configured = True

			group_ids = session.execute(
				sqlalchemy.select(Group.id).
				where(group_conditions).
				order_by(
					sqlalchemy.desc(Group.level)
				)
			).scalars().all()

			for group_id in group_ids:
				session.execute(
					sqlalchemy.insert(user_groups).
					values(
						user_id=self.id,
						group_id=group_id
					)
				)

		if self.parsed_permissions == {}:
			self.reparse_permissions(session)

	@sqlalchemy.ext.hybrid.hybrid_property
	def has_content(self: User) -> bool:
		"""Returns whether or not this user has any forums, posts or threads."""

		return (
			self.forum_count != 0 or
			self.post_count != 0 or
			self.thread_count != 0 or
			self.message_sent_count != 0
		)

	@has_content.expression
	def has_content(cls: User) -> sqlalchemy.sql.elements.BooleanClauseList:
		"""Returns a ``BooleanClauseList`` that represents whether or not
		this user has any forums, posts or threads.
		"""

		return sqlalchemy.or_(
			cls.forum_count != 0,
			cls.post_count != 0,
			cls.thread_count != 0,
			cls.message_sent_count != 0
		)

	@sqlalchemy.ext.hybrid.hybrid_property
	def highest_group(self: User) -> Group:
		"""Returns the ``Group`` with the highest ``level`` this user has."""

		# Can't add an optional ``session`` here, this is a property
		return sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.select(Group).
			where(
				Group.id.in_(
					sqlalchemy.select(user_groups.c.group_id).
					where(user_groups.c.user_id == self.id)
				)
			).
			order_by(
				sqlalchemy.desc(Group.level)
			).
			limit(1)
		).scalars().one()

	@highest_group.expression
	def highest_group(cls: User) -> sqlalchemy.sql.Select:
		"""Returns a selection query that represents the ``Group`` with the highest
		``level`` this user has.
		"""

		return (
			sqlalchemy.select(Group).
			where(
				Group.id.in_(
					sqlalchemy.select(user_groups.c.group_id).
					where(user_groups.c.user_id == cls.id)
				)
			).
			order_by(
				sqlalchemy.desc(Group.level)
			).
			limit(1)
		)

	@property
	def avatar_filename(self: User) -> typing.Union[None, str]:
		"""Returns the filename for this user's avatar."""

		if self.avatar_type is None:
			return None

		extension = (
			flask.current_app.config["USER_AVATAR_TYPES"][self.avatar_type]
		)

		return f"{self.id}.{extension}"

	@property
	def avatar_location(self: User) -> typing.Union[None, str]:
		"""Returns the full path to this user's avatar."""

		if self.avatar_type is None:
			return None

		storage_location = os.environ.get(
			"AVATAR_STORAGE_LOCATION",
			f"{os.getcwd()}/avatars"
		)

		return f"{storage_location}/{self.avatar_filename}"

	@property
	def avatar(self: User) -> typing.Union[None, bytes]:
		"""Returns this user's avatar, if there is one set."""

		if self.avatar_type is None:
			return None

		with open(
			self.avatar_location,
			"rb"
		) as image:
			return image.read()

	@avatar.setter
	def avatar(
		self: User,
		value: typing.Union[None, bytes]
	) -> None:
		"""Sets this user's avatar. If ``value`` is ``None``,
		the avatar is removed.
		"""

		if value is None:
			if self.avatar_type is not None:
				os.remove(self.avatar_location)

			self.avatar_type = None

			return

		with open(
			self.avatar_location,
			"wb"
		) as avatar:
			avatar.write(value)

	def create_ban(
		self: User,
		expiration_timestamp: datetime.datetime,
		reason: str = None,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Bans this user with the provided ``expiration_timestamp``,
		and optionally a ``reason``.
		"""

		self.is_banned = True

		UserBan.create(
			session if session is not None else sqlalchemy.orm.object_session(self),
			user_id=self.id,
			expiration_timestamp=expiration_timestamp,
			reason=reason
		)

	def remove_ban(self: User) -> None:
		"""Unbans this user."""

		self.is_banned = False

		self.ban.delete()

	def reparse_permissions(
		self: User,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Sets this user's ``parsed_permissions`` column to the combination of:

		#. This user's group permissions, where the group with the highest
		   ``level`` is most important.
		#. This user's permissions.

		Where the lower on the list an item is, the higher priority it has. The
		``session`` argument is only meant to be used during the initial creation
		of this user, but it doesn't have to be.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		result = {}

		group_permission_sets = session.execute(
			sqlalchemy.select(
				GroupPermissions
			).
			where(
				GroupPermissions.group_id.in_(
					sqlalchemy.select(user_groups.c.group_id).
					where(user_groups.c.user_id == self.id)
				)
			).
			order_by(
				sqlalchemy.desc(
					sqlalchemy.select(Group.level).
					where(Group.id == GroupPermissions.group_id).
					scalar_subquery()
				)
			)
		).scalars().all()

		for group_number, group_permissions in enumerate(group_permission_sets):
			if group_permissions is None:
				continue

			for permission_name, permission_value in (
				group_permissions.to_permissions().items()
			):
				# Populates all permissions regardless of whether or not they are set.
				if permission_name in result:
					continue

				if permission_value is not None:
					result[permission_name] = permission_value
				elif len(group_permission_sets) - 1 == group_number:
					result[permission_name] = False

		own_permissions = session.execute(
			sqlalchemy.select(UserPermissions).
			where(UserPermissions.user_id == self.id)
		).scalars().one_or_none()

		if own_permissions is not None:
			for permission_name, permission_value in (
				own_permissions.to_permissions().items()
			):
				if permission_value is None:
					continue

				result[permission_name] = permission_value

		self.parsed_permissions = result
