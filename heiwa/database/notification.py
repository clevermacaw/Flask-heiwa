"""Notification models."""

from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .utils import UUID, CDWMixin, CreationTimestampMixin, IdMixin, ReprMixin

__all__ = ["Notification"]


class Notification(
	CDWMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	Base
):
	"""Notification model."""

	__tablename__ = "notifications"

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
	"""The :attr:`id <.User.id>` of the :class:`.User` who received a
	notification.
	"""

	is_read = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)
	"""Whether or not a notification has been read by its receiver."""

	type = sqlalchemy.Column(
		sqlalchemy.Enum(enums.NotificationTypes),
		nullable=False
	)
	"""The type of a notification. These types are defined in
	:class:`NotificationTypes <heiwa.enums.NotificationTypes>`. The
	``NOTIFICATION_TYPES`` attribute of models which can be subjects of
	notifications define which ones relate to them.
	"""

	identifier = sqlalchemy.Column(
		UUID,
		nullable=False
	)
	"""The identifier (usually ``id`` attribute) of the object a notification
	relates to.

	.. note::
		Since this can relate to multiple types of objects whose identifiers
		aren't guaranteed not to collide, this column has not been defined as a
		foreign or unique key.
	"""
