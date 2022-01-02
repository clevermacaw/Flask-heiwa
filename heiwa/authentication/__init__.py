"""Authentication for the API."""

import collections.abc
import datetime
import functools
import typing

import authlib.jose
import flask

from .. import database, exceptions

__all__ = ["authenticate_via_jwt"]
__version__ = "3.2.5"


def authenticate_via_jwt(
	function: collections.abc.Callable[
		typing.Any,
		typing.Any
	]
) -> collections.abc.Callable[
	typing.Any,
	typing.Any
]:
	"""If the HTTP ``Authorization`` header is present, derives the current
	:class:`User <heiwa.database.User>` from it (if possible) using JWT and
	assigns them to :attr:`flask.g.user`. If the user is banned, it's checked
	if their ban has expired. If not, access is denied.
	"""

	@functools.wraps(function)
	def wrapped_function(*args, **kwargs) -> typing.Any:
		if "Authorization" not in flask.request.headers:
			raise exceptions.APIAuthorizationHeaderMissing

		if not flask.request.headers["Authorization"][:7] == "Bearer ":
			raise exceptions.APIAuthorizationHeaderInvalid

		try:
			claims = authlib.jose.jwt.decode(
				flask.request.headers["Authorization"][7:],
				flask.current_app.config["SECRET_KEY"]
			)
		except authlib.jose.JoseError:
			raise exceptions.APIJWTInvalid

		try:
			claims.validate()
		except authlib.jose.JoseError:
			raise exceptions.APIJWTInvalidClaims

		user = flask.g.sa_session.get(database.User, claims["sub"])

		if user is None:
			raise exceptions.APIJWTUserNotFound(claims["sub"])

		if user.is_banned:
			if (
				datetime.datetime.now(tz=datetime.timezone.utc)
				> user.ban.expiration_timestamp
			):
				user.remove_ban()
			else:
				raise exceptions.APIUserBanned

		flask.g.identifier = user.id
		flask.g.user = user

		return function(*args, **kwargs)
	return wrapped_function
