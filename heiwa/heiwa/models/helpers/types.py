from __future__ import annotations

import typing
import uuid

import sqlalchemy
import sqlalchemy.dialects.postgresql

__all__ = ["UUID"]


class UUID(sqlalchemy.types.TypeDecorator):
	"""A simple, portable UUID TypeDecorator."""

	impl = sqlalchemy.types.TypeEngine
	cache_ok = True

	def load_dialect_impl(
		self: UUID,
		dialect: sqlalchemy.engine.Dialect
	):
		if dialect.name == "postgresql":
			return dialect.type_descriptor(sqlalchemy.dialects.postgresql.UUID())
		else:
			return dialect.type_descriptor(sqlalchemy.types.CHAR(32))

	def process_bind_param(
		self: UUID,
		value: typing.Union[None, str, uuid.UUID],
		dialect: sqlalchemy.engine.Dialect
	) -> typing.Union[None, str]:
		if value is None:
			return value
		elif dialect.name == "postgresql":
			return str(value)
		else:
			if not isinstance(value, uuid.UUID):
				return "%.32x" % uuid.UUID(value).int
			else:
				return "%.32x" % value.int

	def process_result_value(
		self: UUID,
		value: typing.Union[None, str, uuid.UUID],
		dialect: sqlalchemy.engine.Dialect
	) -> typing.Union[None, uuid.UUID]:
		if value is None:
			return value
		else:
			if not isinstance(value, uuid.UUID):
				value = uuid.UUID(value)

			return value
