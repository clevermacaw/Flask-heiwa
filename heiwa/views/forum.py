import typing
import uuid

import flask
import sqlalchemy

from .. import (
	authentication,
	encoders,
	exceptions,
	helpers,
	models,
	validators
)
from .helpers import (
	BASE_PERMISSION_SCHEMA,
	find_forum_by_id,
	find_group_by_id,
	find_user_by_id,
	generate_list_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_permission
)

__all__ = ["forum_blueprint"]

forum_blueprint = flask.Blueprint(
	"forum",
	__name__,
	url_prefix="/forums"
)
forum_blueprint.json_encoder = encoders.JSONEncoder

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
	}
	"parent_forum_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"user_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"name": {
		"type": "string",
		"minlength": 1,
		"maxlength": 128
	},
	"description": {
		"type": "string",
		"minlength": 1,
		"maxlength": 65536
	},
	"order": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"last_thread_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"subscriber_count": {
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

CREATE_EDIT_SCHEMA = {
	"name": {
		**ATTR_SCHEMAS["name"],
		"required": True
	},
	"description": {
		**ATTR_SCHEMAS["description"],
		"nullable": True,
		"required": True
	},
	"order": {
		**ATTR_SCHEMAS["order"],
		"required": True
	},
	"parent_forum_id": {
		**ATTR_SCHEMAS["parent_forum_id"],
		"nullable": True,
		"required": True
	}
}
LIST_SCHEMA = generate_list_schema(
	(
		"order",
		"creation_timestamp",
		"edit_timestamp",
		"edit_count",
		"subscriber_count",
		"thread_count"
	),
	default_order_by="order",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"],
	"order": ATTR_SCHEMAS["order"],
	"last_thread_timestamp": ATTR_SCHEMAS["last_thread_timestamp"],
	"subscriber_count": ATTR_SCHEMAS["subscriber_count"],
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
			"parent_forum_id": {
				**ATTR_SCHEMAS["parent_forum_id"],
				"nullable": True
			},
			"user_id": ATTR_SCHEMAS["user_id"],
			"name": ATTR_SCHEMAS["name"],
			"description": {
				**ATTR_SCHEMAS["description"],
				"nullable": True
			},
			"order": ATTR_SCHEMAS["order"],
			"last_thread_timestamp": {
				**ATTR_SCHEMAS["last_thread_timestamp"],
				"nullable": True
			},
			"subscriber_count": ATTR_SCHEMAS["subscriber_count"],
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
			"edit_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["edit_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"parent_forum_id": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["parent_forum_id"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"user_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["user_id"],
				"minlength": 1,
				"maxlength": 32
			},
			"name": {
				"type": "list",
				"schema": ATTR_SCHEMAS["name"],
				"minlength": 1,
				"maxlength": 32
			},
			"description": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["description"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"order": {
				"type": "list",
				"schema": ATTR_SCHEMAS["order"],
				"minlength": 1,
				"maxlength": 32
			},
			"last_thread_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["last_thread_timestamp"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"subscriber_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["subscriber_count"],
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
			"name": {
				**ATTR_SCHEMAS["name"],
				"check_with": "is_valid_regex"
			},
			"description": {
				**ATTR_SCHEMAS["description"],
				"check_with": "is_valid_regex"
			}
		},
		"maxlength": 1
	}
})


