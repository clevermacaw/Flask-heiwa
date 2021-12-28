"""Models and tables for groups."""

from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from . import Base
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

__all__ = [
	"Group",
	"GroupPermissions"
]


class GroupPermissions(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	BasePermissionMixin,
	Base
):
	""":class:`.Group` permission model."""

	__tablename__ = "group_permissions"

	group_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"groups.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :class:`.Group` these permissions belong to."""


class Group(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Group model."""

	__tablename__ = "groups"

	default_for = sqlalchemy.Column(
		sqlalchemy.ARRAY(sqlalchemy.String(128)),
		nullable=False
	)
	r"""The registration services for :class:`.User`\ s who will automatically
	be assigned a group. For example, when a user registers using OpenID, and
	``openid`` is one of the values in this column, the group will be assigned
	to them.

	If `*` is one of the values, all users will be assigned the group.

	.. seealso::
		:attr:`.User.registered_by`

		:meth:`.User.write`
	"""

	level = sqlalchemy.Column(
		sqlalchemy.Integer,
		nullable=False
	)
	"""How important a group's permissions will be when permissions are calculated
	for users or forums. The higher this value is, the more important it will be.

	.. seealso::
		:meth:`.User.reparse_permissions`

		:meth:`.Forum.reparse_permissions`
	"""

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	"""A group's name."""

	description = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=True
	)
	"""A group's description."""

	permissions = sqlalchemy.orm.relationship(
		GroupPermissions,
		uselist=False,
		backref=sqlalchemy.orm.backref(
			"group",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)
	"""A group's permissions. Not required to be set, except for the last group
	whose :attr:`default_for <.Group.default_for>` column contains `*` - meaning
	it's default for all users.
	"""

	class_actions = {
		"create": lambda cls, user: user.parsed_permissions["group_create"],
		"delete": lambda cls, user: user.parsed_permissions["group_delete"],
		"edit": lambda cls, user: user.parsed_permissions["group_edit"],
		"edit_permissions": lambda cls, user: (
			user.parsed_permissions["group_edit_permissions"]
		),
		"view": lambda cls, user: True,
		"view_permissions": lambda cls, user: cls.get_class_permission(user, "view")
	}
	r"""Actions :class:`User`\ s are allowed to perform on all groups, without
	any indication of which group it is.

	``create``:
		Whether or not a user can create groups. Corresponds to the
		``group_create`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``delete``:
		Whether or not a user can delete groups. Corresponds to the
		``group_delete`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit``:
		Whether or not a user can edit groups, excluding their permissions. This
		corresponds to the ``group_edit`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_permissions``:
		Whether or not a user can edit a groups' permissions. This depends on the
		``group_edit_permissions`` in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view``:
		Whether or not a user can view groups. By default, this will always
		be :data:`True`.

	``view_permissions``:
		Whether or not a user can view groups' permissions. By default, this
		will always be :data:`True`.
	"""

	instance_actions = {
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["group_delete"] and
			self.level < user.highest_group.level
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["group_edit"] and
			self.level < user.highest_group.level
		),
		"edit_permissions": lambda self, user: (
			self.get_instance_permission(user, "view") and
			user.parsed_permissions["group_edit_permissions"] and
			self.level < user.highest_group.level
		),
		"view": lambda self, user: True,
		"view_permissions": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given group. Unlike
	:attr:`class_actions <.Group.class_actions>`, this can vary by each group.

	``delete``:
		Whether or not a user can delete this group. This will be :data:`True`
		if the ``group_delete`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>` is :data:`True`,
		and this group's :attr:`level <.Group.level>` is lower than the user's
		highest group's level.

	``edit``:
		Whether or not a user can edit this group, excluding its permissions.
		This will be :data:`True` if the ``group_edit`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>` is :data:`True`,
		and this group's :attr:`level <.Group.level>` is lower than the user's
		highest group's level.

	``edit_permissions``:
		Whether or not a user can edit this group's permissions. This will be
		:data:`True` if the ``group_edit`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>` is :data:`True`,
		and this group's :attr:`level <.Group.level>` is lower than the user's
		highest group's level.

	``view``:
		Whether or not a user can view this group. By default, this will always
		be :data:`True`.

	``view_permissions``:
		Whether or not a user can view this group's permissions. By default, this
		will always be :data:`True`.
	"""
