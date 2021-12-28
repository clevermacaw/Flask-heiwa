"""Models and tables for users."""

from __future__ import annotations

import datetime
import os
import typing

import flask
import sqlalchemy
import sqlalchemy.ext.hybrid
import sqlalchemy.orm

from . import Base
from .group import Group, GroupPermissions
from .utils import (
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
	""":class:`.User` ban model. Can be created manually, but in general, the
	:meth:`.User.create_ban` method will be easier and faster.

	.. seealso::
		:attr:`.User.is_banned`

		:meth:`.User.create_ban()`

		:meth:`.User.remove_ban()`
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
	"""The ID of the :class:`.User` who a ban was issued to."""

	expiration_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		nullable=False
	)
	"""The time a ban expires. When it does, it's not removed immediately, but
	when the :class:`.User` this ban concerns makes any request where they've
	successfully authorized.
	"""

	reason = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)
	"""The reason for a ban."""


class UserPermissions(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	BasePermissionMixin,
	Base
):
	""":class:`.User` permission model. This can be used to set permissions for
	one specific user, instead of only a :class:`.Group`.
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
	"""The ID of the :class:`.User` these permissions belong to."""

class User(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""User model."""

	__tablename__ = "users"

	registered_by = sqlalchemy.Column(
		sqlalchemy.String(128),
		index=True,
		nullable=True
	)
	r"""The service a user was registered by. By default, this can be one of
	2 values: ``guest``, for those who registered using the
	:func:`guest.token <heiwa.views.guest.token>` endpoint, and ``openid``,
	for those who signed up using :mod:`OpenID <heiwa.views.openid>`.
	:class:`.Group`\ s who have this value in their :attr:`.Group.default_for`
	column will automatically be assigned to the user.
	"""

	external_id = sqlalchemy.Column(
		sqlalchemy.String(64),
		index=True,
		nullable=True
	)
	"""The service a user was registered by's identifier for them. For guests,
	this will be a version of their IP address hashed using SCrypt. For users
	registered using OpenID, it will be the ``sub`` key in ``userinfo``.

	.. note::
		Generally, guests will not have permission to create new content
		like threads and posts, but some administrators may allow them to
		do so. In those cases, once their sessions have expired, these
		accounts won't be deleted, but since there is no longer any use
		for it, their IP address stored in this column will be erased.

	.. seealso::
		The OpenID `specification <https://openid.net/specs/openid-conn\
		ect-core-1_0.html#UserInfoResponse>`_ for a successful UserInfo
		response.

		The :attr`.User.has_content` property.
	"""

	# ^ Can't make a unique constraint on ``registered_by`` and ``external_id``
	# together, due to the possibility of multiple guest accounts being
	# made from the same IP address.

	avatar_type = sqlalchemy.Column(
		sqlalchemy.String(256),
		default=None,
		nullable=True
	)
	"""The media type of a user's avatar. If there is no avatar, it will remain
	`None`.

	.. seealso::
		IANA's `list <https://www.iana.org/assignments/media-types/medi\
		a-types.xhtml>`_ of officially recognized media types.

	.. note::
		Media types were formerly recognized as MIME types, and are still
		commonly referred to as such.
	"""

	is_banned = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)
	"""Whether or not a user has been banned. When a ban exists for this user,
	this must be :data:`True` in order for it to be recognized. Defaults to
	:data:`False`.

	.. seealso::

		:class:`.UserBan`

		:meth:`.User.create_ban()`

		:meth:`.User.remove_ban()`
	"""

	parsed_permissions = sqlalchemy.Column(
		sqlalchemy.JSON,
		nullable=False
	)
	"""A user's parsed permissions. This is a combination of the user's groups'
	permissions (where groups with the highest :attr:`.Group.level` attribute
	take precedence), and permissions specific to this user.

	.. seealso::
		:class:`.GroupPermissions`

		:class:`.UserPermissions`

		:meth:`.User.reparse_permissions`

	.. note::
		Parsed permissions don't necessarily need to be stored, but doing
		so will make their usage much faster.
	"""

	encrypted_private_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=True
	)
	r"""A user's RSA private key, encrypted using AES-CBC with a padding size
	of 16. If they choose not to supply one and eneter it manually upon decryption
	of the :class:`.Message`\ s they have received, they can still set a
	:attr:`.User.public_key`.
	"""

	public_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=True
	)
	r"""A user's RSA public key. This must be set for them to be able to receive
	:class:`.Message`\ s, which are always encrypted.

	.. note::
		No set length here, since users can have different key sizes. Though the
		API's upper limit is 4096 bits, which should be enough for effectively
		everyone now.
	"""

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=True
	)
	"""A user's name."""

	status = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)
	"""A user's status. In general, the usage of this should be similar to status
	messages on GitLab and social media.
	"""

	followee_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(user_follows.c.follower_id)
		).
		where(sqlalchemy.text("user_follows.follower_id = users.id")).
		scalar_subquery(),
		deferred=True
	)
	"""The number of users a user is following."""

	follower_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(user_follows.c.followee_id)
		).
		where(sqlalchemy.text("user_follows.followee_id = users.id")).
		scalar_subquery(),
		deferred=True
	)
	"""The number of users following a user."""

	forum_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("forums.id"))
		).
		select_from(sqlalchemy.text("forums")).
		where(sqlalchemy.text("forums.user_id = users.id")).
		scalar_subquery(),
		deferred=True
	)
	r"""The number of :class:`.Forum`\ s a user owns."""

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
	r"""The number of :class:`.Message`\ s a user has received."""

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
	r"""The number of :class:`.Message`\ s a user has received and not yet read."""

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
	r"""The number of :class:`.Message`\ s a user has sent."""

	notification_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(Notification.id)
		).
		where(sqlalchemy.text("notifications.user_id = users.id")).
		scalar_subquery(),
		deferred=True
	)
	r"""The number of :class:`.Notification`\ s a user has."""

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
	r"""The number of unread :class:`.Notification`\ s a user has."""

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
	r"""The number of :class:`.Thread`\ s this user has made."""

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
	r"""The number of :class:`.Post`\ s this user has made."""

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
		"thread_count": lambda self, user: True,
		"post_count": lambda self, user: True
	}

	def write(
		self: User,
		session: sqlalchemy.orm.Session,
		bypass_first_user_check: bool = False
	) -> None:
		r"""If no :class:`.Group`\ s have already been assigned to this user,
		they're set to all groups where the :attr:`.Group.default_for` column
		contains the service this user was registered by or `*`.

		.. seealso::
			:data:`.User.user_groups`

			:attr:`.User.registered_by`

		If the current Flask app has not yet been configured and
		``bypass_first_user_check`` is :data:`False`, all groups specified in the
		``GROUPS_FIRST_USER`` config key will also be added. If no parsed
		permissions have been given, they're automatically parsed.

		.. seealso::
			:attr:`.User.parsed_permissions`

			:attr:`.ConfiguredLockFlask.configured`

			:meth:`.User.reparse_permissions`
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
				Group.default_for.any("*"),  # ``eq`` by default
				# NOTE: Is there any way to properly do ``startswith`` here?
				# This works too, and might even be better in some cases, but
				# I'm not completely happy with it.
				Group.default_for.any(self.registered_by)
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
		r"""Returns whether or not this user owns any forums, has made any threads
		or posts, or sent any messages.

		.. seealso::
			:attr:`.User.forum_count`

			:attr:`.User.thread_count`

			:attr:`.User.post_count`

			:attr:`.User.message_sent_count`
		"""

		return (
			self.forum_count != 0 or
			self.thread_count != 0 or
			self.post_count != 0 or
			self.message_sent_count != 0
		)

	@has_content.expression
	def has_content(cls: User) -> sqlalchemy.sql.elements.BooleanClauseList:
		r"""Returns a list of conditions representing whether or not this user
		owns any forums, has made any threads or posts, or sent any messages.

		.. seealso::
			:attr:`.User.forum_count`

			:attr:`.User.thread_count`

			:attr:`.User.post_count`

			:attr:`.User.message_sent_count`
		"""

		return sqlalchemy.or_(
			cls.forum_count != 0,
			cls.thread_count != 0,
			cls.post_count != 0,
			cls.message_sent_count != 0
		)

	@sqlalchemy.ext.hybrid.hybrid_property
	def highest_group(self: User) -> Group:
		r"""Returns the :class:`.Group` with the highest :attr:`.Group.level`
		this user has.
		"""

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
		r"""Returns a selection query that represents the :class:`.Group` with
		the highest :attr:`.Group.level` this user has.
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
		"""Returns the filename of this user's avatar. If there is no avatar,
		returns :data:`None`.
		"""

		if self.avatar_type is None:
			return None

		extension = (
			flask.current_app.config["USER_AVATAR_TYPES"][self.avatar_type]
		)

		return f"{self.id}.{extension}"

	@property
	def avatar_location(self: User) -> typing.Union[None, str]:
		"""Returns the full path to this user's avatar. If there is no avatar,
		returns :data:`None`.
		"""

		if self.avatar_type is None:
			return None

		storage_location = os.environ.get(
			"AVATAR_STORAGE_LOCATION",
			f"{os.getcwd()}/avatars"
		)

		return f"{storage_location}/{self.avatar_filename}"

	@property
	def avatar(self: User) -> typing.Union[None, bytes]:
		"""Returns this user's avatar in the form of bytes, if there is one.
		Otherwise, :data:`None` is returned.
		"""

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
		"""Sets this user's avatar to the bytes provided in ``value``, if there
		are any. If it's :data:`None`, deletes this user's avatar.
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
		"""Bans this user with the provided ``expiration_timestamp``, and
		optionally a ``reason``.

		.. seealso::
			:class:`.UserBan`
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
		r"""Sets this user's :attr:`.User.parsed_permissions` column to the
		combination of:

			#. This user's :class:`.Group`\ s' permissions, where the group with
			   the highest :attr:`.Group.level` attribute is the most important.
			#. This user's permissions.

		The lower on the list an item is, the higher priority it has.

		.. seealso::
			:class:`.GroupPermissions`

			:class:`.UserPermissions`
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
