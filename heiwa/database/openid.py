"""Utility models for OpenID authentication."""

from __future__ import annotations

import sqlalchemy

from . import Base
from .utils import CDWMixin, CreationTimestampMixin, ReprMixin

__all__ = ["OpenIDAuthentication"]


class OpenIDAuthentication(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	Base
):
	"""CSRF / replay attack protection model for OpenID authentication."""

	__tablename__ = "openid_authentication"

	identifier = sqlalchemy.Column(
		sqlalchemy.String(64),
		primary_key=True
	)
	"""The unique identifier for the user who requested to authenticate.
	In general, this will be an IP address hashed using SCrypt.
	"""

	nonce = sqlalchemy.Column(
		sqlalchemy.String(30),
		nullable=False
	)
	"""An OpenID nonce."""

	state = sqlalchemy.Column(
		sqlalchemy.String(30),
		nullable=False
	)
	"""An OpenID state."""