@forum_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create", models.Forum)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a forum with the requested `parent_forum_id`, `name`, `description`
	and default order position (`order`).
	"""

	forum = models.Forum(
		user_id=flask.g.user.id,
		**flask.g.json
	)

	if flask.g.json["parent_forum_id"] is not None:
		with flask.g.sa_session.no_autoflush:
			parent_forum = find_forum_by_id(
				flask.g.json["parent_forum_id"],
				flask.g.sa_session,
				flask.g.user
			)

			validate_permission(
				flask.g.user,
				"create_subforum",
				parent_forum
			)

			if (
				parent_forum.get_child_level() + 1
				> flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
			):
				raise exceptions.APIForumChildLevelLimitReached(
					flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
				)

		forum.parent_forum = parent_forum

	forum.write(flask.g.sa_session)
	forum.reparse_permissions(flask.g.user)

	flask.g.sa_session.commit()

	return flask.jsonify(forum), helpers.STATUS_CREATED


@forum_blueprint.route("", methods=["GET"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.Forum)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all forums that match the requested filter, and `flask.g.user` has
	permission to view. If parsed permissions don't exist for them, they're
	automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		models.Forum.id == models.ForumParsedPermissions.forum_id,
		models.ForumParsedPermissions.user_id == flask.g.user.id
	)

	conditions = sqlalchemy.or_(
		~(
			sqlalchemy.select(models.ForumParsedPermissions.forum_id).
			where(inner_conditions).
			exists()
		),
		(
			sqlalchemy.select(models.ForumParsedPermissions.forum_id).
			where(
				sqlalchemy.and_(
					inner_conditions,
					models.ForumParsedPermissions.forum_view.is_(True)
				)
			).
			exists()
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Forum
			)
		)

	order_column = getattr(
		models.Forum,
		flask.g.json["order"]["by"]
	)

	forum_without_permissions_exists = False
	first_iteration = True

	while first_iteration or forum_without_permissions_exists:
		first_iteration = False
		forum_without_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Forum,
				(
					sqlalchemy.select(models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(conditions).
			order_by(
				sqlalchemy.asc(order_column)
				if flask.g.json["order"]["asc"]
				else sqlalchemy.desc(order_column)
			).
			limit(flask.g.json["limit"]).
			offset(flask.g.json["offset"])
		).all()

		for row in rows:
			if not row[1]:
				forum_without_permissions_exists = True

				row[0].reparse_permissions(flask.g.user)

		if forum_without_permissions_exists:
			flask.g.sa_session.commit()

	return flask.jsonify(
		[
			row[0]
			for row in rows
		]
	), helpers.STATUS_OK


@forum_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Forum)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all forums that match the requested filter, and `flask.g.user` has
	permission to both view and delete. If parsed permissions don't exist for
	them, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		models.Forum.id == models.ForumParsedPermissions.forum_id,
		models.ForumParsedPermissions.user_id == flask.g.user.id
	)

	conditions = sqlalchemy.or_(
		~(
			sqlalchemy.select(models.ForumParsedPermissions.forum_id).
			where(inner_conditions).
			exists()
		),
		(
			sqlalchemy.select(models.ForumParsedPermissions.forum_id).
			where(
				sqlalchemy.and_(
					inner_conditions,
					models.ForumParsedPermissions.forum_view.is_(True),
					sqlalchemy.or_(
						sqlalchemy.and_(
							models.Forum.user_id == flask.g.user.id,
							models.ForumParsedPermissions.forum_delete_own.is_(True)
						),
						models.ForumParsedPermissions.forum_delete_any.is_(True)
					)
				)
			).
			exists()
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Forum
			)
		)

	order_column = getattr(
		models.Forum,
		flask.g.json["order"]["by"]
	)

	forum_without_permissions_exists = False
	first_iteration = True

	while first_iteration or forum_without_permissions_exists:
		first_iteration = False
		forum_without_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Forum,
				(
					sqlalchemy.select(models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(conditions).
			order_by(
				sqlalchemy.asc(order_column)
				if flask.g.json["order"]["asc"]
				else sqlalchemy.desc(order_column)
			).
			limit(flask.g.json["limit"]).
			offset(flask.g.json["offset"])
		).all()

		ids = []

		for row in rows:
			ids.append(row[0].id)

			if not row[1]:
				forum_without_permissions_exists = True

				row[0].reparse_permissions(flask.g.user)

		if forum_without_permissions_exists:
			flask.g.sa_session.commit()

	if len(ids) != 0:
		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Forum).
			where(models.Forum.id.in_(ids))
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@forum_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Forum)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the forum with the requested `id_`."""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"delete",
		forum
	)

	forum.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@forum_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", models.Forum)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the forum with the requested `id_` with the requested values."""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit",
		forum
	)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(forum, key) != value:
			unchanged = False
			setattr(forum, key, value)

	if unchanged:
		raise exceptions.APIForumUnchanged(forum.id)

	if flask.g.json["parent_forum_id"] != forum.parent_forum_id:
		if forum.id == flask.g.json["parent_forum_id"]:
			raise exceptions.APIForumParentIsChild(id)

		future_parent = find_forum_by_id(
			flask.g.json["parent_forum_id"],
			flask.g.sa_session,
			flask.g.user
		)

		forum.future_parent = future_parent

		validate_permission(
			flask.g.user,
			"move",
			forum
		)

		if (
			forum.future_parent.get_child_level() + 1
			> flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
		):
			raise exceptions.APIForumChildLevelLimitReached(
				flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
			)

		forum.parent_forum = future_parent

		forum.recount_level()

		for child_forum in forum.child_forums:
			child_forum.recount_level()

	forum.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(forum), helpers.STATUS_OK


