import datetime
import hashlib
import typing

import flask
import sqlalchemy

from .. import database, encoders, exceptions, statuses
from .utils import create_jwt

__all__ = ["guest_blueprint"]

guest_blueprint = flask.Blueprint(
	"guest",
	__name__,
	url_prefix="/guest"
)
guest_blueprint.json_encoder = encoders.JSONEncoder

REGISTERED_BY = "guest"


@guest_blueprint.route("/token", methods=["GET"])
def token() -> typing.Tuple[flask.Response, int]:
	"""Returns the access token for a temporary user account. The token expires
	after the time value provided in seconds within the
	``'GUEST_SESSION_EXPIRES_AFTER'`` config key. When another user uses this
	endpoint, all expired guest accounts will also be deleted, provided that
	they have no public content. (threads, posts, forums)
	"""

	max_creation_timestamp = (
		datetime.datetime.now(tz=datetime.timezone.utc)
		- datetime.timedelta(
			seconds=flask.current_app.config[
				"GUEST_SESSION_EXPIRES_AFTER"
			]
		)
	)

	# Delete all expired sessions with no content

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.User).
		where(
			sqlalchemy.and_(
				database.User.creation_timestamp <= max_creation_timestamp,
				database.User.registered_by == REGISTERED_BY,
				~database.User.has_content
			)
		).
		execution_options(synchronize_session="fetch")
	)

	# Remove external identifier for guests with content that would have been
	# deleted otherwise

	flask.g.sa_session.execute(
		sqlalchemy.update(database.User).
		where(
			sqlalchemy.and_(
				database.User.creation_timestamp <= max_creation_timestamp,
				database.User.registered_by == REGISTERED_BY,
				database.User.has_content
			)
		).
		values(external_id=None).
		execution_options(synchronize_session="fetch")
	)

	# Commit here just in case there is something wrong with user input,
	# and an exception is raised

	flask.g.sa_session.commit()

	# NOTE: The app's secret key isn't the greatest salt ever, but the best
	# we can afford to use here, since we're searching for users based on its
	# value. Unfortunately, this means using a random string is out of the
	# question.

	hashed_identifier = hashlib.scrypt(
		flask.g.identifier.encode("utf-8"),
		salt=flask.current_app.config["SECRET_KEY"].encode("utf-8"),
		n=flask.current_app.config["GUEST_SCRYPT_N"],
		r=flask.current_app.config["GUEST_SCRYPT_R"],
		p=flask.current_app.config["GUEST_SCRYPT_P"],
		maxmem=flask.current_app.config["GUEST_SCRYPT_MAXMEM"],
		dklen=32
	).hex()

	existing_session_count = flask.g.sa_session.execute(
		sqlalchemy.select(
			sqlalchemy.func.count(
				database.User.id
			)
		).
		where(
			sqlalchemy.and_(
				database.User.creation_timestamp >= max_creation_timestamp,
				database.User.registered_by == REGISTERED_BY,
				database.User.external_id == hashed_identifier
			)
		)
	).scalars().one()

	print(existing_session_count)

	if (
		existing_session_count
		>= flask.current_app.config["GUEST_MAX_SESSIONS_PER_IP"]
	):
		# Don't share max session limit, it could theoretically be used to obtain
		# basic information about other users. Potentially sensitive config
		# information could also be obtained.

		raise exceptions.APIGuestSessionLimitReached

	user = database.User(
		registered_by=REGISTERED_BY,
		external_id=hashed_identifier
	)
	user.write(
		flask.g.sa_session,
		bypass_first_user_check=True
	)  # Temporary account, don't make it important

	flask.g.sa_session.commit()

	return flask.jsonify({
		"token": create_jwt(
			user.id,
			expires_after=flask.current_app.config["GUEST_SESSION_EXPIRES_AFTER"]
		)
	}), statuses.CREATED
