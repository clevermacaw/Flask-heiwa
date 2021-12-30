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
		sqlalchemy.String(262144),
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
	""" TODO """

	instance_actions = {
		"create": lambda self, user: (
			user.parsed_permissions["category_create"]
			if self.forum_id is None
			else self.forum.get_parsed_permissions(user).category_create
		),
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
	""" TODO """
