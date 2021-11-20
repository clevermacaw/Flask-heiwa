import base64
import binascii
import datetime
import os
import typing
import uuid

import flask
import magic
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
	PERMISSION_KEY_SCHEMA,
	find_group_by_id,
	find_user_by_id,
	generate_list_schema,
	generate_search_schema_registry,
	get_endpoint_limit,
	parse_search,
	requires_permission,
	validate_permission
)

__all__ = ["user_blueprint"]

user_blueprint = flask.Blueprint(
	"user",
	__name__
)
user_blueprint.json_encoder = encoders.JSONEncoder

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
	"is_banned": {
		"type": "boolean"
	},
	"avatar_type": {
		"type": "string",
		"minlength": 3,
		"maxlength": 256
	},
	"name": {
		"type": "string",
		"minlength": 1,
		"maxlength": 128
	},
	"status": {
		"type": "string",
		"minlength": 1,
		"maxlength": 65536
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
	"forum_count": {
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

LIST_SCHEMA = generate_list_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"follower_count",
		"followee_count",
		"forum_count",
		"post_count",
		"thread_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"followee_count": ATTR_SCHEMAS["followee_count"],
	"follower_count": ATTR_SCHEMAS["follower_count"],
	"forum_count": ATTR_SCHEMAS["forum_count"],
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
			"is_banned": ATTR_SCHEMAS["is_banned"],
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
			"forum_count": ATTR_SCHEMAS["forum_count"],
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
				"minlength": 1,
				"maxlength": 32
			},
			"creation_timestamp": {
				"type": "list",
				"schema": ATTR_SCHEMAS["creation_timestamp"],
				"minlength": 1,
				"maxlength": 32
			},
			"edit_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["edit_timestamp"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"avatar_type": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["avatar_type"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"name": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["name"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"status": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["status"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"followee_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["followee_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"follower_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["follower_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"forum_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["forum_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"post_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["post_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"thread_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["thread_count"],
				"minlength": 1,
				"maxlength": 32
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


def generate_avatar_response(user: models.User) -> flask.Response:
	"""Returns the given `user`'s avatar as a file."""

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
) -> models.User:
	"""If the provided `id` is `None`, the current `flask.g.user` will
	be returned. Otherwise, the user with the given ID is returned.
	"""

	if id_ is not None:
		user = find_user_by_id(
			id_,
			session
		)
	else:
		user = flask.g.user

	return user


@user_blueprint.route("/users", methods=["GET"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all the available users.

	Idempotent.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.User
			)
		)

	order_column = getattr(
		models.User,
		flask.g.json["order"]["by"]
	)

	users = flask.g.sa_session.execute(
		sqlalchemy.select(models.User).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(users), helpers.STATUS_OK


@user_blueprint.route("/users", methods=["DELETE"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all users that match the given conditions.

	Not idempotent.
	"""

	conditions = sqlalchemy.or_(
		models.User.id == flask.g.user.id,
		(
			sqlalchemy.select(models.Group.level).
			where(
				models.Group.users.any(id=models.User.id)
			).
			order_by(
				sqlalchemy.desc(models.Group.level)
			).
			limit(1)
		) < flask.g.user.highest_group.level
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.User
			)
		)

	order_column = getattr(
		models.User,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(
			sqlalchemy.select(models.User).
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
@requires_permission(
	lambda: (
		"delete"
		if flask.request.view_args["id_"] is not None
		else "delete_self"
	),
	models.User
)
@limiter.limiter.limit(get_endpoint_limit)
def delete(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the user with the given ID.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"delete" if id_ is not None else "delete_self",
		user
	)

	user.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


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
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def edit(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Updates the user with the given ID with the provided name and status.

	Idempotent.
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
		raise exceptions.APIUserUnchanged(user.id)

	user.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(user), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>", methods=["GET"])
@user_blueprint.route(
	"/self",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the given ID.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	return flask.jsonify(user), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/authorized-actions", methods=["GET"])
@user_blueprint.route(
	"/self/authorized-actions",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def authorized_actions_user(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that the current `flask.g.user` is authorized to
	perform on the given user. This will only be done if they at least have
	permission to view it.

	Idempotent.
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
@requires_permission("edit", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def delete_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the given user's avatar.

	Idempotent.
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
		raise exceptions.APIUserAvatarNotFound(user.id)

	user.avatar = None

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/avatar", methods=["PUT"])
@user_blueprint.route(
	"/self/avatar",
	defaults={"id_": None},
	methods=["PUT"]
)
@validators.validate_json({
	"b64_avatar": {
		"type": "string",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def edit_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Updates the given user's avatar with the decoded base64 file.

	Idempotent.
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

	if len(flask.g.json["b64_avatar"]) > (
		4 * round(flask.current_app.config["USER_MAX_AVATAR_SIZE"] / 3)
	):
		raise exceptions.APIUserAvatarTooLarge(
			flask.current_app.config["USER_MAX_AVATAR_SIZE"]
		)

	try:
		avatar = base64.b64decode(
			flask.g.json["b64_avatar"],
			validate=True
		)
	except (ValueError, binascii.Error):  # TODO: PEP 604
		raise exceptions.APIUserAvatarInvalid

	avatar_type = magic.Magic(mime=True).from_buffer(avatar)

	if avatar_type not in flask.current_app.config["USER_AVATAR_TYPES"]:
		raise exceptions.APIUserAvatarNotAllowedType(avatar_type)

	if user.avatar is None:
		status = helpers.STATUS_CREATED
	else:
		status = helpers.STATUS_OK

	user.avatar_type = avatar_type
	user.avatar = avatar
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
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view_avatar(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the given user's avatar. Not encoded in base64.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	if user.avatar is None:
		return flask.jsonify(None), helpers.STATUS_OK

	return generate_avatar_response(user), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/ban", methods=["PUT"])
@validators.validate_json({
	"ban": {
		"type": "boolean",
		"makes_required": {
			"expiration_timestamp": True,
			"reason": True
		},
		"required": True
	},
	"expiration_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime",
		"dependencies": {
			"ban": True
		},
		"required": False
	},
	"reason": {
		"type": "string",
		"minlength": 1,
		"maxlength": 65536,
		"nullable": True,
		"dependencies": {
			"ban": True
		},
		"required": False
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_ban", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def ban(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Bans the user with the given ID. Requires an expiration timestamp,
	the reason is optional.

	Idempotent.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_ban",
		user
	)

	if (
		flask.g.json["ban"] is user.is_banned and (
			(
				user.is_banned and
				user.ban.expiration_timestamp == flask.g.json["expiration_timestamp"] and
				user.ban.reason == flask.g.json["reason"]
			) or
			not user.is_banned
		)
	):
		raise exceptions.APIUserBanUnchanged(user.ban)

	if (
		flask.g.json["ban"] and
		datetime.datetime.now(tz=flask.g.json["expiration_timestamp"].tzinfo)
		> flask.g.json["expiration_timestamp"]
	):
		raise exceptions.APIUserBanAlreadyExpired(
			flask.g.json["expiration_timestamp"]
		)

	status = helpers.STATUS_OK

	if flask.g.json["ban"]:
		if user.is_banned:
			user.ban.expiration_timestamp = flask.g.json["expiration_timestamp"]
			user.ban.reason = flask.g.json["reason"]

			user.ban.edited()
		else:
			user.create_ban(
				expiration_timestamp=flask.g.json["expiration_timestamp"],
				reason=flask.g.json["reason"]
			)

			status = helpers.STATUS_CREATED
	else:
		user.remove_ban()

	flask.g.sa_session.commit()

	return flask.jsonify(user.ban), status


@user_blueprint.route("/users/<uuid:id_>/ban", methods=["GET"])
@user_blueprint.route(
	"/self/ban",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_ban", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view_ban(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the given ID's ban.

	Idempotent.
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

	return flask.jsonify(user.ban), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/block", methods=["PUT"])
@validators.validate_json({
	"block": {
		"type": "boolean",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_block", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def edit_block(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Blocks the user with the given ID. If `flask.g.user` is a follower of
	`user`, they're automatically removed.

	Idempotent.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_block",
		user
	)

	existing_block = flask.g.sa_session.execute(
		sqlalchemy.select(models.user_blocks).
		where(
			sqlalchemy.and_(
				models.user_blocks.c.blocker_id == flask.g.user.id,
				models.user_blocks.c.blockee_id == user.id
			)
		)
	).scalars().one()

	if flask.g.json["block"] is (existing_block is not None):
		raise exceptions.APIUserBlockUnchanged(flask.g.json["block"])

	if flask.g.json["block"]:
		flask.g.sa_session.execute(
			sqlalchemy.delete(models.user_follows).
			where(
				sqlalchemy.and_(
					models.user_follows.c.follower_id == flask.g.user.id,
					models.user_follows.c.followee_id == user.id
				)
			)
		)

		flask.g.sa_session.execute(
			sqlalchemy.insert(models.user_blocks).
			values(
				blocker_id=flask.g.user.id,
				blockee_id=user.id
			)
		)
	else:
		flask.g.sa_session.delete(existing_block)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/block", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view_block(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not the current user has blocked the user with
	the given ID.

	Idempotent.
	"""

	return flask.jsonify({
		"is_blockee": flask.g.sa_session.execute(
			sqlalchemy.select(models.user_blocks.c.blocker_id).
			where(
				sqlalchemy.and_(
					models.user_blocks.c.blocker_id == flask.g.user.id,
					models.user_blocks.c.blockee_id == find_user_by_id(
						id_,
						flask.g.sa_session
					).id
				)
			).
			exists().
			select()
		).scalars().one()
	}), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/followers", methods=["GET"])
@user_blueprint.route(
	"/self/followers",
	defaults={"id_": None},
	methods=["GET"]
)
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def list_followers(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Lists all the available followers of the user with the given ID.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	conditions = models.User.followees.any(
		id_=user.id
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.User
			)
		)

	order_column = getattr(
		models.User,
		flask.g.json["order"]["by"]
	)

	followers = flask.g.sa_session.execute(
		sqlalchemy.select(models.User).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(followers), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/followees", methods=["GET"])
@user_blueprint.route(
	"/self/followees",
	defaults={"id_": None},
	methods=["GET"]
)
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def list_followees(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Lists all the available users the user with the given ID follows.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	conditions = models.User.followers.any(
		id_=user.id
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.User
			)
		)

	order_column = getattr(
		models.User,
		flask.g.json["order"]["by"]
	)

	followees = flask.g.sa_session.execute(
		sqlalchemy.select(models.User).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(followees), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/follow", methods=["PUT"])
@validators.validate_json({
	"follow": {
		"type": "boolean",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_follow", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def edit_follow(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Follows / unfollows the user with the given ID.

	Idempotent.
	"""

	user = find_user_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_follow",
		user
	)

	existing_follow = flask.g.sa_session.execute(
		sqlalchemy.select(models.user_follows).
		where(
			sqlalchemy.and_(
				models.user_follows.c.follower_id == flask.g.user.id,
				models.user_follows.c.followee_id == user.id
			)
		)
	).scalars().one()

	if flask.g.json["follow"] is (existing_follow is not None):
		raise exceptions.APIUserFollowUnchanged(flask.g.json["follow"])

	if flask.g.json["follow"]:
		flask.g.sa_session.execute(
			sqlalchemy.insert(models.user_follows).
			values(
				follower_id=flask.g.user.id,
				followee_id=user.id
			)
		)
	else:
		flask.g.sa_session.delete(existing_follow)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/follow", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view_follow(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not the current user is a follower of the user
	with the given ID.

	Idempotent.
	"""

	return flask.jsonify({
		"is_followee": flask.g.sa_session.execute(
			sqlalchemy.select(models.user_follows.c.follower_id).
			where(
				sqlalchemy.and_(
					models.user_follows.c.follower_id == flask.g.user.id,
					models.user_follows.c.followee_id == find_user_by_id(
						id_,
						flask.g.sa_session
					).id
				)
			).
			exists().
			select()
		).scalars().one()
	}), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/groups", methods=["GET"])
@user_blueprint.route(
	"/self/groups",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_groups", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def list_groups(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the groups this user has.

	Idempotent.
	"""

	user = get_user_self_or_id(
		id_,
		flask.g.sa_session
	)

	group_ids = flask.g.sa_session.execute(
		sqlalchemy.select(models.Group.id).
		where(models.Group.users.any(id=user.id)).
		order_by(
			sqlalchemy.asc(models.Group.level)
		)
	).scalars().all()

	return flask.jsonify(group_ids), helpers.STATUS_OK


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
@requires_permission("edit_group", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def add_group(
	user_id: typing.Union[None, uuid.UUID],
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Adds a group to this user.

	Idempotent.
	"""

	user = get_user_self_or_id(
		user_id,
		flask.g.sa_session
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session
	)

	user.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_group",
		user
	)

	if not flask.g.sa_session.execute(
		sqlalchemy.select(models.user_groups.c.user_id).
		where(
			sqlalchemy.and_(
				models.user_groups.c.user_id == user.id,
				models.user_groups.c.group_id == group.id
			)
		).
		exists().
		select()
	).scalars().one():
		raise exceptions.APIUserGroupAlreadyAdded(group.id)

	flask.g.sa_session.execute(
		sqlalchemy.insert(models.user_groups).
		values(
			user_id=user.id,
			group_id=group.id
		)
	)

	user.reparse_permissions()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


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
@requires_permission("edit_group", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def delete_group(
	user_id: typing.Union[None, uuid.UUID],
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Removes a group from this user.

	Idempotent.
	"""

	user = get_user_self_or_id(
		user_id,
		flask.g.sa_session
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session
	)

	user.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_group",
		user
	)

	existing_group_association = flask.g.sa_session.execute(
		sqlalchemy.select(models.user_groups.c.user_id).
		where(
			sqlalchemy.and_(
				models.user_groups.c.user_id == user.id,
				models.user_groups.c.group_id == group.id
			)
		)
	).scalars().one()

	if existing_group_association is None:
		raise exceptions.APIUserGroupNotAdded(group.id)

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

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@user_blueprint.route("/users/<uuid:id_>/permissions", methods=["GET"])
@user_blueprint.route(
	"/self/permissions",
	defaults={"id_": None},
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def view_permissions(
	id_: typing.Union[None, uuid.UUID]
) -> typing.Tuple[flask.Response, int]:
	"""Returns the user with the given ID's specific permissions.

	Idempotent.
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

	return flask.jsonify(user.permissions), helpers.STATUS_OK


@user_blueprint.route("/users/<uuid:id_>/permissions", methods=["PUT"])
@user_blueprint.route(
	"/self/permissions",
	defaults={"id_": None},
	methods=["PUT"]
)
@validators.validate_json({
	"forum_create": PERMISSION_KEY_SCHEMA,
	"forum_delete_own": PERMISSION_KEY_SCHEMA,
	"forum_delete_any": PERMISSION_KEY_SCHEMA,
	"forum_edit_own": PERMISSION_KEY_SCHEMA,
	"forum_edit_any": PERMISSION_KEY_SCHEMA,
	"forum_merge_own": PERMISSION_KEY_SCHEMA,
	"forum_merge_any": PERMISSION_KEY_SCHEMA,
	"forum_move_own": PERMISSION_KEY_SCHEMA,
	"forum_move_any": PERMISSION_KEY_SCHEMA,
	"forum_view": PERMISSION_KEY_SCHEMA,
	"group_create": PERMISSION_KEY_SCHEMA,
	"group_delete": PERMISSION_KEY_SCHEMA,
	"group_edit": PERMISSION_KEY_SCHEMA,
	"group_edit_permissions": PERMISSION_KEY_SCHEMA,
	"post_create": PERMISSION_KEY_SCHEMA,
	"post_delete_own": PERMISSION_KEY_SCHEMA,
	"post_delete_any": PERMISSION_KEY_SCHEMA,
	"post_edit_own": PERMISSION_KEY_SCHEMA,
	"post_edit_any": PERMISSION_KEY_SCHEMA,
	"post_edit_vote": PERMISSION_KEY_SCHEMA,
	"post_move_own": PERMISSION_KEY_SCHEMA,
	"post_move_any": PERMISSION_KEY_SCHEMA,
	"post_view": PERMISSION_KEY_SCHEMA,
	"thread_create": PERMISSION_KEY_SCHEMA,
	"thread_delete_own": PERMISSION_KEY_SCHEMA,
	"thread_delete_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_own": PERMISSION_KEY_SCHEMA,
	"thread_edit_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_lock_own": PERMISSION_KEY_SCHEMA,
	"thread_edit_lock_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_pin": PERMISSION_KEY_SCHEMA,
	"thread_edit_vote": PERMISSION_KEY_SCHEMA,
	"thread_merge_own": PERMISSION_KEY_SCHEMA,
	"thread_merge_any": PERMISSION_KEY_SCHEMA,
	"thread_move_own": PERMISSION_KEY_SCHEMA,
	"thread_move_any": PERMISSION_KEY_SCHEMA,
	"thread_view": PERMISSION_KEY_SCHEMA,
	"user_delete": PERMISSION_KEY_SCHEMA,
	"user_edit": PERMISSION_KEY_SCHEMA,
	"user_edit_ban": PERMISSION_KEY_SCHEMA,
	"user_edit_groups": PERMISSION_KEY_SCHEMA,
	"user_edit_permissions": PERMISSION_KEY_SCHEMA
})
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", models.User)
@limiter.limiter.limit(get_endpoint_limit)
def edit_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the user with the given ID's specific permissions.
	Automatically creates them if they don't exist.

	Idempotent.
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
		models.UserPermissions.create(
			flask.g.sa_session,
			user=user,
			**flask.g.json
		)

		status = helpers.STATUS_CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(user.permissions, key) is not value:
				unchanged = False
				setattr(user.permissions, key, value)

		if unchanged:
			raise exceptions.APIUserPermissionsUnchanged(user.id)

		user.permissions.edited()

		status = helpers.STATUS_OK

	flask.g.sa_session.commit()

	return flask.jsonify(user.permissions), status


@user_blueprint.route("/users/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@limiter.limiter.limit(get_endpoint_limit)
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that the current `flask.g.user` is authorized to
	perform without any knowledge on which user they'll be done on.

	Idempotent.
	"""

	return flask.jsonify(
		models.User.get_allowed_class_actions(flask.g.user)
	)
