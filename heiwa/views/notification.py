import typing
import uuid

import flask
import sqlalchemy
import sqlalchemy.orm

from .. import (
	authentication,
	database,
	encoders,
	exceptions,
	statuses,
	validators
)
from .utils import (
	generate_search_schema,
	generate_search_schema_registry,
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
	"type": {
		"type": "string",
		"minlength": 1,
		"maxlength": 128
	},
	"identifier": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	}
}

SEARCH_SCHEMA = generate_search_schema(
	("creation_timestamp",),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"]
}
SEARCH_SCHEMA_REGISTRY = generate_search_schema_registry({
	"$eq": {
		"type": "dict",
		"schema": {
			"id": ATTR_SCHEMAS["id"],
			"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
			"user_id": ATTR_SCHEMAS["user_id"],
			"is_read": ATTR_SCHEMAS["is_read"],
			"type": ATTR_SCHEMAS["type"],
			"identifier": ATTR_SCHEMAS["identifier"]
		},
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
	"$ge": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$in": {
		"type": "dict",
		"schema": {
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
			"type": {
				"type": "list",
				"schema": ATTR_SCHEMAS["type"],
				"minlength": 1,
				"maxlength": 32
			},
			"identifier": {
				"type": "list",
				"schema": ATTR_SCHEMAS["identifier"],
				"minlength": 1,
				"maxlength": 32
			}
		},
		"maxlength": 1
	}
})


def find_notification_by_id(
	notification_id: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user_id: uuid.UUID
) -> database.Notification:
	"""Finds the notification with the given ``notification_id``. If it exists,
	but doesn't belong to the user with the provided ``user_id``,
	``APINotificationNotFound`` will be raised as if it didn't exist.
	"""

	notification = session.execute(
		sqlalchemy.select(database.Notification).
		where(
			sqlalchemy.and_(
				database.Notification.id == notification_id,
				database.Notification.user_id == user_id
			)
		)
	).scalars().one_or_none()

	if notification is None:
		raise exceptions.APINotificationNotFound

	return notification


@notification_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all notifications belonging to ``flask.g.user`` that match the
	requested filter, if there is one.
	"""

	conditions = (database.Notification.user_id == flask.g.user.id)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Notification
			)
		)

	order_column = getattr(
		database.Notification,
		flask.g.json["order"]["by"]
	)

	notifications = flask.g.sa_session.execute(
		sqlalchemy.select(database.Notification).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(notifications), statuses.OK


@notification_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all notifications belonging to ``flask.g.user`` that match the
	requested filter, if there is one.
	"""

	conditions = (database.Notification.user_id == flask.g.user.id)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Notification
			)
		)

	order_column = getattr(
		database.Notification,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.Notification).
		where(
			database.Notification.id.in_(
				sqlalchemy.select(database.Notification.id).
				where(conditions).
				order_by(
					sqlalchemy.asc(order_column)
					if flask.g.json["order"]["asc"]
					else sqlalchemy.desc(order_column)
				).
				limit(flask.g.json["limit"]).
				offset(flask.g.json["offset"])
			)
		).
		execution_options(synchronize_session="fetch")
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@notification_blueprint.route("/confirm-read", methods=["PUT"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def mass_confirm_read() -> typing.Tuple[flask.Response, int]:
	"""Confirms that all notifications belonging to ``flask.g.user`` that match
	the requested filter (if there is one) have been read.
	"""

	conditions = sqlalchemy.and_(
		database.Notification.user_id == flask.g.user.id,
		database.Notification.is_read.is_(False)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Notification
			)
		)

	order_column = getattr(
		database.Notification,
		flask.g.json["order"]["by"]
	)

	notifications = flask.g.sa_session.execute(
		sqlalchemy.select(database.Notification).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	for notification in notifications:
		notification.is_read = True

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@notification_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the notification with the requested ``id_``."""

	notification = find_notification_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	)

	notification.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@notification_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the notification with the requested ``id_``."""

	return flask.jsonify(
		find_notification_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user.id
		)
	), statuses.OK


@notification_blueprint.route("/<uuid:id_>/confirm-read", methods=["PUT"])
@authentication.authenticate_via_jwt
def confirm_read(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Confirms that the notification with the requested ``id_`` has been read."""

	notification = find_notification_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	)

	notification.is_read = True

	return flask.jsonify({}), statuses.NO_CONTENT
