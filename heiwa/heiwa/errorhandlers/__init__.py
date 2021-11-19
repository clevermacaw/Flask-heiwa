"""Error handlers for the Heiwa API.
Aims to return a dict no matter what exception has occurred,
unless there is something incredibly wrong.
"""

import typing

import flask
import werkzeug.exceptions

from .. import exceptions

__all__ = [
	"handle_api_exception",
	"handle_http_exception"
]
__version__ = "1.3.0"


def handle_api_exception(
	exception: exceptions.APIException
) -> typing.Tuple[flask.Response, int]:
	"""Converts an APIException object to a response Flask accepts; a tuple
	containing a dict (which will be processed later), and the HTTP status code.
	"""

	return flask.jsonify(
		{
			"exception": {
				"type": exception.__class__.__name__,
				"details": exception.details
			}
		}
	), exception.code


def handle_http_exception(
	exception: werkzeug.exceptions.HTTPException
) -> typing.Tuple[flask.Response, int]:
	"""Converts an HTTPException object to a dict, which will be processed later.
	Flask does know how to handle HTTP exceptions on its own, but uses HTML
	documents to do so - which would be inconsistent with the rest of our API.
	"""

	return flask.jsonify(
		{
			"exception": {
				"type": exception.__class__.__name__,
				"details": exception.description
			}
		}
	), exception.code
