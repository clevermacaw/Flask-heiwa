import os
import typing

import flask

from .. import encoders, statuses

__all__ = ["meta_blueprint"]

meta_blueprint = flask.Blueprint(
	"meta",
	__name__,
	url_prefix="/meta"
)
meta_blueprint.json_encoder = encoders.JSONEncoder


@meta_blueprint.route("/config", methods=["GET"])
def view_config() -> typing.Tuple[flask.Response, int]:
	"""Returns basic information about this service's config. Keys which should be
	shown are defined in the ``'PUBLIC_CONFIG_KEYS'`` key.
	"""

	return flask.jsonify({
		value.lower(): flask.current_app.config[value]
		for value in flask.current_app.config["PUBLIC_CONFIG_KEYS"]
	}), statuses.OK


@meta_blueprint.route("/icon", methods=["GET"])
def view_icon() -> typing.Tuple[flask.Response, int]:
	"""Returns this service's icon, if there is one."""

	path = os.environ.get(
		"ICON_LOCATION",
		f"{os.getcwd()}/icon.png"
	)
	mimetype = os.environ.get(
		"ICON_MIMETYPE",
		"image/png"
	)

	if not os.path.exists(path):
		response = flask.jsonify(None)
	else:
		response = flask.send_file(
			path,
			mimetype=mimetype,
			as_attachment=True,
			download_name=os.path.basename(path),
			last_modified=os.path.getmtime(path)
		)

	return response, statuses.OK


@meta_blueprint.route("/info", methods=["GET"])
def view_info() -> typing.Tuple[flask.Response, int]:
	"""Returns all meta information about this service. Not hardcoded to accept
	certain config keys, looks for all keys beginning with ``'META_'``.
	"""

	return flask.jsonify({
		key[5:].lower(): value
		for key, value in flask.current_app.config.items()
		if key.startswith("META_")
	}), statuses.OK
