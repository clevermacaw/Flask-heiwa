""""Models for categories."""

from __future__ import annotations

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
