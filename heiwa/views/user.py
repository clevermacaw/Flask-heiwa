import datetime
import io
import os
import typing
import uuid

import Crypto.PublicKey.RSA
import flask
import PIL.Image
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
	BASE_PERMISSION_SCHEMA,
	SEARCH_MAX_IN_LIST_LENGTH,
	find_group_by_id,
	find_user_by_id,
	generate_search_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_permission,
	validate_user_exists
)

__all__ = ["user_blueprint"]

user_blueprint = flask.Blueprint(
	"user",
	__name__
)
user_blueprint.json_encoder = encoders.JSONEncoder


# Stored here instead of the validator, since we'll only ever use it once
def check_rsa_public_key_valid(
	field: str,
	value: bytes,
	error: typing.Callable[[str, str], None]
) -> None:
	"""Checks whether or not ``value`` is a valid RSA public key. If not, ``error``
	is called. This function should be used within a Cerberus validator schema.
	"""

	try:
		Crypto.PublicKey.RSA.import_key(value)
	except ValueError:
		error(field, "must be a valid RSA public key")


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
	"is_banned": {
		"type": "boolean"
	},
	"encrypted_private_key": {
		"type": "binary",
		"coerce": "decode_base64",
		"minlength": 624,  # 1024-bit RSA private key, AES-CBC, block size 16
		"maxlength": 2352  # 4096-bit private key, AES-CBC, block size 16
	},
	"public_key": {
		"type": "binary",
		"check_with": check_rsa_public_key_valid,
		"coerce": "decode_base64",
		"minlength": 161,  # 1024-bit RSA public key
		"maxlength": 550  # 4096-bit RSA public key
	},
	"avatar_type": {
		"type": "string",
		"minlength": 3,
		"maxlength": database.User.avatar_type.property.columns[0].type.length
	},
	"name": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.User.name.property.columns[0].type.length
	},
	"status": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.User.status.property.columns[0].type.length
	},
	"extra_fields": {
		"type": "dict",
		"minlength": 1,
		"maxlength": len(flask.current_app.config["USER_EXTRA_FIELDS"]),
		"schema": {
			key: {
				**value,
				"nullable": False,
				"required": False
			}
			for key, value in flask.current_app.config["USER_EXTRA_FIELDS"].items()
		}
	},
	"followee_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"follower_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"post_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"thread_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	}
}

