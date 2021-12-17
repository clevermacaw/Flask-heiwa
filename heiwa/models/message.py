from __future__ import annotations

import sqlalchemy

from . import Base
from .helpers import (
	CreationTimestampMixin,
	CDWMixin,
	EditInfoMixin,
	IdMixin,
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
		- An ``id`` column from the ``IdMixin``.
		- A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
		- ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
		- A ``sender_id`` foreign key column, associating this message with its
		sender, a ``User``.
		- A ``receiver_id`` foreign key column, associating this message with its
		receiver, another ``User``.
		- An ``is_read`` column, signifying whether or not this message has been
		read. ``False`` by default.
		- An ``encrypted_session_key`` column, containing this message's randomly
		generated key, which should be encrypted using the receiver's
		``public_key``.
		- A nullable ``tag`` column, containing a string derived from the original
		message used to check for any unauthorized changes to the decrypted
		content, once its receiver attempts to read it. This can, for example,
		be a BCrypt hash.
		- An ``encrypted_content`` column, containing the message content, which
		should be encrypted with the receiver's ``public_key``. Its validity cannot
		be checked, since we don't (and shouldn't) have access to the receiver's
		private key.
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

	encrypted_session_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=False
	)
	tag = sqlalchemy.Column(
		sqlalchemy.String(64),
		nullable=True
	)

	encrypted_content = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=False
	)