@forum_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Forum)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the forum with the requested `id_`."""

	return flask.jsonify(
		find_forum_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		)
	), helpers.STATUS_OK


@forum_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Forum)
def authorized_actions_forum(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that `flask.g.user` is authorized to perform on the
	forum with the requested `id_`.
	"""

	return flask.jsonify(
		find_forum_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		).get_allowed_instance_actions(flask.g.user)
	)


@forum_blueprint.route("/<uuid:id_>/merge", methods=["PUT"])
@validators.validate_json({
	"id": {
		"type": "uuid",
		"coerce": "convert_to_uuid",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("merge", models.Forum)
def merge(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Moves all threads and posts from the forum with the given `id_` to the
	one with the `id` provided in the request body, then deletes the old forum.
	"""

	old_forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)
	new_forum = find_forum_by_id(
		flask.g.json["id"],
		flask.g.sa_session,
		flask.g.user
	)

	old_forum.future_parent = new_forum

	validate_permission(
		flask.g.user,
		"merge",
		old_forum
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(models.Thread).
		where(models.Thread.id == old_forum.id).
		values(id=new_forum.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(models.Forum).
		where(models.Forum.parent_forum_id == old_forum.id).
		values(parent_forum_id=new_forum.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(models.forum_subscribers).
		where(models.forum_subscribers.forum_id == old_forum.id).
		values(parent_forum_id=new_forum.id)
	)

	old_forum.delete()
	new_forum.edited()

	flask.g.sa_session.commit()

	new_forum.recount_level()

	for child_forum in new_forum.child_forums:
		child_forum.recount_level()

	flask.g.sa_session.commit()

	return flask.jsonify(new_forum), helpers.STATUS_OK


@forum_blueprint.route("/<uuid:id_>/parsed-permissions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Forum)
def view_parsed_permissions(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns the parsed permissions for `flask.g.user` for the forum with the
	requested `id_`. If they haven't been parsed yet, it's done so atomatically.
	"""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	parsed_permissions = forum.get_parsed_permissions(flask.g.user.id)

	if parsed_permissions is None:
		parsed_permissions = forum.reparse_permissions(flask.g.user)

	return flask.jsonify(parsed_permissions), helpers.STATUS_OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["DELETE"]
)
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_group", models.Forum)
def delete_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the permissions for the group with the requested `group_id` for the
	forum with the given `forum_id`.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session
	)

	forum.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				models.ForumPermissionsGroup.forum_id == forum.id,
				models.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	if permissions is None:
		raise exceptions.APIForumPermissionsGroupNotFound({
			"forum_id": forum.id,
			"group_id": group.id
		})

	flask.g.sa_session.execute(
		sqlalchemy.delete(models.ForumParsedPermissions).
		where(models.ForumParsedPermissions.forum_id == forum.id)
	)

	permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["PUT"]
)
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_group", models.Forum)
def edit_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Updates the permissions for the group with the requested `group_id` for the
	forum with the given `forum_id` with the requested values.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session
	)

	forum.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				models.ForumPermissionsGroup.forum_id == forum.id,
				models.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	if permissions is None:
		permissions = models.ForumPermissionsGroup.create(
			flask.g.sa_session,
			forum_id=forum.id,
			group_id=group.id,
			**flask.g.json
		)

		status = helpers.STATUS_CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(permissions, key) != value:
				unchanged = False
				setattr(permissions, key, value)

		if unchanged:
			raise exceptions.APIForumPermissionsGroupUnchanged(forum.id)

		permissions.edited()

		status = helpers.STATUS_OK

	flask.g.sa_session.execute(
		sqlalchemy.delete(models.ForumParsedPermissions).
		where(models.ForumParsedPermissions.forum_id == forum.id)
	)

	flask.g.sa_session.commit()

	return flask.jsonify(permissions), status


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions_group", models.Forum)
def view_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns `group_id`'s permissions for the forum with the requested
	`forum_id`.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				models.ForumPermissionsGroup.forum_id == forum.id,
				models.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	return flask.jsonify(permissions), helpers.STATUS_OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["DELETE"]
)
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_user", models.Forum)
def delete_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the permissions for the user with the requested `user_id` for the
	forum with the given `forum_id`.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	user = find_user_by_id(
		user_id,
		flask.g.sa_session
	)

	forum.edited_user = user

	validate_permission(
		flask.g.user,
		"edit_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsUser).
		where(
			models.ForumPermissionsUser.forum_id == forum.id,
			models.ForumPermissionsUser.user_id == user.id
		)
	).scalars().one_or_none()

	if permissions is None:
		raise exceptions.APIForumPermissionsUserNotFound({
			"forum_id": forum.id,
			"user_id": user.id
		})

	flask.g.sa_session.execute(
		sqlalchemy.delete(models.ForumParsedPermissions).
		where(models.ForumParsedPermissions.forum_id == forum.id)
	)

	permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["PUT"]
)
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_user", models.Forum)
def edit_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Updates the permissions for the user with the requested `user_id` for the
	forum with the given `forum_id` with the requested values.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	user = find_user_by_id(
		user_id,
		flask.g.sa_session
	)

	forum.edited_user = user

	validate_permission(
		flask.g.user,
		"edit_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsUser).
		where(
			models.ForumPermissionsUser.forum_id == forum.id,
			models.ForumPermissionsUser.user_id == user.id
		)
	).scalars().one_or_none()

	if permissions is None:
		permissions = models.ForumPermissionsUser.create(
			flask.g.sa_session,
			forum_id=forum.id,
			user_id=user.id,
			**flask.g.json
		)

		status = helpers.STATUS_CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(permissions, key) != value:
				unchanged = False
				setattr(permissions, key, value)

		if unchanged:
			raise exceptions.APIForumPermissionsUserUnchanged(forum.id)

		permissions.edited()

		status = helpers.STATUS_OK

	flask.g.sa_session.execute(
		sqlalchemy.delete(models.ForumParsedPermissions).
		where(models.ForumParsedPermissions.forum_id == forum.id)
	)

	flask.g.sa_session.commit()

	return flask.jsonify(permissions), status


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions_user", models.Forum)
def view_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns `user_id`'s permissions for the forum with the requested
	`forum_id`.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	user = find_user_by_id(
		user_id,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(models.ForumPermissionsUser).
		where(
			models.ForumPermissionsUser.forum_id == forum.id,
			models.ForumPermissionsUser.user_id == user.id
		)
	).scalars().one_or_none()

	return flask.jsonify(permissions), helpers.STATUS_OK


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", models.Forum)
def create_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a subscription for `flask.g.user` to the forum with the
	requested `id_`.
	"""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_subscription",
		forum
	)

	if (
		flask.g.sa_session.execute(
			sqlalchemy.select(models.forum_subscribers).
			where(
				sqlalchemy.and_(
					models.forum_subscribers.c.forum_id == forum.id,
					models.forum_subscribers.c.user_id == flask.g.user.id
				)
			)
		).scalars().one_or_none()
	) is not None:
		raise exceptions.APIForumSubscriptionAlreadyExists(forum.id)

	flask.g.sa_session.execute(
		sqlalchemy.insert(models.forum_subscribers).
		values(
			forum_id=forum.id,
			user_id=flask.g.user.id
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", models.Forum)
def delete_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Removes `flask.g.user`'s subscription to the forum with the requested
	`id_`.
	"""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_subscription",
		forum
	)

	existing_subscription = flask.g.sa_session.execute(
		sqlalchemy.select(models.forum_subscribers).
		where(
			sqlalchemy.and_(
				models.forum_subscribers.c.forum_id == forum.id,
				models.forum_subscribers.c.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_subscription is None:
		raise exceptions.APIForumSubscriptionNotFound(forum.id)

	flask.g.sa_session.delete(existing_subscription)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Forum)
def view_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not `flask.g.user` is subscribed to the forum with the
	requested `id_`.
	"""

	return flask.jsonify(
		flask.g.sa_session.execute(
			sqlalchemy.select(models.forum_subscribers.c.forum_id).
			where(
				sqlalchemy.and_(
					models.forum_subscribers.c.forum_id == find_forum_by_id(
						id_,
						flask.g.sa_session,
						flask.g.user
					).id,
					models.forum_subscribers.c.user_id == flask.g.user.id
				)
			).
			exists().
			select()
		).scalars().one()
	), helpers.STATUS_OK


@forum_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that `flask.g.user` is authorized to perform on
	forums without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		models.Forum.get_allowed_class_actions(flask.g.user)
	)
