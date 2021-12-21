"""Validators for requests sent to the API. Uses Cerberus, and currently only
supports JSON.
"""

from __future__ import annotations

import base64
import collections
import datetime
import functools
import re
import typing
import uuid

import cerberus
import flask
import validators

from .. import exceptions, types

__all__ = ["APIValidator", "validate_json"]
__version__ = "1.10.1"


class APIValidator(cerberus.Validator):
	"""Cerberus validator for the API."""

	def _check_with_is_valid_regex(
		self: APIValidator,
		field: str,
		value: str
	) -> None:
		"""Checks whether or not ``value`` is a valid regular expression."""

		try:
			re.compile(value)
		except re.error:
			self._error(field, "must be a valid regular expression")

	def _check_with_is_public_url(
		self: APIValidator,
		field: str,
		value: str
	) -> None:
		"""Checks that ``value`` is a valid URL, and corresponds to a public resource."""

		try:
			validators.url(value, public=True)
		except validators.ValidationFailure:
			self._error(field, "must be a valid public URL")

	def _check_with_has_no_duplicates(
		self: APIValidator,
		field: str,
		value: typing.List[typing.Any]
	) -> None:
		"""Checks that the list in ``value`` contains no duplicate items."""

		if len(value) != len(set(value)):
			self._error(field, "must contain no duplicate items")

	def _normalize_coerce_convert_to_uuid(
		self: APIValidator,
		value: str
	) -> uuid.UUID:
		"""Converts the ``value`` to an UUID."""

		return uuid.UUID(value)

	def _normalize_coerce_convert_to_datetime(
		self: APIValidator,
		value: str
	) -> datetime.datetime:
		"""As long as ``value`` is a string formatted as per ISO-8601,
		it's converted to a ``datetime`` object.
		"""

		result = datetime.datetime.fromisoformat(value)

		if result.tzinfo is None:
			raise ValueError("must have a timezone")

		return result

	def _normalize_coerce_decode_base64(
		self: APIValidator,
		value: str
	) -> bytes:
		"""Converts the base64 ``value`` to the bytes it represents."""

		return base64.b64decode(
			value,
			validate=True
		)

	def _validate_length_divisible_by(
		self: APIValidator,
		divider: int,
		field: str,
		value: types.SupportsLength
	) -> None:
		"""Checks whether or not the length of ``value`` is divisible by ``divider``.
		If not, an error is raised.
		The rule's arguments are validated against this schema:
		{
			'type': 'integer'
		}
		"""

		if len(value) % divider != 0:
			self._error(field, f"length must be divisible by {divider}")

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
		"""For every key in ``makes_required``:
			* If the key's value is an iterable, and the corresponding field's
			value equals one of them, the field is treated as if it was required.
			* If the key's value is not an iterable, and the corresponding field
			equals it, it's treated as if it was required.

		.. note::
			There are no ``valuesrules`` defined for the rule validation schema,
			since unlike type *hints*, where they serve as a hint and no actual
			validation is performed, checking whether or not the value is a ``list``
			of ``any`` / simply ``any`` would be redundant and always resolve to
			``True``.

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
	"""Checks JSON data sent in the ``flask.request`` against a Cerberus schema.
	If there is no data at all, ``exceptions.APIJSONMissing`` will be raised. If
	there is data, but it's not a dictionary as ``cerberus.Validator`` requires,
	``exceptions.APIJSONInvalid`` will be raised will no additional details. If
	the data is invalid as per the schema, ``exceptions.APIJSONInvalid`` will be
	raised with the validation errors given in its details.
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
