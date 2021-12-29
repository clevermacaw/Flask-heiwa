""""Models for categories."""

from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from .. import enums
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