SEARCH_SCHEMA = generate_search_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"edit_count",
		"follower_count",
		"followee_count",
		"post_count",
		"thread_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"],
	"followee_count": ATTR_SCHEMAS["followee_count"],
	"follower_count": ATTR_SCHEMAS["follower_count"],
	"post_count": ATTR_SCHEMAS["post_count"],
	"thread_count": ATTR_SCHEMAS["thread_count"]
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
			"is_banned": ATTR_SCHEMAS["is_banned"],
			"public_key": ATTR_SCHEMAS["public_key"],
			"avatar_type": {
				**ATTR_SCHEMAS["avatar_type"],
				"nullable": True
			},
			"name": {
				**ATTR_SCHEMAS["name"],
				"nullable": True
			},
			"status": {
				**ATTR_SCHEMAS["status"],
				"nullable": True
			},
			"followee_count": ATTR_SCHEMAS["followee_count"],
			"follower_count": ATTR_SCHEMAS["follower_count"],
			"post_count": ATTR_SCHEMAS["post_count"],
			"thread_count": ATTR_SCHEMAS["thread_count"]
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
			"public_key": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["public_key"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"avatar_type": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["avatar_type"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"name": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["name"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"status": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["status"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"followee_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["followee_count"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"follower_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["follower_count"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"post_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["post_count"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"thread_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["thread_count"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			}
		},
		"maxlength": 1
	},
	"$re": {
		"type": "dict",
		"schema": {
			"avatar_type": {
				**ATTR_SCHEMAS["avatar_type"],
				"check_with": "is_valid_regex"
			},
			"name": {
				**ATTR_SCHEMAS["name"],
				"check_with": "is_valid_regex"
			},
			"status": {
				**ATTR_SCHEMAS["status"],
				"check_with": "is_valid_regex"
			}
		},
		"maxlength": 1
	}
})


def generate_avatar_response(user: database.User) -> flask.Response:
	"""Returns the given ``user``'s avatar as an attachment contained within
	a ``flask.Response``.
	"""

	return flask.send_file(
		user.avatar_location,
		mimetype=user.avatar_type,
		as_attachment=True,
		download_name=user.avatar_filename,
		last_modified=os.path.getmtime(user.avatar_location)
	)


def get_user_self_or_id(
	id_: typing.Union[None, uuid.UUID],
	session: sqlalchemy.orm.Session
) -> database.User:
	"""If the provided ``id_`` is ``None``, ``flask.g.user`` will be returned.
	Otherwise, the user with the given ``id_`` is returned.
	"""

	if id_ is not None:
		user = find_user_by_id(
			id_,
			session,
			flask.g.user
		)
	else:
		user = flask.g.user

	return user


@user_blueprint.route("/users", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all users that match the requested filter, if there is one."""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.User
			)
		)

	order_column = getattr(
		database.User,
		flask.g.json["order"]["by"]
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			database.User.get(
				flask.g.user,
				flask.g.sa_session,
				conditions=conditions,
				order_by=(
					sqlalchemy.asc(order_column)
					if flask.g.json["order"]["asc"]
					else sqlalchemy.desc(order_column)
				),
				limit=flask.g.json["limit"],
				offset=flask.g.json["offset"]
			)
		).scalars().all()
	), statuses.OK


@user_blueprint.route("/users", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.User)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all users that match the requested filter if there is one, and
	``flask.g.user`` has permission to delete.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.User
			)
		)

	order_column = getattr(
		database.User,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.User).
		where(
			database.User.id.in_(
				database.User.get(
					flask.g.user,
					flask.g.sa_session,
					additional_actions=["delete"],
					conditions=conditions,
					order_by=(
						sqlalchemy.asc(order_column)
						if flask.g.json["order"]["asc"]
						else sqlalchemy.desc(order_column)
					),
					limit=flask.g.json["limit"],
					offset=flask.g.json["offset"]
				)
			)
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users", methods=["PUT"])
@validators.validate_json(
	{
		**SEARCH_SCHEMA,
		"values": {
			"type": "dict",
			"minlength": 1,
			"schema": {
				"name": {
					**ATTR_SCHEMAS["name"],
					"nullable": True,
					"required": False
				},
				"status": {
					**ATTR_SCHEMAS["status"],
					"nullable": True,
					"required": False
				},
				"extra_fields": {
					**ATTR_SCHEMAS["extra_fields"],
					"nullable": True,
					"required": False,
				},
				"encrypted_private_key": {
					**ATTR_SCHEMAS["encrypted_private_key"],
					"nullable": True,
					"required": False
				},
				"public_key": {
					**ATTR_SCHEMAS["public_key"],
					"nullable": True,
					"required": False
				}
			}
		}
	},
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.User)
def mass_edit() -> typing.Tuple[flask.Response, int]:
	"""Updates all users that match the requested filter if there is one, and
	``flask.g.user`` has permission to edit.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.User
			)
		)

	order_column = getattr(
		database.User,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(database.User).
		where(
			database.User.id.in_(
				database.User.get(
					flask.g.user,
					flask.g.sa_session,
					additional_actions=["edit"],
					conditions=conditions,
					order_by=(
						sqlalchemy.asc(order_column)
						if flask.g.json["order"]["asc"]
						else sqlalchemy.desc(order_column)
					),
					limit=flask.g.json["limit"],
					offset=flask.g.json["offset"]
				)
			)
		).
		values(**flask.g.json["values"])
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route(
	"/users/<uuid:id_>",
	methods=["DELETE"]
)
@user_blueprint.route(
	"/self",
	defaults={"id_": None},
	methods=["DELETE"]
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.User)
def delete(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the user with the requested ``id_``, or ``flask.g.user`` if it's
	``None``.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"delete",
		user
	)

	user.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>", methods=["PUT"])
@user_blueprint.route(
	"/self",
	defaults={"id_": None},
	methods=["PUT"]
)
@validators.validate_json({
	"name": {
		**ATTR_SCHEMAS["name"],
		"nullable": True,
		"required": True
	},
	"status": {
		**ATTR_SCHEMAS["status"],
		"nullable": True,
		"required": True
	},
	"extra_fields": {
		**ATTR_SCHEMAS["extra_fields"],
		"nullable": True,
		"required": False,
	},
	"encrypted_private_key": {
		**ATTR_SCHEMAS["encrypted_private_key"],
		"nullable": True,
		"required": True
	},
	"public_key": {
		**ATTR_SCHEMAS["public_key"],
		"nullable": True,
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit", database.User)
def edit(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Updates the user with the requested ``id_`` (or ``flask.g.user`` if it's
	``None``) with the requested values.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit",
		user
	)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(user, key) != value:
			unchanged = False
			setattr(user, key, value)

	if unchanged:
		raise exceptions.APIUserUnchanged

	user.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(user), statuses.OK


@user_blueprint.route("/users/<uuid:id_>", methods=["GET"])
@user_blueprint.route(
	"/self",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def view(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the requested ``id_``, or ``flask.g.user`` if it's
	``None``.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	return flask.jsonify(user), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/authorized-actions", methods=["GET"])
@user_blueprint.route(
	"/self/authorized-actions",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def authorized_actions_user(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on the
	user with the requested ``id_``, or themselves if it's ``None``.
	"""

	return flask.jsonify(
		get_user_self_or_id(
			id_,
			flask.g.sa_session
		).get_allowed_instance_actions(flask.g.user)
	)


@user_blueprint.route("/users/<uuid:id_>/avatar", methods=["DELETE"])
@user_blueprint.route(
	"/self/avatar",
	defaults={"id_": None},
	methods=["DELETE"]
)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.User)
def delete_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the avatar of the user with the requested ``id_``, or
	``flask.g.user``'s if it's ``None``.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit",
		user
	)

	if user.avatar is None:
		raise exceptions.APIUserAvatarNotFound

	user.avatar = None

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/avatar", methods=["PUT"])
@user_blueprint.route(
	"/self/avatar",
	defaults={"id_": None},
	methods=["PUT"]
)
@validators.validate_json({
	"avatar": {
		"type": "binary",
		"coerce": "decode_base64",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit", database.User)
def edit_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Sets the avatar of the user with the requested ``id_`` (or
	``flask.g.user``'s, if it's ``None``) to the decoded base64 value within the
	``avatar`` request body key.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit",
		user
	)

	if (
		len(flask.g.json["avatar"])
		> flask.current_app.config["USER_MAX_AVATAR_SIZE"]
	):
		raise exceptions.APIUserAvatarTooLarge(
			flask.current_app.config["USER_MAX_AVATAR_SIZE"]
		)

	try:
		image = PIL.Image.open(io.BytesIO(flask.g.json["avatar"]))
		image.verify()
	except OSError:
		raise exceptions.APIUserAvatarInvalid

	avatar_type = PIL.Image.MIME[image.format]

	if avatar_type not in flask.current_app.config["USER_AVATAR_TYPES"]:
		raise exceptions.APIUserAvatarNotAllowedType(avatar_type)

	if user.avatar is None:
		status = statuses.CREATED
	else:
		status = statuses.OK

	user.avatar_type = avatar_type
	user.avatar = flask.g.json["avatar"]
	user.edited()

	flask.g.sa_session.commit()

	return generate_avatar_response(user), status


@user_blueprint.route("/users/<uuid:id_>/avatar", methods=["GET"])
@user_blueprint.route(
	"/self/avatar",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def view_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns a non-base64 encoded version of the avatar of the user with the
	requested ``id_``, or ``flask.g.user``'s if it's ``None``.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	if user.avatar is None:
		return flask.jsonify(None), statuses.OK

	return generate_avatar_response(user), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/ban", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_ban", database.User)
def delete_ban(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the user with the requested ``id_``'s ban."""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_ban",
		user
	)

	if not user.is_banned:
		raise exceptions.APIUserBanNotFound

	user.remove_ban()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/ban", methods=["PUT"])
@validators.validate_json({
	"expiration_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime",
		"required": False
	},
	"reason": {
		"type": "string",
		"minlength": 2,
		"maxlength": 65536,
		"nullable": True,
		"required": False
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_ban", database.User)
def edit_ban(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Bans the user with the requested ``id_``. The ``expiration_timestamp`` is
	required, a ``reason``, while recommended, is not.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_ban",
		user
	)

	if user.is_banned:
		if (
			datetime.datetime.now(tz=datetime.timezone.utc)
			> user.ban.expiration_timestamp
		):
			user.remove_ban()

		if (
			user.ban.expiration_timestamp == flask.g.json["expiration_timestamp"] and
			user.ban.reason == flask.g.json["reason"]
		):
			raise exceptions.APIUserBanUnchanged

	if (
		datetime.datetime.now(tz=flask.g.json["expiration_timestamp"].tzinfo)
		> flask.g.json["expiration_timestamp"]
	):
		raise exceptions.APIUserBanAlreadyExpired

	if user.is_banned:
		user.ban.expiration_timestamp = flask.g.json["expiration_timestamp"]
		user.ban.reason = flask.g.json["reason"]

		user.ban.edited()

		status = statuses.OK
	else:
		user.create_ban(
			expiration_timestamp=flask.g.json["expiration_timestamp"],
			reason=flask.g.json["reason"]
		)

		status = statuses.CREATED

	flask.g.sa_session.commit()

	return flask.jsonify(user.ban), status


@user_blueprint.route("/users/<uuid:id_>/ban", methods=["GET"])
@user_blueprint.route(
	"/self/ban",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_ban", database.User)
def view_ban(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the requested ``id_``'s ban. (or ``flask.g.user``'s,
	if it's ``None``)
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_ban",
		user
	)

	if (
		datetime.datetime.now(tz=datetime.timezone.utc)
		> user.ban.expiration_timestamp
	):
		user.remove_ban()

	return flask.jsonify(user.ban), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/block", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_block", database.User)
def create_block(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a block from ``flask.g.user`` for the user with the requested
	``id_``. If ``flask.g.user`` follows them, that follow is automatically
	removed.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_block",
		user
	)

	if (
		flask.g.sa_session.execute(
			sqlalchemy.select(database.user_blocks).
			where(
				sqlalchemy.and_(
					database.user_blocks.c.blocker_id == flask.g.user.id,
					database.user_blocks.c.blockee_id == user.id
				)
			)
		).scalars().one_or_none()
	) is not None:
		raise exceptions.APIUserBlockAlreadyExists

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.user_follows).
		where(
			sqlalchemy.and_(
				database.user_follows.c.follower_id == flask.g.user.id,
				database.user_follows.c.followee_id == user.id
			)
		)
	)

	flask.g.sa_session.execute(
		sqlalchemy.insert(database.user_blocks).
		values(
			blocker_id=flask.g.user.id,
			blockee_id=user.id
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/block", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_block", database.User)
def delete_block(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Removes ``flask.g.user``'s block for the user with the requested
	``id_``.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_block",
		user
	)

	existing_block = flask.g.sa_session.execute(
		sqlalchemy.select(database.user_blocks).
		where(
			sqlalchemy.and_(
				database.user_blocks.c.blocker_id == flask.g.user.id,
				database.user_blocks.c.blockee_id == user.id
			)
		)
	).scalars().one_or_none()

	if existing_block is None:
		raise exceptions.APIUserBlockNotFound

	flask.g.sa_session.delete(existing_block)
	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/block", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def view_block(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not ``flask.g.user`` has blocked the user with the
	requested ``id_``.
	"""

	validate_user_exists(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			sqlalchemy.select(database.user_blocks.c.blocker_id).
			where(
				sqlalchemy.and_(
					database.user_blocks.c.blocker_id == flask.g.user.id,
					database.user_blocks.c.blockee_id == id_
				)
			).
			exists().
			select()
		).scalars().one()
	), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/followers", methods=["GET"])
@user_blueprint.route(
	"/self/followers",
	defaults={"id_": None},
	methods=["GET"]
)
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def list_followers(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Lists all followers of the user with the requested ``id_`` (or
	``flask.g.user``'s, if it's ``None``) that match the requested filter, if
	there is one.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	conditions = (
		database.User.id.in_(
			sqlalchemy.select(database.user_follows.c.followee_id).
			where(
				database.user_follows.c.follower_id == user.id
			)
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.User
			)
		)

	order_column = getattr(
		database.User,
		flask.g.json["order"]["by"]
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			database.User.get(
				flask.g.user,
				flask.g.sa_session,
				conditions=conditions,
				order_by=(
					sqlalchemy.asc(order_column)
					if flask.g.json["order"]["asc"]
					else sqlalchemy.desc(order_column)
				),
				limit=flask.g.json["limit"],
				offset=flask.g.json["offset"]
			)
		).scalars().all()
	), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/followees", methods=["GET"])
@user_blueprint.route(
	"/self/followees",
	defaults={"id_": None},
	methods=["GET"]
)
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def list_followees(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Lists all followees of the user with the requested ``id_`` (or
	``flask.g.user``'s, if it's ``None``) that match the requested filter, if
	there is one.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	conditions = (
		database.User.id.in_(
			sqlalchemy.select(database.user_follows.c.follower_id).
			where(
				database.user_follows.c.followee_id == user.id
			)
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.User
			)
		)

	order_column = getattr(
		database.User,
		flask.g.json["order"]["by"]
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			database.User.get(
				flask.g.user,
				flask.g.sa_session,
				conditions=conditions,
				order_by=(
					sqlalchemy.asc(order_column)
					if flask.g.json["order"]["asc"]
					else sqlalchemy.desc(order_column)
				),
				limit=flask.g.json["limit"],
				offset=flask.g.json["offset"]
			)
		).scalars().all()
	), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/follow", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_follow", database.User)
def create_follow(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a follow from ``flask.g.user`` for the user with the requested
	``id_``.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_follow",
		user
	)

	if (
		flask.g.sa_session.execute(
			sqlalchemy.select(database.user_follows).
			where(
				sqlalchemy.and_(
					database.user_follows.c.follower_id == flask.g.user.id,
					database.user_follows.c.followee_id == user.id
				)
			)
		).scalars().one_or_none()
	) is not None:
		raise exceptions.APIUserFollowAlreadyExists

	flask.g.sa_session.execute(
		sqlalchemy.insert(database.user_follows).
		values(
			follower_id=flask.g.user.id,
			followee_id=user.id
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/follow", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_follow", database.User)
def delete_follow(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Removes ``flask.g.user``'s follow for the user with the requested
	``id_``.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_follow",
		user
	)

	existing_follow = flask.g.sa_session.execute(
		sqlalchemy.select(database.user_follows).
		where(
			sqlalchemy.and_(
				database.user_follows.c.follower_id == flask.g.user.id,
				database.user_follows.c.followee_id == user.id
			)
		)
	).scalars().one_or_none()

	if existing_follow is None:
		raise exceptions.APIUserFollowNotFound

	flask.g.sa_session.delete(existing_follow)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/follow", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.User)
def view_follow(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not ``flask.g.user`` has followed the user with the
	requested ``id_``.
	"""

	validate_user_exists(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			sqlalchemy.select(database.user_follows.c.follower_id).
			where(
				sqlalchemy.and_(
					database.user_follows.c.follower_id == flask.g.user.id,
					database.user_follows.c.followee_id == id_
				)
			).
			exists().
			select()
		).scalars().one()
	), statuses.OK


@user_blueprint.route("/users/<uuid:id_>/groups", methods=["GET"])
@user_blueprint.route(
	"/self/groups",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_groups", database.User)
def list_groups(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the requested ``id_``'s (or ``flask.g.user``'s, if
	it's ``None``) assigned group IDs.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	group_ids = flask.g.sa_session.execute(
		sqlalchemy.select(database.Group.id).
		where(
			database.Group.id.in_(
				sqlalchemy.select(database.user_groups.c.group_id).
				where(database.user_groups.c.user_id == user.id)
			)
		).
		order_by(
			sqlalchemy.asc(database.Group.level)
		)
	).scalars().all()

	return flask.jsonify(group_ids), statuses.OK


@user_blueprint.route(
	"/users/<uuid:user_id>/groups/<uuid:group_id>",
	methods=["PUT"]
)
@user_blueprint.route(
	"/self/groups/<uuid:group_id>",
	defaults={"user_id": None},
	methods=["PUT"]
)
@authentication.authenticate_via_jwt
@requires_permission("edit_group", database.User)
def add_group(
	user_id: typing.Union[None, uuid.UUID],
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Adds the group with the requested ``group_id`` to the user with the
	requested ``user_id``. (or ``flask.g.user``, if it's ``None``)
	"""

	user = get_user_self_or_id(
		user_id,
		flask.g.sa_session
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session,
		flask.g.user
	)

	user.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_group",
		user
	)

	if not flask.g.sa_session.execute(
		sqlalchemy.select(database.user_groups.c.user_id).
		where(
			sqlalchemy.and_(
				database.user_groups.c.user_id == user.id,
				database.user_groups.c.group_id == group.id
			)
		).
		exists().
		select()
	).scalars().one_or_none():
		raise exceptions.APIUserGroupAlreadyAdded

	flask.g.sa_session.execute(
		sqlalchemy.insert(database.user_groups).
		values(
			user_id=user.id,
			group_id=group.id
		)
	)

	user.reparse_permissions()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route(
	"/users/<uuid:user_id>/groups/<uuid:group_id>",
	methods=["DELETE"]
)
@user_blueprint.route(
	"/self/groups/<uuid:group_id>",
	defaults={"user_id": None},
	methods=["DELETE"]
)
@authentication.authenticate_via_jwt
@requires_permission("edit_group", database.User)
def delete_group(
	user_id: typing.Union[None, uuid.UUID],
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the group with the requested ``group_id`` from the user with the
	requested ``user_id``'s groups. (or ``flask.g.user``'s, if it's ``None``)
	"""

	user = get_user_self_or_id(
		user_id,
		flask.g.sa_session
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session,
		flask.g.user
	)

	user.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_group",
		user
	)

	existing_group_association = flask.g.sa_session.execute(
		sqlalchemy.select(database.user_groups.c.user_id).
		where(
			sqlalchemy.and_(
				database.user_groups.c.user_id == user.id,
				database.user_groups.c.group_id == group.id
			)
		)
	).scalars().one_or_none()

	if existing_group_association is None:
		raise exceptions.APIUserGroupNotAdded

	if "*" in group.default_for:
		found_default_group = False

		for user_group in user.groups:
			if (
				user_group.id != group.id and
				"*" in user_group.default_for
			):
				found_default_group = True

				break

		if not found_default_group:
			raise exceptions.APIUserCannotRemoveLastDefaultGroup

	flask.g.sa_session.delete(existing_group_association)

	user.reparse_permissions()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/permissions", methods=["PUT"])
@user_blueprint.route(
	"/self/permissions",
	defaults={"id_": None},
	methods=["PUT"]
)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", database.User)
def delete_permissions(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the user with the requested ``id_``'s (or ``flask.g.user``'s,
	if it's ``None``) permissions.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_permissions",
		user
	)

	if user.permissions is None:
		raise exceptions.APIUserPermissionsNotFound

	user.permissions.delete()

	return flask.jsonify({}), statuses.NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/permissions", methods=["PUT"])
@user_blueprint.route(
	"/self/permissions",
	defaults={"id_": None},
	methods=["PUT"]
)
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", database.User)
def edit_permissions(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Updates the user with the requested ``id_``'s (or ``flask.g.user``, if it's
	``None``) permissions, or creates them if there are none.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_permissions",
		user
	)

	if user.permissions is None:
		database.UserPermissions.create(
			flask.g.sa_session,
			user_id=user.id,
			**flask.g.json
		)

		status = statuses.CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(user.permissions, key) is not value:
				unchanged = False
				setattr(user.permissions, key, value)

		if unchanged:
			raise exceptions.APIUserPermissionsUnchanged

		user.permissions.edited()

		status = statuses.OK

	flask.g.sa_session.commit()

	return flask.jsonify(user.permissions), status


@user_blueprint.route("/users/<uuid:id_>/permissions", methods=["GET"])
@user_blueprint.route(
	"/self/permissions",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions", database.User)
def view_permissions(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the requested ``id_``'s (or ``flask.g.user``'s,
	if it's ``None``) permissions.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_permissions",
		user
	)

	return flask.jsonify(user.permissions), statuses.OK


@user_blueprint.route("/users/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on
	users without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		database.User.get_allowed_static_actions(flask.g.user)
	), statuses.OK
