import collections.abc
import functools
import typing

import flask
import sqlalchemy.orm

import heiwa.database
import heiwa.exceptions

__all__ = [
	"requires_permission",
	"validate_permission"
]


def requires_permission(
	action: typing.Union[
		str,
		typing.Callable
	],
	resource: typing.Union[
		sqlalchemy.orm.DeclarativeMeta,
		heiwa.database.Base
	]
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
	"""Checks whether or not ``flask.g.user`` has permission to perform ``action``
	(string, or callable that returns a string) on the given ``resource``.
	Raises ``heiwa.exceptions.APINoPermission`` if that's not the case.
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
			validate_permission(
				flask.g.user,
				action if isinstance(action, str) else action(),
				resource
			)

			return function(*w_args, **w_kwargs)
		return wrapped_function
	return wrapper


def validate_permission(
	user: heiwa.database.User,
	action: str,
	resource: typing.Union[
		sqlalchemy.orm.DeclarativeMeta,
		heiwa.database.Base
	]
) -> None:
	"""Checks whether or not ``user`` has permission to perform ``action`` on
	the given ``resource``. Raises ``heiwa.exceptions.APINoPermission`` if that's
	not the case.
	"""

	if isinstance(resource, sqlalchemy.orm.DeclarativeMeta):
		resource_name = resource.__name__

		allowed = resource.get_class_permission(
			user,
			action
		)
	else:
		resource_name = resource.__class__.__name__

		allowed = resource.get_instance_permission(
			user,
			action
		)

	if not allowed:
		raise heiwa.exceptions.APINoPermission({
			"resource": resource_name,
			"action": action
		})
