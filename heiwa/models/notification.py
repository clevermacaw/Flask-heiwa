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
	"""Notification model. Contains:
		#. An ``id`` column from the ``IdMixin``.
		#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
		#. A ``user_id`` foreign key column, associating this notification with its
		owner, a ``User``.
		#. An ``is_read`` column, signifying whether or not this notification has
		been read. ``False`` by default.
		#. A ``type`` column, containing what the type of this notification is.
		Uses the ``enums.NotificationTypes`` enums.
		#. An ``identifier`` column, containing the UUID of which resource this
		notification concerns. As, despite the name, UUIDs may not *always* be
		unique across all threads, forums & other resources, and plugins would
		have to add their own foreign keys, it's been deemed unnecessary for it
		to be a foreign key.
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
