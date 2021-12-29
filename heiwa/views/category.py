"""API views for :class:`Category <heiwa.database.Category>` objects."""

import flask

from .. import encoders

__all__ = ["category_blueprint"]

category_blueprint = flask.Blueprint(
	"category",
	__name__,
	url_prefix="/categories"
)
category_blueprint.json_encoder = encoders.JSONEncoder

# TODO
