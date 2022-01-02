"""API views for :class:`Category <heiwa.database.Category>` objects."""

import flask

from .. import authentication, encoders, database

__all__ = ["category_blueprint"]

category_blueprint = flask.Blueprint(
	"category",
	__name__,
	url_prefix="/categories"
)
category_blueprint.json_encoder = encoders.JSONEncoder

# TODO

# WARNING: This endpoint is not finished, and is only meant for testing
# environments.
@category_blueprint.route("", methods=["GET"])
@authentication.authenticate_via_jwt
def list_():
	print(
		database.Category.get(
			flask.g.user,
			flask.g.sa_session
		)
	)

	return "Did it work?"
