"""Message models."""

from __future__ import annotations

import sqlalchemy

from . import Base
from .utils import (
	UUID,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	ReprMixin
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
	"""Message model."""

	__tablename__ = "messages"

	sender_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		)
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` who sent a message."""

	receiver_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		)
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` who received a message.

	.. note::
		Since allowing for multiple receivers of a single message would mean
		encrypting the message separately for each user and complicate things
		a lot, it has not been implemented. However, sending the same message
		to multiple people at once is still possible.
	"""

	is_read = sqlalchemy.Column(
		sqlalchemy.Boolean,
		default=False,
		nullable=False
	)
	"""Whether or not a message has been read."""

	encrypted_session_key = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=False
	)
	"""The AES key used to encrypt a message, encrypted using the receiver's
	:attr:`public_key <.User.public_key>`.
	"""

	tag = sqlalchemy.Column(
		sqlalchemy.String(64),
		nullable=True
	)
	"""A string of characters defined from the decrypted version of a message,
	used to check whether or not the encrypted content has been modified. This
	will usually be some form of hash, like SHA256 or SCrypt for extra (possibly
	unnecessary) security.
	"""

	encrypted_content = sqlalchemy.Column(
		sqlalchemy.LargeBinary,
		nullable=False
	)
	"""A message's content, encrypted using AES with its session key. By default,
	the maximum size of this value will be 262160 bytes - up to 65536 4-byte
	unicode characters, or about 262144 1-byte characters - those generally
	compatible with ASCII.
	"""
