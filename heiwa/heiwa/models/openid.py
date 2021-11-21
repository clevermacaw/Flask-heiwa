from __future__ import annotations

import sqlalchemy

from . import Base
from .helpers import (
	CDWMixin,
	CreationTimestampMixin,
	ReprMixin
)

__all__ = ["OpenIDAuthentication"]


class OpenIDAuthentication(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	Base
):
	"""CSRF / replay attack protection for OpenID authentication."""

	__tablename__ = "openid_authentication"

	identifier = sqlalchemy.Column(
		sqlalchemy.String(64),
		primary_key=True
	)

	nonce = sqlalchemy.Column(
		sqlalchemy.String(30),
		nullable=False
	)
	state = sqlalchemy.Column(
		sqlalchemy.String(30),
		nullable=False
	)

	def __repr__(self: OpenIDAuthentication) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			identifier=self.identifier
		)
