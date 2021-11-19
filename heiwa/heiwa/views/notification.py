import typing
import uuid

import flask
import sqlalchemy
import sqlalchemy.orm

from .. import (
	authentication,
	encoders,
	exceptions,
	helpers,
	limiter,
	models,
	validators
)
from .helpers import (
	generate_list_schema,
	generate_search_schema_registry,
	get_endpoint_limit,
	parse_search
)

__all__ = ["notification_blueprint"]

notification_blueprint = flask.Blueprint(
	"notification",
	__name__,
	url_prefix="/notifications"
)
notification_blueprint.json_encoder = encoders.JSONEncoder

ATTR_SCHEMAS = {
	"id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"creation_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"user_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"is_read": {
		"type": "boolean"
	},
	"type_": {
		"type": "string",
		"minlength": 1,
		"maxlength": 128
	}
}

LIST_SCHEMA = generate_list_schema(
	("creation_timestamp",),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"]
}
EQ_SEARCH_SCHEMA = {
	"id": ATTR_SCHEMAS["id"],
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"user_id": ATTR_SCHEMAS["user_id"],
	"is_read": ATTR_SCHEMAS["is_read"],
	"type_": ATTR_SCHEMAS["type_"]
}
IN_SEARCH_SCHEMA = {
	"id": {
		"type": "list",
		"schema": ATTR_SCHEMAS["id"],
		"minlength": 1,
		"maxlength": 32
	},
	"creation_timestamp": {
		"type": "list",
		"schema": ATTR_SCHEMAS["creation_timestamp"],
		"minlength": 1,
		"maxlength": 32
	},
	"user_id": {
		"type": "list",
		"schema": ATTR_SCHEMAS["user_id"],
		"minlength": 1,
		"maxlength": 32
	},
	"type_": {
		"type": "list",
		"schema": ATTR_SCHEMAS["type_"],
		"minlength": 1,
		"maxlength": 32
	}
}
SEARCH_SCHEMA_REGISTRY = generate_search_schema_registry({
	"$eq": {
		"type": "dict",
		"schema": EQ_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$lt": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$gt": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$le": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$in": {
		"type": "dict",
		"schema": IN_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$ge": {
		"type": "dict",
		"schema": {
			"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"]
		},
		"maxlength": 1
	}
})


def find_notification_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user_id: uuid.UUID
) -> models.Notification:
	"""Finds the notification with the given ID. If it exists, but is not
	owned by the provided user, APINotificationNotFound will be raised as
	if it didn't exist.
	"""

	notification = session.execute(
		sqlalchemy.select(models.Notification).
		where(
			sqlalchemy.and_(
				models.Notification.id == id_,
				models.Notification.user_id == user_id
			)
		)
	).scalars().one_or_none()

	if notification is None:
		raise exceptions.APINotificationNotFound(id)

	return notification


@notification_blueprint.route("", methods=["GET"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists the available notifications.

	Idempotent.
	"""

	conditions = (models.Notification.user_id == flask.g.user.id)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Notification
			)
		)

	order_column = getattr(
		models.Notification,
		flask.g.json["order"]["by"]
	)

	notifications = flask.g.sa_session.execute(
		sqlalchemy.select(models.Notification).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(notifications), helpers.STATUS_OK


@notification_blueprint.route("/confirm-read", methods=["PUT"])
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def confirm_read_all() -> typing.Tuple[flask.Response, int]:
	"""Confirms that all notifications have been read.

	Idempotent.
	"""

	flask.g.sa_session.execute(
		sqlalchemy.update(models.Notification).
		where(models.Notification.user_id == flask.g.user.id).
		values(is_read=True)
	)

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@notification_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all notifications that match the given conditions.

	Not idempotent.
	"""

	conditions = (models.Notification.user_id == flask.g.user.id)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Notification
			)
		)

	order_column = getattr(
		models.Notification,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(
			sqlalchemy.select(models.Notification).
			where(conditions).
			order_by(
				sqlalchemy.asc(order_column)
				if flask.g.json["order"]["asc"]
				else sqlalchemy.desc(order_column)
			).
			limit(flask.g.json["limit"]).
			offset(flask.g.json["offset"])
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@notification_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the notification with the provided ID.

	Idempotent.
	"""

	notification = find_notification_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	)

	notification.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@notification_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the notification with the provided ID.

	Idempotent.
	"""

	return flask.jsonify(
		find_notification_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user.id
		)
	), helpers.STATUS_OK


@notification_blueprint.route("/<uuid:id_>/confirm-read", methods=["PUT"])
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def confirm_read(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Confirms that the notification with the provided ID has been read.

	Idempotent.
	"""

	notification = find_notification_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	)

	notification.is_read = True

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT
