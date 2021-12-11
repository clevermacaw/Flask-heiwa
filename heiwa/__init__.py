from __future__ import annotations

import functools
import os

import flask
import sqlalchemy
import sqlalchemy.orm
import werkzeug.exceptions

__all__ = [
	"ConfiguredLockFlask",
	"create_app"
]
__version__ = "0.13.44"


class ConfiguredLockFlask(flask.Flask):
	"""A Flask subclass which supports detecting whether or not everything has
	been set up for production use based on either `CONFIGURED_LOCK_LOCATION`,
	or `$current_working_directory/configured.lock`.
	"""

	@property
	@functools.lru_cache()
	def configured(self: ConfiguredLockFlask) -> bool:
		"""Returns whether or not this instance has been configured.
		This value depends on whether or not either the file located at
		the `CONFIGURED_LOCK_LOCATION` environment variable exists, or the
		`$current_working_directory/configured.lock` file exists.
		(Exists → False, Doesn't exist → True)
		"""

		return not os.path.isfile(
			os.environ.get(
				"CONFIGURED_LOCK_LOCATION",
				f"{os.getcwd()}/configured.lock"
			)
		)

	@configured.setter
	def configured(
		self: ConfiguredLockFlask,
		configured: bool
	) -> None:
		"""Sets whether or not this instance has been configured, and clears
		the getter's cache.
		"""

		location = os.environ.get(
			"CONFIGURED_LOCK_LOCATION",
			f"{os.getcwd()}/configured.lock"
		)

		if os.path.exists(location) and configured:
			os.remove(location)
		elif not configured:
			open(location, "w").close()

		self.configured.fget.cache_clear()


def create_app() -> ConfiguredLockFlask:
	"""Creates a pre-configured `ConfiguredLockFlask` Heiwa app.
	If the file defining whether or not this app has been configured
	before exists (meaning that isn't the case), the database models
	and tables are also created. Once that's done, default groups are
	also created.
	"""

	app = ConfiguredLockFlask(__name__)

	with app.app_context():
		app.config.from_pyfile(
			os.environ.get(
				"CONFIG_LOCATION",
				f"{os.getcwd()}/config.py"
			)
		)

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
			"""Sets the global user identifier (`flask.g.identifier`) to the
			remote IP address, and creates a basic SQLAlchemy session derived
			from `flask.current_app.SASession` at `flask.g.sa_session`.
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
			"""Closes and removes `flask.g.sa_session`, using
			`flask.current_app.SASession`.
			"""

			if "sa_session" in flask.g:
				flask.current_app.SASession.remove()

			return response

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
			forum_blueprint,
			group_blueprint,
			guest_blueprint,
			meta_blueprint,
			notification_blueprint,
			openid_blueprint,
			post_blueprint,
			thread_blueprint,
			user_blueprint
		)

		for blueprint in (
			forum_blueprint,
			group_blueprint,
			guest_blueprint,
			meta_blueprint,
			notification_blueprint,
			openid_blueprint,
			post_blueprint,
			thread_blueprint,
			user_blueprint
		):
			app.register_blueprint(blueprint)

		if not app.configured:
			from .models import Base, Group, GroupPermissions

			Base.metadata.create_all(bind=sa_engine)

			with app.SASession() as sa_session:
				for group_name, group_attrs in app.config["GROUP_DEFAULTS"].items():
					if sa_session.execute(
						sqlalchemy.select(Group).
						where(Group.name == group_name)
					).scalars().one_or_none() is not None:
						continue

					group_to_add = Group.create(
						sa_session,
						default_for=group_attrs["default_for"],
						level=group_attrs["level"],
						name=group_name,
						description=group_attrs["description"]
					)

					if "permissions" in group_attrs:
						GroupPermissions.create(
							sa_session,
							group_id=group_to_add.id,
							**group_attrs["permissions"]
						)

					sa_session.commit()

	return app
