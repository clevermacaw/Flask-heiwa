import operator
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
	models,
	validators
)
from .helpers import (
	BASE_PERMISSION_SCHEMA,
	find_group_by_id,
	generate_list_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_permission
)

__all__ = ["group_blueprint"]

group_blueprint = flask.Blueprint(
	"group",
	__name__,
	url_prefix="/groups"
)
group_blueprint.json_encoder = encoders.JSONEncoder

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
	"default_for": {
		"type": "list",
		"check_with": "has_no_duplicates",
		"schema": {
			"type": "string",
			"minlength": 1,
			"maxlength": 128
		}
	},
	"level": {
		"type": "integer",
		"min": -2147483647,
		"maxlength": 2147483647
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
	"user_count": {
		"type": "integer",
		"min": 0,
		"maxlength": 2147483647
	}
}

CREATE_EDIT_SCHEMA = {
	"default_for": {
		**ATTR_SCHEMAS["default_for"],
		"required": True
	},
	"level": {
		**ATTR_SCHEMAS["level"],
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
	}
}
LIST_SCHEMA = generate_list_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"level",
		"user_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"level": ATTR_SCHEMAS["level"],
	"user_count": ATTR_SCHEMAS["user_count"]
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
			"default_for": ATTR_SCHEMAS["default_for"],
			"level": ATTR_SCHEMAS["level"],
			"name": ATTR_SCHEMAS["name"],
			"description": {
				**ATTR_SCHEMAS["description"],
				"nullable": True
			},
			"user_count": ATTR_SCHEMAS["user_count"]
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
			"default_for": {
				"type": "list",
				"schema": ATTR_SCHEMAS["default_for"],
				"minlength": 1,
				"maxlength": 32
			},
			"level": {
				"type": "list",
				"schema": ATTR_SCHEMAS["level"],
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
			"user_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["user_count"],
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


def check_if_last_default_group(group: models.Group) -> bool:
	"""Returns whether or not the given `group` is the last group which is
	default for `*`. This function assumes this group has that attribute,
	and there is no need to check.
	"""

	if flask.g.sa_session.execute(
		sqlalchemy.select(models.Group).
		where(
			sqlalchemy.and_(
				models.Group.id != group.id,
				models.Group.default_for.any(
					"*",
					operator=operator.eq
				)
			)
		).
		exists()
	).scalars().one():
		return False

	return True


@group_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create", models.Group)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a group with the given name, description and level.

	Not idempotent.
	"""

	group = models.Group.create(
		flask.g.sa_session,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(group), helpers.STATUS_CREATED


@group_blueprint.route("", methods=["GET"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.Group)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all available groups.

	Idempotent.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Group
			)
		)

	order_column = getattr(
		models.Group,
		flask.g.json["order"]["by"]
	)

	groups = flask.g.sa_session.execute(
		sqlalchemy.select(models.Group).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(groups), helpers.STATUS_OK


@group_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Group)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all groups that match the given conditions.

	Not idempotent.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Group
			)
		)

	order_column = getattr(
		models.Group,
		flask.g.json["order"]["by"]
	)

	groups = flask.g.sa_session.execute(
		sqlalchemy.select(models.Group).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	if len(groups) != 0:
		ids = []

		for group in groups:
			ids.append(group.id)

			if "*" in group.default_for and check_if_last_default_group(group):
				raise exceptions.APIGroupCannotDeleteLastDefault(group.id)

		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Group).
			where(models.Group.id.in_(ids))
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@group_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Group)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the group with the given ID.

	Idempotent.
	"""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"delete",
		group
	)

	if "*" in group.default_for and check_if_last_default_group(group):
		raise exceptions.APIGroupCannotDeleteLastDefault(group.id)

	group.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@group_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", models.Group)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the given group with the given values.

	Idempotent.
	"""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit",
		group
	)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(group, key) != value:
			unchanged = False
			setattr(group, key, value)

	if unchanged:
		raise exceptions.APIGroupUnchanged(group.id)

	group.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(group), helpers.STATUS_OK


@group_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Group)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the group with the given ID.

	Idempotent.
	"""

	return flask.jsonify(
		find_group_by_id(
			id_,
			flask.g.sa_session
		)
	), helpers.STATUS_OK


@group_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Group)
def authorized_actions_group(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that the current `flask.g.user` is authorized to
	perform on the given group. This will only be done if they at least have
	permission to view it.

	Idempotent.
	"""

	return flask.jsonify(
		find_group_by_id(
			id_,
			flask.g.sa_session
		).get_allowed_instance_actions(flask.g.user)
	)


@group_blueprint.route("/<uuid:id_>/permissions", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", models.Group)
def delete_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the group with the given ID's permissions.

	Idempotent.
	"""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_permissions",
		group
	)

	if "*" in group.default_for and check_if_last_default_group(group):
		raise exceptions.APIGroupCannotDeletePermissionsForLastDefault(group.id)

	if group.permissions is None:
		raise exceptions.APIGroupPermissionsNotFound(id)

	group.permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@group_blueprint.route("/<uuid:id_>/permissions", methods=["PUT"])
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", models.Group)
def edit_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the group with the given ID's permissions.
	Automatically creates them if they don't exist.

	Idempotent.
	"""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_permissions",
		group
	)

	if "*" in group.default_for:
		for key, value in flask.g.json.items():
			if value is None:
				raise exceptions.APIGroupCannotLeavePermissionNullForLastDefault({
					"group_id": group.id,
					"permission": key
				})

	if group.permissions is None:
		models.GroupPermissions.create(
			flask.g.sa_session,
			group=group,
			**flask.g.json
		)

		status = helpers.STATUS_CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(group.permissions, key) is not value:
				unchanged = False
				setattr(group.permissions, key, value)

		if unchanged:
			raise exceptions.APIGroupPermissionsUnchanged(group.id)

		group.permissions.edited()

		status = helpers.STATUS_OK

	flask.g.sa_session.commit()

	return flask.jsonify(group.permissions), status


@group_blueprint.route("/<uuid:id_>/permissions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view_permissions", models.Group)
def view_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the group with the given ID's permissions.

	Idempotent.
	"""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_permissions",
		group
	)

	return flask.jsonify(group.permissions), helpers.STATUS_OK


@group_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that the current `flask.g.user` is authorized to
	perform without any knowledge on which group they'll be done on.

	Idempotent.
	"""

	return flask.jsonify(
		models.Group.get_allowed_class_actions(flask.g.user)
	)
