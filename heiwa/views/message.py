import typing
import uuid

import flask
import sqlalchemy

from .. import (
	authentication,
	database,
	encoders,
	exceptions,
	statuses,
	validators
)
from .utils import (
	SEARCH_MAX_IN_LIST_LENGTH,
	generate_search_schema,
	generate_search_schema_registry,
	parse_search,
	validate_user_exists
)

__all__ = ["message_blueprint"]

message_blueprint = flask.Blueprint(
	"messages",
	__name__,
	url_prefix="/messages"
)
message_blueprint.json_encoder = encoders.JSONEncoder

ATTR_SCHEMAS = {
	"id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"creation_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"edit_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"edit_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"sender_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"receiver_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"is_read": {
		"type": "boolean"
	},
	"encrypted_session_key": {
		"type": "binary",
		"coerce": "decode_base64",
		"length_divisible_by": 16,
		"minlength": 128,  # encrypted with 1024-bit RSA
		"maxlength": SEARCH_MAX_IN_LIST_LENGTH   # encrypted with 4096-bit RSA
	},
	"tag": {
		"type": "string",
		"minlength": 1,  # Both values are completely arbitrary.
		"maxlength": database.Message.tag.property.columns[0].type.length
	},
	"encrypted_content": {
		"type": "binary",
		"coerce": "decode_base64",
		"length_divisible_by": 16,
		"minlength": 16,  # Min. AES-CBC length, block size 16
		"maxlength": 262160  # ~65536 character message with each char being 4 bytes
	}
}

