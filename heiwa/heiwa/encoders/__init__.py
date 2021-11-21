"""Encoders for the Heiwa API. Currently only supports JSON."""

from __future__ import annotations

import typing

import datetime
import enum
import json
import uuid

import flask
import sqlalchemy
import sqlalchemy.orm

__all__ = ["JSONEncoder"]
__version__ = "1.2.1"


# Flask does have a custom encoder already that would take care of UUID
# string-ification, but I don't really want to subclass that here. I prefer
# the ISO date(time) formatting over Flask's choice of RFC 822, and overriding
# that feels somewhat hacky. So I'll just use json.JSONEncoder instead.
class JSONEncoder(json.JSONEncoder):
	"""A JSON encoder for the Heiwa API. Adds support for:
		- SQLAlchemy ORM mapped objects. (Converted to dicts)
		- Date(time) objects. (Converted to ISO strings)
		- UUID objects. (Converted to equivalent strings)
		- Enum objects. (Converted to their associated value)
	"""

	def default(
		self: JSONEncoder,
		object_: object
	) -> typing.Union[
		typing.Any,
		str,
		typing.Dict[str, typing.Any]
	]:
		"""Converts:
			- SQLAlchemy ORM mapped object → dict, where only the attributes
			`flask.g.user` has access to are included.
			- Date(time) object → ISO formatted string
			- UUID object → UUID string
			- Enum object → Enum object value
		"""

		if isinstance(object_.__class__, sqlalchemy.orm.DeclarativeMeta):
			if hasattr(object_, "get_allowed_columns"):
				return {
					column: getattr(object_, column)
					for column in object_.get_allowed_columns(flask.g.user)
				}
			else:
				return {
					column.key: getattr(object_, column.key)
					for column in sqlalchemy.inspect(object_).mapper.column_attrs
					if not column.key.startswith("_")
				}

		if isinstance(
			object_,
			(
				datetime.date,
				datetime.time,
				datetime.datetime
			)
		):  # TODO: PEP 604
			return object_.isoformat()

		if isinstance(object_, uuid.UUID):
			return str(object_)

		if isinstance(object_, enum.Enum):
			return object_.value

		return json.JSONEncoder.default(self, object_)
