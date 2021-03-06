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
	PERMISSION_KEY_SCHEMA,
	SEARCH_MAX_IN_LIST_LENGTH,
	find_category_by_id,
	find_forum_by_id,
	find_group_by_id,
	find_user_by_id,
	generate_search_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_category_exists,
	validate_forum_exists,
	validate_permission,
	validate_user_exists
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
	},
	"category_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"parent_forum_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"name": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.Forum.name.property.columns[0].type.length
	},
	"description": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.Forum.description.property.columns[0].type.length
	},
	"order": {
		"type": "integer",
		"min": -2147483647,
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
	"category_id": {
		**ATTR_SCHEMAS["category_id"],
		"nullable": True,
		"required": True
	},
	"parent_forum_id": {
		**ATTR_SCHEMAS["parent_forum_id"],
		"nullable": True,
		"required": True
	},
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
	}
}
SEARCH_SCHEMA = generate_search_schema(
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

PERMISSION_SCHEMA = {
	"category_create": PERMISSION_KEY_SCHEMA,
	"category_delete": PERMISSION_KEY_SCHEMA,
	"category_edit": PERMISSION_KEY_SCHEMA,
	"category_view": PERMISSION_KEY_SCHEMA,
	"forum_create": PERMISSION_KEY_SCHEMA,
	"forum_delete": PERMISSION_KEY_SCHEMA,
	"forum_edit": PERMISSION_KEY_SCHEMA,
	"forum_merge": PERMISSION_KEY_SCHEMA,
	"forum_move": PERMISSION_KEY_SCHEMA,
	"forum_view": PERMISSION_KEY_SCHEMA,
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
	"thread_view": PERMISSION_KEY_SCHEMA
}

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
			"category_id": {
				**ATTR_SCHEMAS["category_id"],
				"nullable": True
			},
			"parent_forum_id": {
				**ATTR_SCHEMAS["parent_forum_id"],
				"nullable": True
			},
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
			"category_id": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["category_id"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"parent_forum_id": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["parent_forum_id"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"name": {
				"type": "list",
				"schema": ATTR_SCHEMAS["name"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"description": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["description"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"order": {
				"type": "list",
				"schema": ATTR_SCHEMAS["order"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"last_thread_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["last_thread_timestamp"],
					"nullable": True
				},
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"subscriber_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["subscriber_count"],
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
@requires_permission("create", database.Forum)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a forum with the requested ``category_id``, ``parent_forum_id``,
	``name``, ``description`` and default order position (``order``).
	"""

	forum = database.Forum(**flask.g.json)

	if flask.g.json["category_id"] is not None:
		with flask.g.sa_session.no_autoflush:
			if flask.g.json["parent_forum_id"] is not None:
				category = find_category_by_id(
					flask.g.json["category_id"],
					flask.g.sa_session,
					flask.g.user
				)

				if category.forum_id != flask.g.json["parent_forum_id"]:
					raise exceptions.APIForumCategoryOutsideParent
			else:
				validate_category_exists(
					flask.g.json["category_id"],
					flask.g.sa_session,
					flask.g.user
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
				"create_child_forum",
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

	return flask.jsonify(forum), statuses.CREATED


@forum_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.Forum)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all forums that match the requested filter if there is one, and
	``flask.g.user`` has permission to view. If parsed permissions don't exist
	for them, they're automatically calculated.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Forum
			)
		)

	order_column = getattr(
		database.Forum,
		flask.g.json["order"]["by"]
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			database.Forum.get(
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


@forum_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Forum)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all forums that match the requested filter if there is one, and
	``flask.g.user`` has permission to both view and delete. If parsed permissions
	don't exist for them, they're automatically calculated.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Forum
			)
		)

	order_column = getattr(
		database.Forum,
		flask.g.json["order"]["by"]
	)

	forum_ids = flask.g.sa_session.execute(
		database.Forum.get(
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
			offset=flask.g.json["offset"],
			ids_only=True
		)
	).scalars().all()

	thread_ids = flask.g.sa_session.execute(
		sqlalchemy.select(database.Thread.id).
		where(database.Thread.forum_id.in_(forum_ids))
	).scalars().all()

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.Notification).
		where(
			sqlalchemy.or_(
				sqlalchemy.and_(
					database.Notification.type.in_(database.Thread.NOTIFICATION_TYPES),
					database.Notification.identifier.in_(thread_ids)
				),
				sqlalchemy.and_(
					database.Notification.type.in_(database.Post.NOTIFICATION_TYPES),
					database.Notification.identifier.in_(
						sqlalchemy.select(database.Post.id).
						where(database.Post.thread_id.in_(thread_ids))
					)
				)
			)
		).
		execution_options(synchronize_session="fetch")
	)

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.Forum).
		where(database.Forum.id.in_(forum_ids))
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@forum_blueprint.route("", methods=["PUT"])
@validators.validate_json(
	{
		**SEARCH_SCHEMA,
		"values": {
			"type": "dict",
			"minlength": 1,
			"schema": {
				"parent_forum_id": {
					**ATTR_SCHEMAS["parent_forum_id"],
					"nullable": True,
					"required": False
				},
				"category_id": {
					**ATTR_SCHEMAS["category_id"],
					"nullable": True,
					"required": False
				},
				"name": {
					**ATTR_SCHEMAS["name"],
					"required": False
				},
				"description": {
					**ATTR_SCHEMAS["description"],
					"nullable": True,
					"required": False
				},
				"order": {
					**ATTR_SCHEMAS["order"],
					"required": False
				}
			}
		}
	},
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.Thread)
def mass_edit() -> typing.Tuple[flask.Response, int]:
	"""Updates all forums that match the requested filter if there is one, and
	``flask.g.user`` has permission to both view and edit. If parsed permissions
	haven't been calculated for them, they're automatically calculated.
	"""

	conditions = True
	additional_actions = ["edit"]

	if "category_id" in flask.g.json["values"]:
		category = find_category_by_id(
			flask.g.json["category_id"],
			flask.g.sa_session,
			flask.g.user
		)

		if "parent_forum_id" in flask.g.json["values"]:
			if category.forum_id != flask.g.json["values"]["parent_forum_id"]:
				raise exceptions.APIForumCategoryOutsideParent
		else:
			conditions = sqlalchemy.and_(
				conditions,
				database.Forum.parent_forum_id == category.forum_id
			)

	if "parent_forum_id" in flask.g.json["values"]:
		parent_forum = find_forum_by_id(
			flask.g.json["values"]["parent_forum_id"],
			flask.g.sa_session,
			flask.g.user
		)

		validate_permission(
			flask.g.user,
			"move",
			parent_forum
		)

		if (
			parent_forum.get_child_level() + 1
			> flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
		):
			raise exceptions.APIForumChildLevelLimitReached(
				flask.current_app.config["FORUM_MAX_CHILD_LEVEL"]
			)

		additional_actions.append("move")

		conditions = sqlalchemy.and_(
			conditions,
			database.Forum.id != parent_forum.id
		)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Forum
			)
		)

	order_column = getattr(
		database.Forum,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(database.Forum).
		where(
			database.Forum.id.in_(
				database.Forum.get(
					flask.g.user,
					flask.g.sa_session,
					additional_actions=additional_actions,
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


@forum_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Forum)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the forum with the requested ``id_``."""

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

	return flask.jsonify({}), statuses.NO_CONTENT


@forum_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.Forum)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the forum with the requested ``id_`` with the requested values."""

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

	if flask.g.json["category_id"] != forum.category_id:
		category = find_category_by_id(
			flask.g.json["category_id"],
			flask.g.sa_session,
			flask.g.user
		)

		if (
			category.forum_id != (
				flask.g.json["parent_forum_id"]
				if flask.g.json["parent_forum_id"] != forum.parent_forum_id
				else forum.parent_forum_id
			)
		):
			raise exceptions.APIForumCategoryOutsideParent

	if flask.g.json["parent_forum_id"] != forum.parent_forum_id:
		if forum.id == flask.g.json["parent_forum_id"]:
			raise exceptions.APIForumParentIsChild

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

		forum.delete_all_parsed_permissions(flask.g.sa_session)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(forum, key) != value:
			unchanged = False
			setattr(forum, key, value)

	if unchanged:
		raise exceptions.APIForumUnchanged

	forum.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(forum), statuses.OK


@forum_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Forum)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the forum with the requested ``id_``."""

	return flask.jsonify(
		find_forum_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		)
	), statuses.OK


@forum_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Forum)
def authorized_actions_forum(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on the
	forum with the requested ``id_``.
	"""

	return flask.jsonify(
		find_forum_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		).get_allowed_instance_actions(flask.g.user)
	)


@forum_blueprint.route("/<uuid:id_old>/merge/<uuid:id_new>", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("merge", database.Forum)
def merge(
	id_old: uuid.UUID,
	id_new: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Moves all threads and posts from the forum with the given ``id_old`` to
	the one with the ``id_new``, then deletes the old forum.
	"""

	old_forum = find_forum_by_id(
		id_old,
		flask.g.sa_session,
		flask.g.user
	)
	new_forum = find_forum_by_id(
		id_new,
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
		sqlalchemy.update(database.Thread).
		where(database.Thread.id == old_forum.id).
		values(id=new_forum.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(database.Forum).
		where(database.Forum.parent_forum_id == old_forum.id).
		values(parent_forum_id=new_forum.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(database.forum_subscribers).
		where(database.forum_subscribers.c.forum_id == old_forum.id).
		values(parent_forum_id=new_forum.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(database.Notification).
		where(
			sqlalchemy.and_(
				database.Notification.type.in_(database.Forum.NOTIFICATION_TYPES),
				database.Notification.identifier == old_forum.id
			)
		).
		values(
			identifier=new_forum.id
		)
	)

	new_forum.delete_all_parsed_permissions(flask.g.sa_session)

	old_forum.delete()
	new_forum.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(new_forum), statuses.OK


@forum_blueprint.route("/<uuid:id_>/parsed-permissions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Forum)
def view_parsed_permissions(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns the parsed permissions for ``flask.g.user`` for the forum with the
	requested ``id_``. If they haven't been parsed yet, it's done so atomatically.
	"""

	forum = find_forum_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	return flask.jsonify(
		forum.get_parsed_permissions(flask.g.user)
	), statuses.OK


# TODO: List and mass delete permissions for groups and users


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["DELETE"]
)
@validators.validate_json(PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_group", database.Forum)
def delete_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the permissions for the group with the requested ``group_id`` for
	the forum with the given ``forum_id``.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session,
		flask.g.user
	)

	forum.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				database.ForumPermissionsGroup.forum_id == forum.id,
				database.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	if permissions is None:
		raise exceptions.APIForumPermissionsGroupNotFound

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.ForumParsedPermissions).
		where(database.ForumParsedPermissions.forum_id == forum.id)
	)

	permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["PUT"]
)
@validators.validate_json(PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_group", database.Forum)
def edit_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Updates the permissions for the group with the requested ``group_id`` for
	the forum with the given ``forum_id`` with the requested values.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session,
		flask.g.user
	)

	forum.edited_group = group

	validate_permission(
		flask.g.user,
		"edit_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				database.ForumPermissionsGroup.forum_id == forum.id,
				database.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	if permissions is None:
		permissions = database.ForumPermissionsGroup.create(
			flask.g.sa_session,
			forum_id=forum.id,
			group_id=group.id,
			**flask.g.json
		)

		status = statuses.CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(permissions, key) != value:
				unchanged = False
				setattr(permissions, key, value)

		if unchanged:
			raise exceptions.APIForumPermissionsGroupUnchanged

		permissions.edited()

		status = statuses.OK

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.ForumParsedPermissions).
		where(database.ForumParsedPermissions.forum_id == forum.id)
	)

	flask.g.sa_session.commit()

	return flask.jsonify(permissions), status


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/group/<uuid:group_id>",
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions_group", database.Forum)
def view_permissions_group(
	forum_id: uuid.UUID,
	group_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns ``group_id``'s permissions for the forum with the requested
	``forum_id``.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	group = find_group_by_id(
		group_id,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"view_permissions_group",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsGroup).
		where(
			sqlalchemy.and_(
				database.ForumPermissionsGroup.forum_id == forum.id,
				database.ForumPermissionsGroup.group_id == group.id
			)
		)
	).scalars().one_or_none()

	return flask.jsonify(permissions), statuses.OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["DELETE"]
)
@validators.validate_json(PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_user", database.Forum)
def delete_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Deletes the permissions for the user with the requested ``user_id`` for the
	forum with the given ``forum_id``.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	user = find_user_by_id(
		user_id,
		flask.g.sa_session,
		flask.g.user
	)

	forum.edited_user = user

	validate_permission(
		flask.g.user,
		"edit_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsUser).
		where(
			database.ForumPermissionsUser.forum_id == forum.id,
			database.ForumPermissionsUser.user_id == user.id
		)
	).scalars().one_or_none()

	if permissions is None:
		raise exceptions.APIForumPermissionsUserNotFound

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.ForumParsedPermissions).
		where(database.ForumParsedPermissions.forum_id == forum.id)
	)

	permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.OK


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["PUT"]
)
@validators.validate_json(PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions_user", database.Forum)
def edit_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Updates the permissions for the user with the requested ``user_id`` for the
	forum with the given ``forum_id`` with the requested values.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	user = find_user_by_id(
		user_id,
		flask.g.sa_session,
		flask.g.user
	)

	forum.edited_user = user

	validate_permission(
		flask.g.user,
		"edit_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsUser).
		where(
			database.ForumPermissionsUser.forum_id == forum.id,
			database.ForumPermissionsUser.user_id == user.id
		)
	).scalars().one_or_none()

	if permissions is None:
		permissions = database.ForumPermissionsUser.create(
			flask.g.sa_session,
			forum_id=forum.id,
			user_id=user.id,
			**flask.g.json
		)

		status = statuses.CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(permissions, key) != value:
				unchanged = False
				setattr(permissions, key, value)

		if unchanged:
			raise exceptions.APIForumPermissionsUserUnchanged

		permissions.edited()

		status = statuses.OK

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.ForumParsedPermissions).
		where(database.ForumParsedPermissions.forum_id == forum.id)
	)

	flask.g.sa_session.commit()

	return flask.jsonify(permissions), status


@forum_blueprint.route(
	"/<uuid:forum_id>/permissions/user/<uuid:user_id>",
	methods=["GET"]
)
@authentication.authenticate_via_jwt
@requires_permission("view_permissions_user", database.Forum)
def view_permissions_user(
	forum_id: uuid.UUID,
	user_id: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns ``user_id``'s permissions for the forum with the requested
	``forum_id``.
	"""

	forum = find_forum_by_id(
		forum_id,
		flask.g.sa_session,
		flask.g.user
	)

	validate_user_exists(
		user_id,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"view_permissions_user",
		forum
	)

	permissions = flask.g.sa_session.execute(
		sqlalchemy.select(database.ForumPermissionsUser).
		where(
			database.ForumPermissionsUser.forum_id == forum.id,
			database.ForumPermissionsUser.user_id == user_id
		)
	).scalars().one_or_none()

	return flask.jsonify(permissions), statuses.OK


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", database.Forum)
def create_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a subscription for ``flask.g.user`` to the forum with the
	requested ``id_``.
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
			sqlalchemy.select(database.forum_subscribers).
			where(
				sqlalchemy.and_(
					database.forum_subscribers.c.forum_id == forum.id,
					database.forum_subscribers.c.user_id == flask.g.user.id
				)
			)
		).scalars().one_or_none()
	) is not None:
		raise exceptions.APIForumSubscriptionAlreadyExists

	flask.g.sa_session.execute(
		sqlalchemy.insert(database.forum_subscribers).
		values(
			forum_id=forum.id,
			user_id=flask.g.user.id
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", database.Forum)
def delete_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Removes ``flask.g.user``'s subscription to the forum with the requested
	``id_``.
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
		sqlalchemy.select(database.forum_subscribers).
		where(
			sqlalchemy.and_(
				database.forum_subscribers.c.forum_id == forum.id,
				database.forum_subscribers.c.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_subscription is None:
		raise exceptions.APIForumSubscriptionNotFound

	flask.g.sa_session.delete(existing_subscription)

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@forum_blueprint.route("/<uuid:id_>/subscription", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Forum)
def view_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not ``flask.g.user`` is subscribed to the forum with the
	requested ``id_``.
	"""

	validate_forum_exists(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	return flask.jsonify(
		flask.g.sa_session.execute(
			sqlalchemy.select(database.forum_subscribers.c.forum_id).
			where(
				sqlalchemy.and_(
					id_,
					database.forum_subscribers.c.user_id == flask.g.user.id
				)
			).
			exists().
			select()
		).scalars().one()
	), statuses.OK


@forum_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on
	forums without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		database.Forum.get_allowed_static_actions(flask.g.user)
	), statuses.OK
