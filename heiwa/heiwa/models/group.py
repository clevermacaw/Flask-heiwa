from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from . import Base
from .helpers import (
	BasePermissionMixin,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
	UUID
)

__all__ = [
	"Group",
	"GroupPermissions"
]


class GroupPermissions(
	CDWMixin,
	BasePermissionMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Heiwa group permission model."""

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

	def __repr__(self: GroupPermissions) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			group_id=self.group_id
		)


class Group(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Heiwa user group model."""

	__tablename__ = "groups"

	default_for = sqlalchemy.Column(
		sqlalchemy.ARRAY(sqlalchemy.String(128)),
		nullable=False
	)
	level = sqlalchemy.Column(
		sqlalchemy.Integer,
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
