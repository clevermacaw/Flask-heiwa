from __future__ import annotations

import sqlalchemy

from . import Base
from .helpers import (
	CreationTimestampMixin,
	CDWMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
	UUID
)

__all__ = ["Message"]


class Message(
	CDWMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Message model. Contains:
		- An `id` column from the `IdMixin`.
		- A `creation_timestamp` column from the `CreationTimestampMixin`.
		- `edit_timestamp` and `edit_count` columns from the `EditInfoMixin`.
		- A `sender_id` foreign key column, associating this message with its
		sender, a `User`.
		- A `receiver_id` foreign key column, associating this message with its
		receiver, another `User`.
		- An `is_read` column, signifying whether or not this message has been
		read. `False` by default.
		- A `content` column, containing the message content, which should be
		encrypted with the receiver's public key. Its validity cannot be checked,
		since we don't (and shouldn't) have access to the receiver's private key.
	"""

	__tablename__ = "messages"

	sender_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		)
	)
	receiver_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		)
	)
	# Let's not do multiple receiver IDs, encrypting messages separately with
	# their public keys would only be realistic to do on the server side.
	# And that wouldn't be proper E2EE, which we don't want.

	is_read = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)

	content = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=False
	)
