"""Encoders for the API. Currently only supports JSON."""

from __future__ import annotations

import base64
import datetime
import enum
import json
import typing
import uuid

import flask
import sqlalchemy
import sqlalchemy.orm

__all__ = ["JSONEncoder"]
__version__ = "1.3.4"


# Flask does have a custom encoder already that would take care of UUID
# string-ification, but I don't really want to subclass that here. I prefer
# the ISO date(time) formatting over Flask's choice of RFC 822, and overriding
# that feels somewhat hacky. So I'll just use json.JSONEncoder instead.
class JSONEncoder(json.JSONEncoder):
	r"""A JSON encoder based on the default ``JSONEncoder``, modified to add a few
	necessary features.

	Conversions:

	.. _JSONEncoder conversion table:

		========================================= ===================================
		From                                      To
		========================================= ===================================
		SQLAlchemy ORM models                     Dictionaries with all columns that
		                                          are allowed, or don't start with
		                                          ``'_'`` if there are no permissions
		                                          set up.
		``bytes``                                 Base64 encoded strings
		``date``\ s, ``time``\ s, ``datetime``\ s ISO-8601 strings
		``Enum``\ s                               Their values
		``UUID``\ s                               Their string equivalents
		========================================= ===================================

	.. note::
		Flask's default JSON encoder converts dates and times using the format
		defined in `RFC 822 <https://tools.ietf.org/html/rfc822>`_. Since it's
		more common and universal, ISO-8601 has been chosen instead.
	"""

	def default(
		self: JSONEncoder,
		o: object
	) -> typing.Union[
		typing.Any,
		str,
		typing.Dict[
			str,
			typing.Any
		]
	]:
		"""Converts various objects to JSONable values, as described in the
		`JSONEncoder conversion table`_.
		"""

		if isinstance(o.__class__, sqlalchemy.orm.DeclarativeMeta):
			if hasattr(o, "get_allowed_columns"):
				return {
					column: getattr(o, column)
					for column in o.get_allowed_columns(flask.g.user)
				}

			return {
				column.key: getattr(o, column.key)
				for column in sqlalchemy.inspect(o).mapper.column_attrs
				if not column.key.startswith("_")
			}

		if isinstance(o, bytes):
			return base64.b64encode(o).decode("utf-8")

		if isinstance(
			o,
			(
				datetime.date,
				datetime.time,
				datetime.datetime
			)
		):
			return o.isoformat()

		if isinstance(o, enum.Enum):
			return o.value

		if isinstance(o, uuid.UUID):
			return str(o)

		return json.JSONEncoder.default(self, o)
