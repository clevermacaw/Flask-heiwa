from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .helpers import (
	CDWMixin,
	CreationTimestampMixin,
	IdMixin,
	ReprMixin,
	UUID
)

__all__ = ["Notification"]


class Notification(
	CDWMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	Base
):
	"""Heiwa notification model.
	Uses ..enums.NotificationTypes for storing their types.
	"""

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

	is_read = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)
	type = sqlalchemy.Column(
		sqlalchemy.Enum(enums.NotificationTypes),
		nullable=False
	)

	# Don't include any foreign key here. It would be nice for cascading
	# deletion, but could cause a number of issues in some cases.

	identifier = sqlalchemy.Column(
		UUID,
		nullable=False
	)
