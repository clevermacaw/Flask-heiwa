"""API error handlers. Unless something is very wrong, responses will always
contain dictionaries.
"""

import typing

import flask
import werkzeug.exceptions

from .. import exceptions

__all__ = [
	"handle_api_exception",
	"handle_http_exception"
]
__version__ = "1.4.0"


def handle_api_exception(
	exception: exceptions.APIException
) -> typing.Tuple[flask.Response, int]:
	"""Turns an :class:`APIException <heiwa.exceptions.APIException>` object into
	a dictionary of its type (class name) and
	:attr:`details <heiwa.exceptions.APIException.details>`, then returns a tuple
	of:
		#. The dictionary contained within a :class:`flask.Response`.
		#. Its status code.
	"""

	return flask.jsonify({
		"type": exception.__class__.__name__,
		"details": exception.details
	}), exception.code


def handle_http_exception(
	exception: werkzeug.exceptions.HTTPException
) -> typing.Tuple[flask.Response, int]:
	"""Turns an :class:`HTTPException <werkzeug.exceptions.HTTPException>` object
	into a dictionary of its type (class name) and
	:attr:`description <werkzeug.exceptions.HTTPException.description>`, then
	returns a tuple of:
		#. The dictionary contained within a :class:`flask.Response`.
		#. Its status code.

	.. note::
		Flask's default error handler knows how to handle this type of exception
		already, but since it uses HTML documents to do so, it would be inconsistent
		with the rest of the API.
	"""

	return flask.jsonify({
		"type": exception.__class__.__name__,
		"details": exception.description
	}), exception.code
