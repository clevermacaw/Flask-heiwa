from __future__ import annotations

import datetime
import typing

import flask
import limits
import limits.storage
import limits.strategies

__all__ = ["Limiter"]
__version__ = "2.2.1"


class Limiter:
	"""Rate limiter, mainly compatible with Flask applications."""

	def __init__(
		self: Limiter,
		default_limits: typing.Union[
			None,
			typing.Iterable[str]
		] = None,
		endpoint_limits: typing.Union[
			None,
			typing.Dict[
				str,
				typing.Iterable[str]
			]
		] = None,
		Storage: limits.storage.Storage = limits.storage.MemoryStorage,
		Strategy: limits.strategies.RateLimiter = (
			limits.strategies.MovingWindowRateLimiter
		),
		key_func: typing.Callable[
			[None],
			typing.Hashable
		] = lambda: flask.request.remote_addr,
		endpoint_func: typing.Callable[
			[None],
			str
		] = lambda: flask.request.endpoint
	) -> None:
		"""Sets this instance's attributes to the given values.
		If ``default_limits`` is ``None``, and this method is running within
		a Flask app context, it's set to the current Flask app's
		``'RATELIMIT_DEFAULT'`` config key as long there is one.
		The same applies to ``endpoint_limits`` as well, but with the
		``'RATELIMIT_SPECIFIC'`` config key.
		"""

		self.default_limits = [
			limits.parse(limit)
			for limit in (
				default_limits
				if default_limits is not None
				else (
					flask.current_app.config["RATELIMIT_DEFAULT"]
					if (
						flask.has_app_context() and
						"RATELIMIT_DEFAULT" in flask.current_app.config
					)
					else default_limits
				)
			)
		]
		self.endpoint_limits = {
			endpoint: [
				limits.parse(limit)
				for limit in limit_set
			]
			for endpoint, limit_set in (
				endpoint_limits.items()
				if endpoint_limits is not None
				else (
					flask.current_app.config["RATELIMIT_SPECIFIC"].items()
					if (
						flask.has_app_context() and
						"RATELIMIT_SPECIFIC" in flask.current_app.config
					)
					else endpoint_limits
				)
			)
		}

		self.storage = Storage()
		self.strategy = Strategy(self.storage)

		self.key_func = key_func
		self.endpoint_func = endpoint_func

	def check(
		self: Limiter,
		identifier: typing.Union[
			None,
			typing.Hashable
		] = None,
		endpoint: typing.Union[
			None,
			str
		] = None,
		add_expires: bool = False
	) -> typing.Union[
		bool,
		typing.Tuple[
			bool,
			typing.Union[
				None,
				datetime.datetime
			]
		]
	]:
		"""Returns whether or not the user with the given identifier
		(the output of ``self.key_func`` by default) can access ``endpoint``
		(the output of ``self.endpoint_func`` by default) with its rate limit.
		If ``add_expires`` is ``True`` and the user has passed the check,
		the time when the lowest rate limit's entry in the storage expires
		is also returned. Otherwise, if the user has not passed the check,
		the storage expiration time of the rate limit it failed on is returned.
		"""

		identifier = self.key_func() if identifier is None else identifier
		endpoint = self.endpoint_func() if endpoint is None else endpoint

		limit_set = (
			self.endpoint_limits[endpoint]
			if endpoint in self.endpoint_limits
			else self.default_limits
		)

		passed_limit = True
		soonest_expiration_limit = None

		if len(limit_set) != 0:
			for limit in limit_set:
				if (
					soonest_expiration_limit is None or
					soonest_expiration_limit.get_expiry() > limit.get_expiry()
				):
					soonest_expiration_limit = limit

				if not self.strategy.hit(
					limit,
					identifier,
					endpoint
				):
					soonest_expiration_limit = limit
					passed_limit = False

		# If there are no rate limits specified, we can assume
		# this endpoint has none. For example, a rate limit
		# specific to this endpoint is ``[]``, overrides the default,
		# and that endpoint then has no rate limit.

		if add_expires:
			return (
				passed_limit,
				datetime.datetime.fromtimestamp(
					self.strategy.get_window_stats(
						soonest_expiration_limit,
						identifier,
						endpoint
					)[0],
					tz=datetime.timezone.utc
				)
			)

		return passed_limit
