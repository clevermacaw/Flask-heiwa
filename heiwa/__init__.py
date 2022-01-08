"""Heiwa, a forum API."""

from __future__ import annotations

import datetime
import os
import time

import flask
import sqlalchemy
import sqlalchemy.orm
import werkzeug.exceptions

__all__ = [
	"ConfiguredLockFlask",
	"create_app"
]
__version__ = "0.17.0"


class ConfiguredLockFlask(flask.Flask):
	"""A Flask subclass which supports detecting and setting whether or not
	everything has been set up for production use.
	"""

	def __init__(self: ConfiguredLockFlask, *args, **kwargs) -> None:
		"""Sets whether or not this app has been configured, and when the last
		update to its config was. This depends on whether or not the file located
		where the ``CONFIGURED_LOCK_LOCATION`` environment variable (or
		``'$current_working_directory/configured.lock'``, if it's unset)
		describes exists, and its content if it does. If it doesn't exist, the
		app has not been configured. Otherwise, it has, and the last time that
		happened was when the file's content - an ISO-8601 datetime - describes.
		"""

		self.lock_file_location = os.environ.get(
			"CONFIGURED_LOCK_LOCATION",
			f"{os.getcwd()}/configured.lock"
		)

		self._configured = os.path.isfile(self.lock_file_location)

		if self._configured:
			with open(self.lock_file_location, "r", encoding="utf-8") as lock_file:
				self._last_configured = datetime.datetime.fromisoformat(
					lock_file.read().splitlines()[0]
				)
		else:
			self._last_configured = None

		flask.Flask.__init__(self, *args, **kwargs)

	@property
	def configured(self: ConfiguredLockFlask) -> bool:
		"""Gets the value in the
		:attr:`_configured <.ConfiguredLockFlask._configured>` instance variable.
		This describes whther or not the current app has been properly set up for
		production use.

		:returns: The variable.
		"""

		return self._configured

	@configured.setter
	def configured(
		self: ConfiguredLockFlask,
		configured_: bool
	) -> None:
		"""Sets whether or not this app has been configured, and creates / removes
		the lock file.

		:param configured_: Whether or not the app has been configured.
		"""

		if configured_:
			with open(self.lock_file_location, "w", encoding="utf-8") as lock_file:
				if self._last_configured is None:
					self._last_configured = datetime.datetime.now(tz=datetime.timezone.utc)

				lock_file.write(self._last_configured.isoformat())
		elif os.path.exists(self._lock_file_location):
			os.remove(self.lock_file_location)

		self._configured = configured_

	@property
	def last_configured(self: ConfiguredLockFlask) -> typing.Union[
		None,
		datetime.datetime
	]:
		"""Gets the value in the
		:attr:`_last_configured <.ConfiguredLockFlask._last_configured>` instance
		variable. This describes the last time the current app was re/configured.

		:returns: The variable.
		"""

		return self._last_configured

	@last_configured.setter
	def last_configured(
		self: ConfiguredLockFlask,
		last_configured_: datetime.datetime
	) -> None:
		"""Sets the last time this app has been re/configured. If it has not been
		configured before, it's automatically set to :data:`True`.

		:param last_configured_: The last time the app has been re/configured.
		"""

		if not self._configured:
			self._configured = True

		with open(self._lock_file_location, "w", encoding="utf-8") as lock_file:
			lock_file.write(last_configured_)

		self._last_configured = datetime.datetime


