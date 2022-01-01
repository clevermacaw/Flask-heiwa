from __future__ import annotations

import datetime
import typing

import flask
import limits
import limits.storage
import limits.strategies

__all__ = ["Limiter"]
__version__ = "2.2.4"


class Limiter:
	"""Rate limiter, primarily compatible with Flask applications."""

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

		:param default_limits: An iterable of default rate limits. For example,
			``4/1second`` and ``2000/1hour``. If this value is :data:`None` and
			this method is running within a Flask app context, it's set to the
			app's ``RATELIMIT_DEFAULT`` config key, if there is one.
		:param endpoint_limits: The same as ``default_limits``, but for specific
			endpoints, where the key corresponds to the endpoint's name.
		:param Storage: The storage backend this rate limiter uses to store
			requests.
		:param Strategy: The strategy for this rate limiter.
		:param key_func: A function that returns the unique identifier for the
			current user with each request. By default, this will be remote IP
			addresses.
		:param endpoint_func: A function which returns the current endpoint with
			each request. By default, this will be :attr:`flask.request.endpoint`.
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
		"""Returns whether or not the current user has exceeded the rate limit
		for the given endpoint.

		:param identifier: The current user's identifier. If :data:`None`, the
			output of the :attr:`key_func <.Limiter.key_func>` is used. This
			is generally expected behavior.
		:param endpoint: The current endpoint.
		:param add_expires: Whether or not the function should return the time
			the user will be allowed to access the endpoint again. If :data:`True`,
			this will always be returned, even if they have not exceeded the rate
			limit.

		:returns: If ``add_expires`` is :data:`False`, whether or not the user
			has exceeded the rate limit, stored in a boolean value. If it's
			:data:`True`, that value and also the time they can access it again.

		.. note::
			If there are no rate limits specified for the current endpoint, it's
			assumed that it has none. For example, when a rate limit specific to
			the endpoint is an empty iterable, the default limit is overriden
			and the endpoint has no rate limit at all.
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
