import operator
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
	BASE_PERMISSION_SCHEMA,
	find_group_by_id,
	generate_search_schema,
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
	"edit_count": {
		"type": "integer",
		"min": 0,
		"maxlength": 2147483647
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
SEARCH_SCHEMA = generate_search_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"edit_count",
		"level",
		"user_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"],
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
			"edit_count": ATTR_SCHEMAS["edit_count"],
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
			"edit_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["edit_count"],
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


def check_if_last_default_group(group_id: uuid.UUID) -> bool:
	"""Returns whether or not the group with the given ``group_id`` is
	the last group whose ``default_for`` column contains ``'*'``.
	"""

	return flask.g.sa_session.execute(
		sqlalchemy.select(database.Group.id).
		where(
			sqlalchemy.and_(
				database.Group.id != group_id,
				database.Group.default_for.any(
					"*",
					operator=operator.eq
				)
			)
		).
		exists().
		select()
	).scalars().one()


@group_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create", database.Group)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a group with the requested ``name``, ``description``,
	``default_for`` and ``level``.
	"""

	group = database.Group.create(
		flask.g.sa_session,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(group), statuses.CREATED


@group_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.Group)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all groups that match the requested filter, if there is one."""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Group
			)
		)

	order_column = getattr(
		database.Group,
		flask.g.json["order"]["by"]
	)

	groups = flask.g.sa_session.execute(
		sqlalchemy.select(database.Group).
		where(conditions).
		order_by(
			sqlalchemy.asc(order_column)
			if flask.g.json["order"]["asc"]
			else sqlalchemy.desc(order_column)
		).
		limit(flask.g.json["limit"]).
		offset(flask.g.json["offset"])
	).scalars().all()

	return flask.jsonify(groups), statuses.OK


@group_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Group)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all groups that match the requested filter if there is one,
	and ``flask.g.user`` has permission to both view and delete.
	"""

	order_column = getattr(
		database.Group,
		flask.g.json["order"]["by"]
	)

	# Don't delete the last default group
	conditions = (
		database.Group.id != (
			sqlalchemy.select(database.Group.id).
			where(
				database.Group.default_for.any(
					"*",
					operator=operator.eq
				)
			).
			order_by(
				# Order the opposite way
				sqlalchemy.asc(order_column)
				if not flask.g.json["order"]["asc"]
				else sqlalchemy.desc(order_column)
			).
			scalar_subquery()
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Group
			)
		)

	flask.g.sa_session.execute(
		sqlalchemy.delete(database.Group).
		where(
			database.Group.id.in_(
				sqlalchemy.select(database.Group.id).
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


@group_blueprint.route("", methods=["PUT"])
@validators.validate_json(
	{
		**SEARCH_SCHEMA,
		"values": {
			"type": "dict",
			"minlength": 1,
			"schema": {
				"default_for": {
					**ATTR_SCHEMAS["default_for"],
					"required": False
				},
				"level": {
					**ATTR_SCHEMAS["level"],
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
				}
			}
		}
	},
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.Group)
def mass_edit() -> typing.Tuple[flask.Response, int]:
	"""Updates all groups that match the requested filter if there is one,
	and ``flask.g.user`` has permission to both view and edit.
	"""

	conditions = True

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Group
			)
		)

	order_column = getattr(
		database.Group,
		flask.g.json["order"]["by"]
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(database.Group).
		where(
			database.Group.id.in_(
				sqlalchemy.select(database.Group.id).
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


@group_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Group)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the group with the requested ``id_``."""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"delete",
		group
	)

	if "*" in group.default_for and check_if_last_default_group(group.id):
		raise exceptions.APIGroupCannotDeleteLastDefault

	group.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@group_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.Group)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the group with the requested ``id_`` with the requested values."""

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
		raise exceptions.APIGroupUnchanged

	group.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(group), statuses.OK


@group_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Group)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the group with the requested ``id_``."""

	return flask.jsonify(
		find_group_by_id(
			id_,
			flask.g.sa_session
		)
	), statuses.OK


@group_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Group)
def authorized_actions_group(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on the
	group with the requested ``id_``.
	"""

	return flask.jsonify(
		find_group_by_id(
			id_,
			flask.g.sa_session
		).get_allowed_instance_actions(flask.g.user)
	)


@group_blueprint.route("/<uuid:id_>/permissions", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", database.Group)
def delete_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the group with the requested ``id_``'s permissions."""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"edit_permissions",
		group
	)

	if "*" in group.default_for and check_if_last_default_group(group.id):
		raise exceptions.APIGroupCannotDeletePermissionsForLastDefault

	if group.permissions is None:
		raise exceptions.APIGroupPermissionsNotFound

	group.permissions.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@group_blueprint.route("/<uuid:id_>/permissions", methods=["PUT"])
@validators.validate_json(BASE_PERMISSION_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit_permissions", database.Group)
def edit_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the group with the requested ``id_``'s permissions.
	Automatically creates them if they don't exist.
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
				raise exceptions.APIGroupCannotLeavePermissionNullForLastDefault

	if group.permissions is None:
		database.GroupPermissions.create(
			flask.g.sa_session,
			group_id=group.id,
			**flask.g.json
		)

		status = statuses.CREATED
	else:
		unchanged = True

		for key, value in flask.g.json.items():
			if getattr(group.permissions, key) is not value:
				unchanged = False
				setattr(group.permissions, key, value)

		if unchanged:
			raise exceptions.APIGroupPermissionsUnchanged

		group.permissions.edited()

		status = statuses.OK

	flask.g.sa_session.commit()

	return flask.jsonify(group.permissions), status


@group_blueprint.route("/<uuid:id_>/permissions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view_permissions", database.Group)
def view_permissions(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the group with the requested ``id_``'s permissions."""

	group = find_group_by_id(
		id_,
		flask.g.sa_session
	)

	validate_permission(
		flask.g.user,
		"view_permissions",
		group
	)

	return flask.jsonify(group.permissions), statuses.OK


@group_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that the current ``flask.g.user`` is authorized to
	perform on groups without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		database.Group.get_allowed_class_actions(flask.g.user)
	), statuses.OK