def create_app() -> ConfiguredLockFlask:
	r"""Creates a pre-configured :class:`.ConfiguredLockFlask` app. If the app is
	detected as not having been fully configured before, all database models and
	tables are also created. Once that's done, default
	:class:`Group <.database.Group>``\ s are also created. If the app's config
	file was last changed after the app was configured, it's checked if any
	:class:`User <.database.User>`\ s have
	:attr:`extra_fields <.database.User.extra_fields>` which are no longer
	allowed, and removed if so.
	"""

	app = ConfiguredLockFlask(__name__)

	with app.app_context():
		config_location = os.environ.get(
			"CONFIG_LOCATION",
			f"{os.getcwd()}/config.py"
		)

		app.config.from_pyfile(config_location)

		sa_engine = sqlalchemy.create_engine(app.config["DATABASE_URI"])

		app.SASession = sqlalchemy.orm.scoped_session(
			sqlalchemy.orm.sessionmaker(
				bind=sa_engine
			)
		)

		from .encoders import JSONEncoder
		from .limiter import Limiter

		app.json_encoder = JSONEncoder
		app.limiter = Limiter(
			key_func=lambda: flask.g.identifier
		)

		from .exceptions import APIException, APIRateLimitExceeded

		@app.before_request
		def before_request() -> None:
			"""Sets the global current user identifier (``flask.g.identifier``)
			to the remote IP address, and creates a basic SQLAlchemy session
			derived from ``flask.current_app.SASession`` at ``flask.g.sa_session``.
			"""

			flask.g.identifier = flask.request.remote_addr

			is_rate_limit_exceeded, rate_limit_expires = (
				flask.current_app.limiter.check(add_expires=True)
			)

			if not is_rate_limit_exceeded:
				raise APIRateLimitExceeded(details=rate_limit_expires)

			flask.g.sa_session = flask.current_app.SASession()

		@app.teardown_request
		def teardown_request(response: flask.Response) -> flask.Response:
			"""Closes and removes ``flask.g.sa_session``, using
			``flask.current_app.SASession``.
			"""

			if "sa_session" in flask.g:
				flask.current_app.SASession.remove()

			return response

		app.configured = True

		from .errorhandlers import handle_api_exception, handle_http_exception

		for handler in (
			(
				APIException,
				handle_api_exception
			),
			(
				werkzeug.exceptions.HTTPException,
				handle_http_exception
			)
		):
			app.register_error_handler(*handler)

		from .views import (
			category_blueprint,
			forum_blueprint,
			group_blueprint,
			guest_blueprint,
			message_blueprint,
			meta_blueprint,
			notification_blueprint,
			openid_blueprint,
			post_blueprint,
			thread_blueprint,
			user_blueprint
		)

		for blueprint in (
			category_blueprint,
			forum_blueprint,
			group_blueprint,
			guest_blueprint,
			message_blueprint,
			meta_blueprint,
			notification_blueprint,
			openid_blueprint,
			post_blueprint,
			thread_blueprint,
			user_blueprint
		):
			app.register_blueprint(blueprint)

		if not app.configured:
			from .database import Base, Group, GroupPermissions

			with app.SASession() as sa_session:
				Base.metadata.create_all(bind=sa_engine)

				for group_name, group_attrs in app.config["GROUP_DEFAULTS"].items():
					if sa_session.execute(
						sqlalchemy.select(Group).
						where(Group.name == group_name)
					).scalars().one_or_none() is not None:
						continue

					group = Group.create(
						sa_session,
						default_for=group_attrs["default_for"],
						level=group_attrs["level"],
						name=group_name,
						description=group_attrs["description"]
					)

					# Need to get the group ID here
					sa_session.commit()

					if "permissions" in group_attrs:
						GroupPermissions.create(
							sa_session,
							group_id=group.id,
							**group_attrs["permissions"]
						)

					sa_session.commit()

		if (
			app.last_configured
			< datetime.datetime.fromtimestamp(
				os.path.getmtime(config_location),
				tz=datetime.timezone.utc
			)
		):
			from .database import User

			with app.SASession() as sa_session:
				any_user_changed = False

				for user in sa_session.execute(
					sqlalchemy.select(User).
					where(~User.extra_fields.is_(None))
				):
					for extra_field in user.extra_fields:
						if extra_field not in app.config["USER_EXTRA_FIELDS"]:
							any_user_changed = True

							user.extra_fields.remove(extra_field)

				if any_user_changed:
					sa_session.commit()

	return app
