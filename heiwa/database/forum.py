from __future__ import annotations

import functools
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


@sqlalchemy.orm.declarative_mixin
class ForumPermissionMixin:
	"""A ``Forum`` helper mixin with columns corresponding to all permissions
	relevant in forums, as well as their default values and a ``to_permissions``
	method.
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
	"""A ``Forum`` helper model to store cached parsed permissions for specific
	users. Not meant to be exposed directly.

	Contains:

	#. A ``forum_id`` foreign key column, associating the instance with a
	   ``Forum``.
	#. A ``user_id`` foreign key column, associating the instance with a
	   ``User``.
	#. All columns from the ``ForumPermissionMixin``, but non-nullable.
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


class ForumPermissionsGroup(
	ForumPermissionMixin,
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	r"""A ``Forum`` helper mixin to store permissions for specific ``Group``\ s.

	Contains:

	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A ``forum_id`` foreign key column, associating the instance with a
	   ``Forum``.
	#. A ``group_id`` foreign key column, associating the instance with a
	   ``Group``.
	#. All columns from the ``ForumPemrissionMixin``.
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
		"""Deletes the parent forum's ``ForumParsedPermissions`` for the members of
		this instance's ``group_id``.
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
	r"""A ``Forum`` helper mixin to store permissions for specific ``User``\ s.

	Contains:

	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A ``forum_id`` foreign key column, associating the instance with a
	   ``Forum``.
	#. A ``user_id`` foreign key column, associating the instance with a
	   ``User``.
	#. All columns from the ``ForumPemrissionMixin``.
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
		"""Deletes the parent forum's ``ForumParsedPermissions`` for
		the associated user.
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

	class_actions = {
		"create": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_create"]
		),
		"create_child_forum": lambda cls, user: (
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
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_delete"]
		),
		"edit": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_edit"]
		),
		"edit_permissions_group": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			cls.get_class_permission(user, "edit")
		),
		"edit_permissions_user": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			cls.get_class_permission(user, "edit")
		),
		"edit_subscription": lambda cls, user: (
			cls.get_class_permission(user, "view")
		),
		"merge": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_merge"]
		),
		"move": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["forum_move"]
		),
		"view": lambda cls, user: user.parsed_permissions["forum_view"],
		"view_permissions_group": lambda cls, user: (
			cls.get_class_permission(user, "view")
		),
		"view_permissions_user": lambda cls, user: (
			cls.get_class_permission(user, "view")
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
	"""

	instance_actions = {
		"create_child_forum": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).forum_create
		),
		"create_thread": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).thread_view and
			self.get_parsed_permissions(user).thread_create
		),
		"create_thread_locked": lambda self, user: (
			self.get_instance_permission(user, "create_thread") and
			self.get_parsed_permissions(user).thread_edit_lock_own
		),
		"create_thread_pinned": lambda self, user: (
			self.get_instance_permission(user, "create_thread") and
			self.get_parsed_permissions(user).thread_edit_pin
		),
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).forum_delete
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).forum_edit
		),
		"edit_permissions_group": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_instance_permission(user, "edit")
		),
		"edit_permissions_user": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_instance_permission(user, "edit")
		),
		"edit_subscription": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"merge": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).forum_merge and (
				not hasattr(self, "future_forum") or
				self.future_forum.get_instance_permission(user, "merge")
			)
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.get_parsed_permissions(user).forum_move and (
				not hasattr(self, "future_forum") or
				self.future_forum.get_instance_permission(user, "move")
			)
		),
		"view": lambda self, user: self.get_parsed_permissions(user).forum_view,
		"view_permissions_group": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"view_permissions_user": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given forum. Unlike
	:attr:`class_actions <.Forum.class_actions>`, this can vary by each forum.

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

	@functools.lru_cache()
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

		parsed_permissions = session.execute(
			sqlalchemy.select(ForumParsedPermissions).
			where(
				sqlalchemy.and_(
					ForumParsedPermissions.forum_id == self.id,
					ForumParsedPermissions.user_id == user.id
				)
			)
		).scalars().one_or_none()

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

		existing_parsed_permissions = self.get_parsed_permissions(user)

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
