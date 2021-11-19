import typing

import flask

__all__ = ["get_endpoint_limit"]


def get_endpoint_limit() -> typing.Union[None, str]:  # PEP 604
	return flask.current_app.config["RATELIMIT_SPECIFIC"].get(
		flask.request.endpoint
	)
