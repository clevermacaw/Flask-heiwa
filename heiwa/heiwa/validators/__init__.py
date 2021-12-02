"""Validators for requests sent to the API. Uses Cerberus, and currently only
supports JSON.
"""

from __future__ import annotations

import collections
import datetime
import functools
import re
import typing
import uuid

import cerberus
import flask
import validators

from .. import exceptions

__all__ = ["APIValidator", "validate_json"]
__version__ = "1.8.4"


class APIValidator(cerberus.Validator):
	"""Cerberus validator for the API. Adds methods related to UUIDs,
	ISO-formatted datetime, URLs, regex and the `makes_required` rule.
	"""

	def _check_with_is_valid_regex(
		self: APIValidator,
		field: str,
		value: str
	) -> None:
		"""Checks whether or not `value` is a valid regular expression."""

		try:
			re.compile(value)
		except re.error:
			self._error(field, "must be a valid regular expression")

	def _check_with_is_public_url(
		self: APIValidator,
		field: str,
		value: str
	) -> None:
		"""Checks that this URL is valid, and corresponds to a public resource."""

		try:
			validators.url(value, public=True)
		except validators.ValidationFailure:
			self._error(field, "must be a valid public URL")

	def _check_with_has_no_duplicates(
		self: APIValidator,
		field: str,
		value: typing.List[typing.Any]
	) -> None:
		"""Checks that the given list contains no duplicate items."""

		if len(value) != len(set(value)):
			self._error(field, "must contain no duplicate items")

	def _normalize_coerce_convert_to_uuid(
		self: APIValidator,
		value: str
	) -> uuid.UUID:
		"""Converts a given string into a UUID."""

		return uuid.UUID(value)

	def _normalize_coerce_convert_to_datetime(
		self: APIValidator,
		value: str
	) -> datetime.datetime:
		"""Converts a given ISO formatted datetime string to a datetime.
		Must have a timezone in order to work properly with the rest of the API.
		"""

		result = datetime.datetime.fromisoformat(value)

		if result.tzinfo is None:
			raise ValueError("must have a timezone")

		return result

	def _validate_makes_required(
		self: APIValidator,
		makes_required: typing.Dict[
			str,
			typing.Union[
				typing.Iterable[typing.Any],
				typing.Any
			]
		],
		field: str,
		value: typing.Any
	) -> None:
		"""For every key in `makes_required`:
			- If the key's value is an iterable, and the corresponding field's
			value equals one of them, the field is treated as if it was required.
			- If the key's value is not an iterable, and the corresponding field
			equals it, it's treated as if it was required.
		The rule's arguments are validated against this schema:
		{
			'type': 'dict',
			'keysrules': {
				'type': 'string'
			}
		}
		"""

		for required_field, required_value in makes_required.items():
			if (
				(
					isinstance(required_value, typing.Iterable) and
					value not in required_value
				) or
				required_value != value
			):
				continue

			if self._lookup_field(required_field) == (None, None):
				self._error(required_field, f"required when {field} equals {value}")

	types_mapping = cerberus.Validator.types_mapping.copy()
	types_mapping["uuid"] = cerberus.TypeDefinition("uuid", (uuid.UUID,), ())


def validate_json(
	schema: typing.Dict[
		str,
		typing.Union[
			str,
			typing.Dict
		]
	],
	*args,
	**kwargs
) -> collections.abc.Callable[
	collections.abc.Callable[
		typing.Any,
		typing.Any
	],
	collections.abc.Callable[
		typing.Any,
		typing.Any
	]
]:
	"""Checks JSON data sent in the `flask.request` against a Cerberus schema.
	If there is no data at all, `exceptions.APIJSONMissing` will be raised.
	If there is data, but it's not a dictionary as `cerberus.Validator` requires,
	`exceptions.APIJSONInvalid` will be raised will no additional details.
	If the data is invalid as per the schema, `exceptions.APIJSONInvalid` will
	be raised with the validation errors given in its details.
	"""

	def wrapper(
		function: collections.abc.Callable[
			typing.Any,
			typing.Any
		]
	) -> collections.abc.Callable[
		typing.Any,
		typing.Any
	]:
		@functools.wraps(function)
		def wrapped_function(*w_args, **w_kwargs) -> typing.Any:
			if flask.request.json is None:
				raise exceptions.APIJSONMissing

			if not isinstance(flask.request.json, dict):
				raise exceptions.APIJSONInvalid

			validator = APIValidator(
				schema,
				*args,
				**kwargs
			)

			if not validator.validate(flask.request.json):
				raise exceptions.APIJSONInvalid(validator.errors)

			flask.g.json = validator.document

			return function(*w_args, **w_kwargs)
		return wrapped_function
	return wrapper
