import datetime
import typing

import flask
import sqlalchemy

from .. import encoders, exceptions, helpers, limiter, models
from .helpers import create_jwt, get_endpoint_limit

__all__ = ["guest_blueprint"]

guest_blueprint = flask.Blueprint(
	"guest",
	__name__,
	url_prefix="/guest"
)
guest_blueprint.json_encoder = encoders.JSONEncoder


@guest_blueprint.route("/token", methods=["GET"])
@limiter.limiter.limit(get_endpoint_limit)
def token() -> typing.Tuple[flask.Response, int]:
	"""Returns the access token for a temporary user account.
	The token expires after `GUEST_SESSION_EXPIRES_AFTER`.
	When another user uses this endpoint, all expired guest accounts will also be
	deleted, provided that they have no public content. (threads, posts, forums)

	Not idempotent.
	"""

	max_creation_timestamp = (
		datetime.datetime.now(tz=datetime.timezone.utc) +
		datetime.timedelta(seconds=flask.current_app.config[
			"GUEST_SESSION_EXPIRES_AFTER"
		])
	)

	existing_session_count = flask.g.sa_session.execute(
		sqlalchemy.select(
			sqlalchemy.func.count(
				models.User.id
			)
		).
		where(
			sqlalchemy.and_(
				models.User.creation_timestamp < max_creation_timestamp,
				models.User.registered_by == "guest",
				models.User.external_id == flask.g.identifier
			)
		)
	).scalars().one()

	if (
		existing_session_count
		>= flask.current_app.config["GUEST_MAX_SESSIONS_PER_IP"]
	):
		# Don't share max session limit, it could theoretically be used to obtain
		# basic information about other users. Potentially sensitive config
		# information could also be obtained.
		raise exceptions.APIGuestSessionLimitReached

	# Delete all expired sessions with no content
	flask.g.sa_session.execute(
		sqlalchemy.delete(models.User).
		where(
			sqlalchemy.and_(
				models.User.creation_timestamp > max_creation_timestamp,
				models.User.registered_by == "guest",
				~models.User.has_content
			)
		).
		execution_options(synchronize_session="fetch")
	)

	# No need to commit here, unless something's very wrong,
	# no exceptions will be raised

	user = models.User(
		registered_by="guest",
		external_id=flask.g.identifier
	)
	user.write(
		flask.g.sa_session,
		bypass_first_user_check=True
	)  # Temporary account, don't make it important

	flask.g.sa_session.commit()

	return flask.jsonify(
		{
			"token": create_jwt(
				user.id,
				expires_after=flask.current_app.config["GUEST_SESSION_EXPIRES_AFTER"]
			)
		}
	), helpers.STATUS_CREATED
