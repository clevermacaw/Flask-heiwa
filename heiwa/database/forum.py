"""Forum models and tables."""

from __future__ import annotations

import typing
import uuid

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
r"""A table defining which :class:`.User`\ s have subscribed to which
:class:`.Forum`\ s.
"""


@sqlalchemy.orm.declarative_mixin
class ForumPermissionMixin:
	"""A helper mixin with columns corresponding to all permissions recognized
	only in forums.
	"""

	category_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move = sqlalchemy.Column(
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
		"category_create": None,
		"category_delete": None,
		"category_edit": None,
		"category_view": None,
		"forum_create": None,
		"forum_delete": None,
		"forum_edit": None,
		"forum_merge": None,
		"forum_move": None,
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
	"""The default values of all permissions. In this case, :data:`None`."""

	def to_permissions(self: ForumPermissionMixin) -> typing.Dict[
		str,
		typing.Union[
			None,
			bool
		]
	]:
		"""Transforms the values in this instance to the standard format for
		permissions - a dictionary, where string keys represent permissions,
		and their boolean value represents whether or not they're granted.
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
	r"""A helper model used to store cached forum permissions based on the
	:class:`.ForumPermissionMixin` for :class:`.User`\ s.
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
	"""The :attr:`id <.Forum.id>` of the :class:`.Forum` a set of cached
	permissions relates to.
	"""

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` a set of cached
	permissions relates to.
	"""

	category_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	category_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	category_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	category_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_merge = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	forum_move = sqlalchemy.Column(
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

	DEFAULT_PERMISSIONS = {
		"category_create": False,
		"category_delete": False,
		"category_edit": False,
		"category_view": False,
		"forum_create": False,
		"forum_delete": False,
		"forum_edit": False,
		"forum_merge": False,
		"forum_move": False,
		"forum_view": False,
		"post_create": False,
		"post_delete_own": False,
		"post_delete_any": False,
		"post_edit_own": False,
		"post_edit_any": False,
		"post_edit_vote": False,
		"post_move_own": False,
		"post_move_any": False,
		"post_view": False,
		"thread_create": False,
		"thread_delete_own": False,
		"thread_delete_any": False,
		"thread_edit_own": False,
		"thread_edit_any": False,
		"thread_edit_lock_own": False,
		"thread_edit_lock_any": False,
		"thread_edit_pin": False,
		"thread_edit_vote": False,
		"thread_merge_own": False,
		"thread_merge_any": False,
		"thread_move_own": False,
		"thread_move_any": False,
		"thread_view": False
	}
	"""The default values of all permissions. In this case, :data:`False`."""


class ForumPermissionsGroup(
	ForumPermissionMixin,
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	r"""A helper model used to store :class:`.Forum` permissions for
	:class:`.Group`\ s, based on the :class:`.ForumPermissionMixin`.
	"""

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
	"""The :attr:`id <.Forum.id>` of the :class:`.Forum` a set of permissions
	relates to.
	"""

	group_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"groups.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.Group.id>` of the :class:`.Group` a set of permissions
	relates to.
	"""

	def write(
		self: ForumPermissionsGroup,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Deletes the related :class:`.Forum`'s permissions for all users who
		are part of the related :class:`.Group`.

		:param session: The session to execute the deletion query with.
		"""

		from .user import user_groups

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


class ForumPermissionsUser(
	ForumPermissionMixin,
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	r"""A helper model used to store :class:`.Forum` permissions for
	:class:`.User`\ s, based on the :class:`.ForumPermissionMixin`.
	"""

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
	"""The :attr:`id <.Forum.id>` of the :class:`.Forum` a set of permissions
	relates to.
	"""

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` a set of permissions
	relates to.
	"""

	def write(
		self: ForumPermissionsUser,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Deletes the related :class:`.Forum`'s permissions for the
		:class:`.User` who this set of permissions relates to.

		:param session: The session to execute the deletion query with.
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


class Forum(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Forum model.

	.. note::
		Forums used to have their specific owners in the past, but since they're
		mainly going to be defined by a group of administrators who host the
		service and dealing with owners would cause unnecessary complications,
		they have been removed.
	"""

	__tablename__ = "forums"

	category_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"categories.id",
			ondelete="SET NULL",
			onupdate="CASCADE"
		),
		index=True,
		nullable=True
	)
	"""The :attr:`id <.Category.id>` of the :class:`.Category` a forum belongs
	in. If :data:`None`, the forum doesn't belong in any category and will
	generally be shown at the bottom in frontend programs.

	When / if the category is deleted, the forum will not be deleted, but
	instead, this column will become :data:`None`.
	"""

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
	"""The :attr:`id <.Forum.id>` of the forum another forum is a child of.

	.. seealso::
		:attr:`.Forum.child_forums`

		:meth:`.Forum.get_child_level`
	"""

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	"""A forum's name."""

	description = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)
	"""A forum's description."""

	order = sqlalchemy.Column(
		sqlalchemy.Integer,
		default=0,
		nullable=False
	)
	"""The order a forum will be displayed in by default. The higher it is, the
	higher the forum will be.
	"""

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(forum_subscribers.c.forum_id)
		).
		where(forum_subscribers.c.forum_id == sqlalchemy.text("forums.id")).
		scalar_subquery()
	)
	r"""The amount of :class:`.User`\ s subscribed to a forum."""

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
	r"""The amount of :class:`.Thread`\ s in a forum

	.. seealso::
		:data:`.forum_subscribers`
	"""

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
	"""The time the latest :class:`.Thread` in a forum was made. If there haven't
	been any threads so far, this will be :data:`None`.
	"""

	category = sqlalchemy.orm.relationship(
		"Category",
		passive_deletes="all",
		foreign_keys=[category_id],
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
	"""A forum's parsed permission cache.

	.. seealso::
		:meth:`.Forum.reparse_permissions`

		:class:`.ForumParsedPermissions`
	"""

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
	"""Forum permissions for groups.

	.. seealso::
		:class:`.ForumPermissionsGroup`
	"""

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
	"""Forum permissions for users.

	.. seealso::
		:class:`.ForumPermissionsUser`
	"""

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
	"""A forum's children. Unless those child forums have their own specific
	permissions set, they inherit their parent's.

	.. seealso::
		:attr:`.Forum.parent_forum_id`

		:meth:`.Forum.get_child_level`
	"""

	def _static_action_create_thread(user) -> bool:
		r"""Checks whether or not the ``user`` is allowed to create
		:class:`.Thread`\ s without knowledge of which forum it'll be done in.

		:param user: The user.

		:returns: The result.
		"""

		from .thread import Thread

		return (
			Forum.static_actions["view"](user) and
			Thread.static_actions["create"](user)
		)

	def _static_action_create_thread_locked(user) -> bool:
		r"""Checks whether or not the ``user`` is allowed to create locked
		:class:`.Thread`\ s without knowledge of which forum it'll be done in.

		:param user: The user.

		:returns: The result.
		"""

		from .thread import Thread

		return (
			Forum.static_actions["view"](user) and
			Thread.static_actions["edit_lock"](user)
		)

	def _static_action_create_thread_pinned(user) -> bool:
		r"""Checks whether or not the ``user`` is allowed to create pinned
		:class:`.Thread`\ s without knowledge of which forum it'll be done in.

		:param user: The user.

		:returns: The result.
		"""

		from .thread import Thread

		return (
			Forum.static_actions["view"](user) and
			Thread.static_actions["edit_pin"](user)
		)

	def _static_action_move_thread_to(user) -> bool:
		r"""Checks whether or not the ``user`` is allowed to create move
		:class:`.Thread`\s to forums, without knowledge of which forum it'll
		be.

		:param user: The user.

		:returns: The result.
		"""

		from .thread import Thread

		return (
			Forum.static_actions["view"](user) and
			Thread.static_actions["move"](user)
		)

	static_actions = {
		"create": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_create"]
		),
		"create_child_forum": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_create"]
		),
		"create_thread": _static_action_create_thread,
		"create_thread_locked": _static_action_create_thread_locked,
		"create_thread_pinned": _static_action_create_thread_pinned,
		"delete": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_delete"]
		),
		"edit": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_edit"]
		),
		"edit_permissions_group": lambda user: (
			Forum.static_actions["view"](user) and
			Forum.static_actions["edit"](user)
		),
		"edit_permissions_user": lambda user: (
			Forum.static_actions["view"](user) and
			Forum.static_actions["edit"](user)
		),
		"edit_subscription": lambda user: (
			Forum.static_actions["view"](user)
		),
		"merge": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_merge"]
		),
		"move": lambda user: (
			Forum.static_actions["view"](user) and
			user.parsed_permissions["forum_move"]
		),
		"move_thread_to": _static_action_move_thread_to,
		"view": lambda user: user.parsed_permissions["forum_view"],
		"view_permissions_group": lambda user: (
			Forum.static_actions["view"](user)
		),
		"view_permissions_user": lambda user: (
			Forum.static_actions["view"](user)
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on all threads, without
	any indication of which thread it is.

	``create``:
		Whether or not a user can create forums. This depends on the user being
		allowed to view forums, as well as the ``forum_create`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_child_forum``:
		Whether or not a user can create child forums within other forums. This
		depends on the user being allowed to view forums, as well as the
		``forum_create`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_thread``:
		Whether or not a user can create threads within forums. This depends on
		the user being allowed to view forums, as well as the ``thread_view``
		and ``thread_create`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_thread_locked``:
		Whether or not a user can create locked threads within forums. This
		depends on the user being allowed to create threads, as well as the
		``thread_edit_lock_own`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_thread_pinned``:
		Whether or not a user can create locked threads within forums. This
		depends on the user being allowed to create threads, as well as the
		``thread_edit_pin`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``delete``:
		Whether or not a user can delete forums. This depends on the user being
		allowed to view forums, as well as the ``forum_delete`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit``:
		Whether or not a user can edit forums. This depends on the user being
		allowed to view forums, as well as the ``forum_edit`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_permissions_group``:
		Whether or not a user can edit forums' permission for groups. As long as
		the user is allowed to edit and view forums, this will always be
		:data:`True` by default.

	``edit_permissions_user``:
		Whether or not a user can edit forums' permission for users. As long as
		the user is allowed to edit and view forums, this will always be
		:data:`True` by default.

	``edit_subscription``:
		Whether or not a user is allowed to subscribe to / unsubscribe from
		forums. As long as they are allowed to view them, this will always
		be :data:`True` by default.

	``merge``:
		Whether or not a user is allowed to merge forums with other forums. This
		depends on the ``forum_merge`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``move``:
		Whether or not a user is allowed to move forums to other forums, making
		them child forums. This depends on the user being allowed to view forums,
		as well as the ``forum_move`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``move_thread_to``:
		Whether or not a user is allowed to move threads to forums, This depends
		on the user being allowed to view both threads and forums, as well as
		either the ``thread_move_own`` or ``thread_move_any`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view``:
		Whether or not a user is allowed to view forums. This depends on the
		``forum_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view_permissions_group``:
		Whether or not a user is allowed to view groups' permissions for forums.
		As long as the user is allowed to view forums, always :data:`True` by
		default.

	``view_permissions_user``:
		Whether or not a user is allowed to view users' permissions for forums.
		As long as the user is allowed to view forums, always :data:`True` by
		default.

	.. seealso::
		:attr:`.Forum.instance_actions`

		:attr:`.Forum.action_queries`
	"""

	def _instance_action_create_thread(self: Forum, user) -> bool:
		"""Checks whether or not ``user`` is allowed to create a :class:`.Thread`
		in this forum.

		:param user: The user, a :class:`.User`.

		:returns: The result of the check.
		"""

		parsed_permissions = self.get_parsed_permissions(user)

		return (
			self.instance_actions["view"](self, user) and
			parsed_permissions.thread_view and
			parsed_permissions.thread_create
		)

	def _instance_action_create_thread_locked(self: Forum, user) -> bool:
		"""Checks whether or not ``user`` is allowed to create a locked
		:class:`.Thread` in this forum.

		:param user: The user, a :class:`.User`.

		:returns: The result of the check.

		.. seealso::
			:attr:`.Thread.is_locked`
		"""

		parsed_permissions = self.get_parsed_permissions(user)

		return (
			self.instance_actions["create_thread"](self, user) and (
				parsed_permissions.thread_edit_lock_own or
				parsed_permissions.thread_edit_lock_any
			)
		)

	instance_actions = {
		"create_child_forum": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.get_parsed_permissions(user).forum_create
		),
		"create_thread": _instance_action_create_thread,
		"create_thread_locked": _instance_action_create_thread_locked,
		"create_thread_pinned": lambda self, user: (
			self.instance_actions["create_thread"](self, user) and
			self.get_parsed_permissions(user).thread_edit_pin
		),
		"delete": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.get_parsed_permissions(user).forum_delete
		),
		"edit": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.get_parsed_permissions(user).forum_edit
		),
		"edit_permissions_group": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.instance_actions["edit"](self, user)
		),
		"edit_permissions_user": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.instance_actions["edit"](self, user)
		),
		"edit_subscription": lambda self, user: (
			self.instance_actions["view"](self, user)
		),
		"merge": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.get_parsed_permissions(user).forum_merge and (
				not hasattr(self, "future_forum") or
				self.future_forum.instance_actions["merge"](self, user)
			)
		),
		"move": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.get_parsed_permissions(user).forum_move and (
				not hasattr(self, "future_forum") or
				self.future_forum.instance_actions["move"](self, user)
			)
		),
		"move_thread_to": lambda self, user: (
			self.instance_actions["create_thread"](self, user)
		),
		"view": lambda self, user: self.get_parsed_permissions(user).forum_view,
		"view_permissions_group": lambda self, user: (
			self.instance_actions["view"](self, user)
		),
		"view_permissions_user": lambda self, user: (
			self.instance_actions["view"](self, user)
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given forum. Unlike
	:attr:`static_actions <.Forum.static_actions>`, this can vary by each forum.

	``create_child_forum``:
		Whether or not a user can create child forums within this forum. This
		depends on the user being allowed to view it, as well as the
		``forum_create`` value in this forum's permissions for that user.

	``create_thread``:
		Whether or not a user can create threads within this forum. This depends
		on the user being allowed to view it, as well as the ``thread_view`` and
		``thread_create`` values in this forum's permissions for that user.

	``create_thread_locked``:
		Whether or not a user can create locked threads within this forum. This
		depends on them being allowed to create threads, as well as the
		``thread_edit_lock_own`` value in this forum's permissions for that user.

	``create_thread_pinned``:
		Whether or not a user can create pinned threads within this forum. This
		depends on them being allowed to create threads, as well as the
		``thread_edit_pin`` value in this forum's permissions for that user.

	``delete``:
		Whether or not a user is allowed to delete this forum. This depends on
		them being allowed to view it, as well as the ``forum_delete`` value
		in this forum's permissions for that user.

	``edit``:
		Whether or not a user is allowed to edit this forum. This depends on them
		being allowed to view it, as well as the ``forum_edit`` value in this
		forum's permissions for that user.

	``edit_permissions_group``:
		Whether or not a user is allowed to edit groups' permissions for this
		user. As long as they are allowed to edit it, always :data:`True` by
		default.

	``edit_permissions_user``:
		Whether or not a user is allowed to edit users' permissions for this
		user. As long as they are allowed to edit it, always :data:`True` by
		default.

	``edit_subscription``:
		Whether or not a user is allowed to subscribe to / unsubscribe from this
		forum. As long as they are allowed to view it, always :data:`True` by
		default.

	``merge``:
		Whether or not a user is allowed to merge this forum with other forums.
		This depends on them being able to view it, as well as the ``forum_merge``
		value in the user's permissions for this forum. If the ``future_forum``
		attribute is set, the same conditions must also apply to it.

	``move``:
		Whether or not a user is allowed to move this forum to another forum,
		making it its child forum. This depends on them being able to view it,
		as well as the ``forum_move`` value in the user's permissions for this
		forum. If the ``future_forum`` attribute is set, the same conditions
		must also apply to it.

	``move_thread_to``:
		Whether or not a user is allowed to move :class:`.Thread`\ s to this
		forum. This depends on the user being allowed to create threads in it.

	``view``:
		Whether or not a user is allowed to view this forum. This depends on the
		``forum_view`` value in this forum's permissions for that user.

	``view_permissions_group``:
		Whether or not a user is allowed to view groups' permissions for this
		forum. As long as they are allowed to view the forum itself, this will
		always be :data:`True` by default.

	``view_permissions_user``:
		Whether or not a user is allowed to view users' permissions for this
		forum. As long as they are allowed to view the forum itself, this will
		always be :data:`True` by default.

	.. seealso::
		:attr:`.Forum.static_actions`

		:attr:`.Forum.action_queries`
	"""

	action_queries = {
		"create_child_forum": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.forum_create.is_(True)
		),
		"create_thread": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.thread_view.is_(True),
			ForumParsedPermissions.thread_create.is_(True)
		),
		"create_thread_locked": lambda user: sqlalchemy.and_(
			Forum.action_queries["create_thread"](user),
			sqlalchemy.or_(
				ForumParsedPermissions.thread_edit_lock_own.is_(True),
				ForumParsedPermissions.thread_edit_lock_any.is_(True)
			)
		),
		"create_thread_pinned": lambda user: sqlalchemy.and_(
			Forum.action_queries["create_thread"](user),
			ForumParsedPermissions.thread_edit_pin.is_(True)
		),
		"delete": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.forum_delete
		),
		"edit": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.forum_edit
		),
		"edit_permissions_group": lambda user: Forum.action_queries["edit"](user),
		"edit_permissions_user": lambda user: Forum.action_queries["edit"](user),
		"edit_subscription": lambda user: Forum.action_queries["view"](user),
		"merge": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.forum_merge.is_(True)
		),
		"move": lambda user: sqlalchemy.and_(
			Forum.action_queries["view"](user),
			ForumParsedPermissions.forum_move.is_(True)
		),
		"move_thread_to": lambda user: Forum.action_queries["create_thread"](user),
		"view": lambda user: ForumParsedPermissions.forum_view.is_(True),
		"view_permissions_group": lambda user: Forum.action_queries["view"](user),
		"view_permissions_user": lambda user: Forum.action_queries["view"](user)
	}
	"""Actions and their required permissions translated to be evaluable within
	SQL queries. Unless arbitrary additional attributes come into play, these
	permissions will generally be the same as
	:attr:`instance_actions <.Forum.instance_actions>`.

	.. seealso::
		:attr:`.Forum.instance_actions`

		:attr:`.Forum.static_actions`
	"""

	def delete(
		self: Forum,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		r"""Deletes all :class:`.Notification`\ s associated with this forum, as
		well as the forum itself. If the ``session`` argument is :data:`None`,
		it's set to this object's session.
		"""

		from .notification import Notification
		from .post import Post
		from .thread import Thread

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		thread_ids = session.execute(
			sqlalchemy.select(Thread.id).
			where(Thread.forum_id == self.id)
		).scalars().all()

		session.execute(
			sqlalchemy.delete(Notification).
			where(
				sqlalchemy.or_(
					sqlalchemy.and_(
						Notification.type.in_(Thread.NOTIFICATION_TYPES),
						Notification.identifier.in_(thread_ids)
					),
					sqlalchemy.and_(
						Notification.type.in_(Post.NOTIFICATION_TYPES),
						Notification.identifier.in_(
							sqlalchemy.select(Post.id).
							where(Post.thread_id.in_(thread_ids))
						)
					),
					sqlalchemy.and_(
						Notification.type.in_(self.NOTIFICATION_TYPES),
						Notification.identifier == self.id
					)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self, session)

	@classmethod
	def get(
		cls: Forum,
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

		Since forums' permissions may not be parsed, this will always emit
		additional queries to check.

		:param user: The user whose permissions should be evaluated.
		:param session: The SQLAlchemy session to execute additional queries with.
		:param additional_actions: Additional actions that a user must be able to
			perform on forums, other than the default ``view`` action.
		:param conditions: Any additional conditions. :data:`True` by default,
			meaning there are no conditions.
		:param order_by: An expression to order by.
		:param limit: A limit.
		:param offset: An offset.
		:param ids_only: Whether or not to only return a query for IDs.

		:returns: The query.
		"""

		inner_conditions = (
			sqlalchemy.and_(
				ForumParsedPermissions.forum_id == cls.id,
				ForumParsedPermissions.user_id == user.id
			)
		)

		first_iteration = True
		forum_without_parsed_permissions_exists = False

		while (first_iteration or forum_without_parsed_permissions_exists):
			first_iteration = False

			rows = session.execute(
				sqlalchemy.select(
					cls.id,
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
					# Just in case
					sqlalchemy.select(cls if not ids_only else cls.id).
					where(False)
				)

			forum_ids = []
			unparsed_permission_forum_ids = []

			for row in rows:
				forum_id, parsed_permissions_exist = row

				if not parsed_permissions_exist:
					forum_without_parsed_permissions_exists = True
					unparsed_permission_forum_ids.append(forum_id)

					continue

				forum_ids.append(forum_id)

			if forum_without_parsed_permissions_exists:
				for forum in (
					session.execute(
						sqlalchemy.select(cls).
						where(cls.id.in_(unparsed_permission_forum_ids))
					).scalars()
				):
					forum.reparse_permissions(user)

				session.commit()

			if ids_only:
				return sqlalchemy.select(forum_ids)

			return (
				sqlalchemy.select(cls).
				where(cls.id.in_(forum_ids)).
				order_by(order_by)
			)

	def _get_child_forum_and_own_ids(
		self: Forum,
		session: sqlalchemy.orm.Session,
		current_id: typing.Union[
			None,
			uuid.UUID
		] = None
	) -> typing.List[uuid.UUID]:
		"""Returns a list of this forum's :attr:`id <.Forum.id>`, combined with
		its child forums'. If the ``session`` argument is :data:`None`, it's set
		to this object's session.

		.. seealso::
			:attr:`.Forum.child_forums`
		"""

		if current_id is None:
			current_id = self.id

		ids = [current_id]

		for child_forum_id in session.execute(
			sqlalchemy.select(Forum.id).
			where(Forum.parent_forum_id == current_id)
		).scalars().all():
			ids += self._get_child_forum_ids(
				session,
				child_forum_id
			)

		return ids

	def delete_all_parsed_permissions(
		self: Forum,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Deletes all instances of :class:`.ForumParsedPermissions` associated
		with this forum, as well as its children. If the ``session`` argument is
		:data:`None`, it's set to this object's session.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		session.execute(
			sqlalchemy.delete(ForumParsedPermissions).
			where(
				ForumParsedPermissions.forum_id.in_(
					self._get_child_forum_and_own_ids(session)
				)
			)
		)

	def _parse_child_level(
		self: Forum,
		session: sqlalchemy.orm.Session,
		child_level: int = 0,
		current_id: typing.Union[
			None,
			uuid.UUID
		] = None
	) -> int:
		"""Returns how many levels 'deep' this forum is. For example, if there is
		no parent forum set, it's ``0``. If it's the child of a forum with no
		parent of it sown, it's ``1``.

		.. seealso::
			:meth:`.Forum.get_child_level`
		"""

		if current_id is None:
			current_id = self.id

		parent_forum_id = session.execute(
			sqlalchemy.select(Forum.parent_forum_id).
			where(Forum.id == current_id)
		).scalars().one_or_none()

		if parent_forum_id is not None:
			child_level += 1

			return self._parse_child_level(
				session,
				child_level,
				parent_forum_id
			)

		return child_level

	def get_child_level(
		self: Forum,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Returns how many levels 'deep' this forum is. For example, if there is
		no parent forum set, it's ``0``. If it's the child of a forum with no
		parent of it sown, it's ``1``. If the ``session`` argument is :data:`None`,
		it's set to this object's session.

		This value is primarily used to limit forum creation through the API. If
		the child level limit is, for example, a fairly liberal ``25``, forums
		more than 25 levels deep will not be created.

		.. note::
			Ideally, there would be no limit at all, but calculating inherited
			permissions has to be done through a recursive function to some
			extent. Recursion, at least in CPython, currently has inherent limits.

		.. seealso::
			:meth:`.Forum._parse_child_level`
		"""

		if self.parent_forum_id is None:
			return 0

		return self._parse_child_level(
			session if session is not None else sqlalchemy.orm.object_session(self),
			1,
			self.parent_forum_id
		)

	def get_parsed_permissions(
		self: Forum,
		user,
		auto_parse: bool = True,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> typing.Union[
		None,
		ForumParsedPermissions
	]:
		"""Returns the cached parsed permissions this forum has for the given
		``user``. If ``auto_parse`` is :data:`True` and the permissions have not
		yet been parsed, they are parsed automatically. If the ``session``
		argument is :data:`None`, it's set to this object's session.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		parsed_permissions = session.get(
			ForumParsedPermissions,
			(
				self.id,
				user.id
			)
		)  # Don't query twice for the same thing

		if parsed_permissions is None and auto_parse:
			self.reparse_permissions(user)

		return parsed_permissions

	def get_subscriber_ids(
		self: Forum,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> typing.List[uuid.UUID]:
		r"""Returns this forum's subscribers' :attr:`id <.User.id>`\ s. If the
		``session`` argument is :data:`None`, it's set to this object's session.

		.. seealso::
			:data:`.forum_subscribers`
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		return session.execute(
			sqlalchemy.select(forum_subscribers.c.user_id).
			where(forum_subscribers.c.forum_id == self.id)
		).scalars().all()

	def _get_permissions_group(
		self: Forum,
		group_id: uuid.UUID,
		session: sqlalchemy.orm.Session,
		forum_id: typing.Union[
			None,
			uuid.UUID
		] = None
	) -> typing.Dict[str, bool]:
		"""Returns this forum's, as well as the parent forums' permissions for
		the :class:`.Group` with the given ``group_id``. If the ``forum_id``
		argument is :data:`None`, the current forum is considered to be ``self``.
		Otherwise, the :attr:`id <.Forum.id>` supplied within the argument is
		considered to be that of the current forum's.

		This forum's permissions take precedence. For unset permissions, the
		parent closest to this forum takes precedence.

		.. note::
			In the past, this function used to retrieve the parent forum object,
			and called this function on it. This does improve readability, but
			introduces a considerable amount of unnecessary data being used.

		.. seealso::
			:class:`.ForumPermissionsGroup`
		"""

		if forum_id is None:
			forum_id = self.id
			parent_forum_id = self.parent_forum_id
		else:
			parent_forum_id = session.execute(
				sqlalchemy.select(Forum.parent_forum_id).
				where(Forum.id == forum_id)
			).scalars().one_or_none()

		parsed_group_permissions = {}

		own_group_permissions = session.execute(
			sqlalchemy.select(ForumPermissionsGroup).
			where(
				sqlalchemy.and_(
					ForumPermissionsGroup.group_id == group_id,
					ForumPermissionsGroup.forum_id == forum_id
				)
			)
		).scalars().one_or_none()

		if own_group_permissions is not None:
			parsed_group_permissions = own_group_permissions.to_permissions()

		if parent_forum_id is not None:
			for permission_name, permission_value in self._get_permissions_group(
				group_id,
				session,
				parent_forum_id
			).items():
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
		session: sqlalchemy.orm.Session,
		forum_id: typing.Union[
			None,
			uuid.UUID
		] = None
	) -> typing.Dict[str, bool]:
		"""Returns this forum's, as well as the parent forums' permissions for
		the :class:`.User` with the given ``user_id``. If the ``forum_id``
		argument is :data:`None`, the current forum is considered to be ``self``.
		Otherwise, the :attr:`id <.Forum.id>` supplied within the argument is
		considered to be that of the current forum's.

		This forum's permissions take precedence. For unset permissions, the
		parent closest to this forum takes precedence.

		.. note::
			In the past, this function used to retrieve the parent forum object,
			and called this function on it. This does improve readability, but
			introduces a considerable amount of unnecessary data being used.

		.. seealso::
			:class:`.ForumPermissionsUser`
		"""

		if forum_id is None:
			forum_id = self.id
			parent_forum_id = self.parent_forum_id
		else:
			parent_forum_id = session.execute(
				sqlalchemy.select(Forum.parent_forum_id).
				where(Forum.id == forum_id)
			).scalars().one_or_none()

		parsed_user_permissions = {}

		own_user_permissions = session.execute(
			sqlalchemy.select(ForumPermissionsUser).
			where(
				sqlalchemy.and_(
					ForumPermissionsUser.user_id == user_id,
					ForumPermissionsUser.forum_id == forum_id
				)
			)
		).scalars().one_or_none()

		if own_user_permissions is not None:
			parsed_user_permissions = own_user_permissions.to_permissions()

		if parent_forum_id is not None:
			for permission_name, permission_value in self._get_permissions_user(
				user_id,
				session,
				parent_forum_id
			).items():
				if (
					permission_value is None or
					parsed_user_permissions.get(permission_name) is not None
				):
					continue

				parsed_user_permissions[permission_name] = permission_value

		return parsed_user_permissions

	def reparse_permissions(
		self: Forum,
		user,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> ForumParsedPermissions:
		"""Sets the given ``user``'s :class:`.ForumParsedPermissions` for the
		current forum to:

		#. The user's :attr:`parsed_permissions <.User.parsed_permissions>`.
		#. Any permissions associated with this forum defined for the groups the
		   user is a part of.
		#. Any permissions associated with this forum defined for the user.

		In that order. The lower on the list a set of permissions is, the more
		important it is and overrides values that existed in the previous set.

		If the ``session`` argument is :data:`None`, it's set to this object's
		session.

		.. seealso::
			:meth:`.Forum._get_permissions_group`

			:class:`.ForumPermissionsGroup`

			:meth:`.Forum._get_permissions_user`

			:class:`.ForumPermissionsUser`
		"""

		from .group import Group
		from .user import user_groups

		if session is None:
			session = sqlalchemy.orm.object_session(self)

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

		existing_parsed_permissions = self.get_parsed_permissions(
			user,
			auto_parse=False
		)

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

		return existing_parsed_permissions
