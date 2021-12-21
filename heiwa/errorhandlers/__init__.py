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
__version__ = "1.3.4"


def handle_api_exception(
	exception: exceptions.APIException
) -> typing.Tuple[flask.Response, int]:
	"""Turns an ``APIException`` object into a dictionary of its type (class name)
	and details, then returns a tuple of:
		#. The dictionary contained within a ``flask.Response``.
		#. Its status code.
	"""

	return flask.jsonify({
		"exception": {
			"type": exception.__class__.__name__,
			"details": exception.details
		}
	}), exception.code


def handle_http_exception(
	exception: werkzeug.exceptions.HTTPException
) -> typing.Tuple[flask.Response, int]:
	"""Turns an ``HTTPException`` object into a dictionary of its type (class name)
	and description, then returns a tuple of:
		#. The dictionary contained within a ``flask.Response``.
		#. Its status code.

	.. note::
		Flask's default error handler knows how to handle this type of exception
		already, but since it uses HTML documents to do so, it would be inconsistent
		with the rest of the API.
	"""

	return flask.jsonify({
		"exception": {
			"type": exception.__class__.__name__,
			"details": exception.description
		}
	}), exception.code