CREATE_EDIT_SCHEMA = {
	"receiver_id": {
		**ATTR_SCHEMAS["receiver_id"],
		"required": True
	},
	"encrypted_session_key": {
		**ATTR_SCHEMAS["encrypted_session_key"],
		"required": True
	},
	"tag": {
		**ATTR_SCHEMAS["tag"],
		"nullable": True,
		"required": True
	},
	"encrypted_content": {
		**ATTR_SCHEMAS["encrypted_content"],
		"required": True
	}
}
SEARCH_SCHEMA = generate_search_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"edit_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"]
}
SEARCH_SCHEMA_REGISTRY = generate_search_schema_registry({
	"$eq": {
		"type": "dict",
		"schema": {
			"id": ATTR_SCHEMAS["id"],
			"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
			"edit_timestamp": {
				**ATTR_SCHEMAS["edit_timestamp"],
				"nullable": True
			},
			"edit_count": ATTR_SCHEMAS["edit_count"],
			"sender_id": ATTR_SCHEMAS["sender_id"],
			"receiver_id": ATTR_SCHEMAS["receiver_id"],
			"is_read": ATTR_SCHEMAS["is_read"],
			"encrypted_session_key": ATTR_SCHEMAS["encrypted_session_key"],
			"tag": {
				**ATTR_SCHEMAS["tag"],
				"nullable": True
			},
			"encrypted_content": ATTR_SCHEMAS["encrypted_content"]
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
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"creation_timestamp": {
				"type": "list",
				"schema": ATTR_SCHEMAS["creation_timestamp"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"edit_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["edit_timestamp"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"edit_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["edit_count"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"sender_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["sender_id"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"receiver_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["receiver_id"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"encrypted_session_key": {
				"type": "list",
				"schema": ATTR_SCHEMAS["encrypted_session_key"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"tag": {
				"type": "list",
				"schema": ATTR_SCHEMAS["tag"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"encrypted_content": {
				"type": "list",
				"schema": ATTR_SCHEMAS["encrypted_content"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			}
		},
		"maxlength": 1
	}
})


def find_message_by_id(
	message_id: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user_id: uuid.UUID
) -> database.Message:
	"""Finds the message with the given ``message_id``. If it exists, but hasn't
	been sent or received by the user with the provided ``user_id``,
	``APIMessageNotFound`` will be raised as if it didn't exist.
	"""

	message = session.execute(
		sqlalchemy.select(database.Message).
		where(
			sqlalchemy.and_(
				database.Message.id == message_id,
				sqlalchemy.or_(
					database.Message.sender_id == user_id,
					database.Message.receiver_id == user_id
				)
			)
		)
	).scalars().one_or_none()

	if message is None:
		raise exceptions.APIMessageNotFound

	return message


@message_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a message with the requested `receiver_id`, `encrypted_session_key`,
	`tag` and `encrypted_content`.
	"""

	if flask.g.json["receiver_id"] == flask.g.user.id:
		raise exceptions.APIMessageCannotSendToSelf

	validate_user_exists(
		flask.g.json["receiver_id"],
		flask.g.sa_session,
		flask.g.user
	)

	if flask.g.sa_session.execute(
		sqlalchemy.select(database.user_blocks.c.blockee_id).
		where(
			sqlalchemy.and_(
				database.user_blocks.c.blocker_id == flask.g.json["receiver_id"],
				database.user_blocks.c.blockee_id == flask.g.user.id
			)
		).
		exists().
		select()
	).scalars().one():
		raise exceptions.APIMessageReceiverBlockedSender

	message = database.Message.create(
		flask.g.sa_session,
		sender_id=flask.g.user.id,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(message), statuses.CREATED


@message_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all messages sent or received by ``flask.g.user`` that match the
	requested filter, if there is one.
	"""

	conditions = sqlalchemy.or_(
		database.Message.sender_id == flask.g.user.id,
		database.Message.receiver_id == flask.g.user.id
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Message
			)
		)

	order_column = getattr(
		database.Message,
		flask.g.json["order"]["by"]
	)

	messages = flask.g.sa_session.execute(
		sqlalchemy.select(database.Message).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(messages), statuses.OK


@message_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all messages sent or received by ``flask.g.user`` that match the
	requested filter, if there is one.

	.. note::
		.. _Received message deletion note:
		The choice of allowing receivers to delete messages may be controversial.
		However, especially in one-on-one chats (which are the only ones currently
		supported), the element of extra privacy outweighs edge cases where being
		able to completely delete messages sent to you could be undesirable.
	"""

	conditions = sqlalchemy.or_(
		database.Message.sender_id == flask.g.user.id,
		database.Message.receiver_id == flask.g.user.id
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Message
			)
		)

	order_column = getattr(
		database.Message,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.Message).
		where(
			database.Message.id.in_(
				sqlalchemy.select(database.Message.id).
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


@message_blueprint.route("", methods=["PUT"])
@validators.validate_json(
	{
		**SEARCH_SCHEMA,
		"values": {
			"type": "dict",
			"minlength": 1,
			"schema": {
				"receiver_id": {
					**ATTR_SCHEMAS["receiver_id"],
					"required": False  # Explicit just in case
				},
				"is_read": {
					**ATTR_SCHEMAS["is_read"],
					"required": False
				},
				"encrypted_session_key": {
					**ATTR_SCHEMAS["encrypted_session_key"],
					"required": False
				},
				"tag": {
					**ATTR_SCHEMAS["tag"],
					"nullable": True,
					"required": False
				},
				"encrypted_content": {
					**ATTR_SCHEMAS["encrypted_content"],
					"required": False
				}
			}
		}
	},
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
def mass_edit() -> typing.Tuple[flask.Response, int]:
	"""Updates all messages sent or received by ``flask.g.user`` that match the
	requested filter, if there is one. If ``'is_read'`` is part of the values to
	update, only received messages are considered.

	.. note::
		_Receiver ID editing note
		Changing the receiver ID originally wasn't allowed, but there are edge
		cases where it could be helpful - like a user migrating to a new account
		where they've kept their previous public key they also use elsewhere.
		And since there isn't any real reason to prevent users from doing it,
		it's now allowed.
	"""

	conditions = (database.Message.receiver_id == flask.g.user.id)

	if "receiver_id" in flask.g.json["values"]:
		validate_user_exists(
			flask.g.json["values"]["receiver_id"],
			flask.g.sa_session,
			flask.g.user
		)

	# Don't change read status of sent messages
	if "is_read" not in flask.g.json["values"]:
		conditions = sqlalchemy.or_(
			conditions,
			database.Message.sender_id == flask.g.user.id
		)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Message
			)
		)

	order_column = getattr(
		database.Message,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(database.Message).
		where(
			database.Message.id.in_(
				sqlalchemy.select(database.Message.id).
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
		values(**flask.g.json["values"]).
		execution_options(synchronize_session="fetch")
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@message_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the message with the requested ``id_``, provided that it exists
	and has been either sent or received by the current user.

	.. seealso::
		The `Received message deletion note`_ for the ``mass_delete``
		endpoint.
	"""

	find_message_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	).delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@message_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json({
	"is_read": {
		**ATTR_SCHEMAS["is_read"],
		"required": True
	},
	**CREATE_EDIT_SCHEMA
})
@authentication.authenticate_via_jwt
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the message with the requested ``id_`` with the requested values,
	provided that it exists and the current user has either sent or receieved it.

	.. seealso::
		The `Receiver ID editing note`_ for the ``mass_edit`` endpoint.
	"""

	message = find_message_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user.id
	)

	if (
		message.sender_id == flask.g.user.id and
		message.is_read != flask.g.json["is_read"]
	):
		raise exceptions.APIMessageCannotChangeIsReadOfSent

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(message, key) != value:
			unchanged = False
			setattr(message, key, value)

	if unchanged:
		raise exceptions.APIMessageUnchanged

	message.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(message), statuses.OK


@message_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the message with the requested ``id_``."""

	return flask.jsonify(
		find_message_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user.id
		)
	), statuses.OK
