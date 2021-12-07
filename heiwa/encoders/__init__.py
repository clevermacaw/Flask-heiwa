"""Encoders for the Heiwa API. Currently only supports JSON."""

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
__version__ = "1.3.0"


# Flask does have a custom encoder already that would take care of UUID
# string-ification, but I don't really want to subclass that here. I prefer
# the ISO date(time) formatting over Flask's choice of RFC 822, and overriding
# that feels somewhat hacky. So I'll just use json.JSONEncoder instead.
class JSONEncoder(json.JSONEncoder):
	"""A JSON encoder for the Heiwa API. Adds support for:
		- SQLAlchemy ORM mapped objects. (Converted to dictionaries)
		- Bytes. (Converted to base64)
		- Date(time) objects. (Converted to ISO strings)
		- Enum objects. (Converted to their associated value)
		- UUID objects. (Converted to equivalent strings)
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
		"""Converts:
			- SQLAlchemy ORM mapped object → dictionary, where only the attributes
			`flask.g.user` has access to are included.
			- Date(time) object → ISO formatted string
			- UUID object → UUID string
			- Enum object → Enum object value
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
