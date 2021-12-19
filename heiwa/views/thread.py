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
	find_forum_by_id,
	find_thread_by_id,
	generate_search_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_permission
)

__all__ = ["thread_blueprint"]

thread_blueprint = flask.Blueprint(
	"thread",
	__name__,
	url_prefix="/threads"
)
thread_blueprint.json_encoder = encoders.JSONEncoder

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
	"forum_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"user_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"is_locked": {
		"type": "boolean"
	},
	"is_pinned": {
		"type": "boolean"
	},
	"tags": {
		"type": "list",
		"check_with": "has_no_duplicates",
		"schema": {
			"type": "string",
			"minlength": 1,
			"maxlength": 128
		}
	},
	"name": {
		"type": "string",
		"minlength": 1,
		"maxlength": 128
	},
	"content": {
		"type": "string",
		"minlength": 1,
		"maxlength": 65536
	},
	"vote_value": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"post_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"subscriber_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"last_post_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	}
}

CREATE_EDIT_SCHEMA = {
	"forum_id": {
		**ATTR_SCHEMAS["forum_id"],
		"required": True
	},
	"is_locked": {
		**ATTR_SCHEMAS["is_locked"],
		"required": True
	},
	"is_pinned": {
		**ATTR_SCHEMAS["is_pinned"],
		"required": True
	},
	"tags": {
		**ATTR_SCHEMAS["tags"],
		"required": True
	},
	"name": {
		**ATTR_SCHEMAS["name"],
		"required": True
	},
	"content": {
		**ATTR_SCHEMAS["content"],
		"required": True
	}
}
SEARCH_SCHEMA = generate_search_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"edit_count",
		"vote_value",
		"post_count",
		"subscriber_count",
		"last_post_timestamp"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"],
	"vote_value": ATTR_SCHEMAS["vote_value"],
	"post_count": ATTR_SCHEMAS["post_count"],
	"subscriber_count": ATTR_SCHEMAS["subscriber_count"],
	"last_post_timestamp": ATTR_SCHEMAS["last_post_timestamp"]
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
			"forum_id": ATTR_SCHEMAS["forum_id"],
			"user_id": ATTR_SCHEMAS["user_id"],
			"is_locked": ATTR_SCHEMAS["is_locked"],
			"is_pinned": ATTR_SCHEMAS["is_pinned"],
			"tags": ATTR_SCHEMAS["tags"],
			"name": ATTR_SCHEMAS["name"],
			"content": ATTR_SCHEMAS["content"],
			"vote_value": ATTR_SCHEMAS["vote_value"],
			"post_count": ATTR_SCHEMAS["post_count"],
			"subscriber_count": ATTR_SCHEMAS["subscriber_count"],
			"last_post_timestamp": {
				**ATTR_SCHEMAS["last_post_timestamp"],
				"nullable": True
			}
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
			"forum_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["forum_id"],
				"minlength": 1,
				"maxlength": 32
			},
			"user_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["user_id"],
				"minlength": 1,
				"maxlength": 32
			},
			"tags": {
				"type": "list",
				"schema": ATTR_SCHEMAS["tags"],
				"minlength": 1,
				"maxlength": 32
			},
			"name": {
				"type": "list",
				"schema": ATTR_SCHEMAS["name"],
				"minlength": 1,
				"maxlength": 32
			},
			"content": {
				"type": "list",
				"schema": ATTR_SCHEMAS["content"],
				"minlength": 1,
				"maxlength": 32
			},
			"vote_value": {
				"type": "list",
				"schema": ATTR_SCHEMAS["vote_value"],
				"minlength": 1,
				"maxlength": 32
			},
			"post_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["post_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"subscriber_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["subscriber_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"last_post_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["last_post_timestamp"],
					"nullable": True
				},
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
			"content": {
				**ATTR_SCHEMAS["content"],
				"check_with": "is_valid_regex"
			}
		},
		"maxlength": 1
	}
})


def get_thread_ids_from_search(
	conditions: typing.Union[
		sqlalchemy.sql.expression.BinaryExpression,
		sqlalchemy.sql.expression.ClauseList
	],
	inner_conditions: typing.Union[
		sqlalchemy.sql.expression.BinaryExpression,
		sqlalchemy.sql.expression.ClauseList
	]
) -> typing.List[uuid.UUID]:
	"""Returns the IDs of threads that match the current search query, and
	``conditions``.
	"""
	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				models.Thread
			)
		)

	order_column = getattr(
		models.Thread,
		flask.g.json["order"]["by"]
	)

	thread_without_parsed_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or thread_without_parsed_forum_permissions_exists:
		first_iteration = False
		thread_without_parsed_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Thread,
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

		thread_ids = []

		for row in rows:
			thread_id, parsed_forum_permissions_exist = row

			if not parsed_forum_permissions_exist:
				thread_without_parsed_forum_permissions_exists = True

				thread_id.forum.reparse_permissions(flask.g.user)

			thread_ids.append(thread_id)

		if thread_without_parsed_forum_permissions_exists:
			flask.g.sa_session.commit()

	return thread_ids


@thread_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create_thread", models.Forum)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a thread with the requested ``forum_id``, locked status
	(``is_locked``), pinned status (``is_pinned``), ``name`` and ``content``.
	"""

	forum = find_forum_by_id(
		flask.g.json["forum_id"],
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"create_thread",
		forum
	)

	if flask.g.json["is_locked"]:
		validate_permission(
			flask.g.user,
			"create_thread_locked",
			forum
		)

	if flask.g.json["is_pinned"]:
		validate_permission(
			flask.g.user,
			"create_thread_pinned",
			forum
		)

	thread = models.Thread.create(
		flask.g.sa_session,
		user_id=flask.g.user.id,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(thread), helpers.STATUS_CREATED


@thread_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.Thread)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all threads that match the requested filter if there is one, and
	``flask.g.user`` has permission to view. If parsed permissions don't exist
	for their respective forums, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		models.Thread.forum_id == models.ForumParsedPermissions.forum_id,
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
					models.ForumParsedPermissions.thread_view.is_(True)
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
				models.Thread
			)
		)

	order_column = getattr(
		models.Thread,
		flask.g.json["order"]["by"]
	)

	thread_without_parsed_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or thread_without_parsed_forum_permissions_exists:
		first_iteration = False
		thread_without_parsed_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Thread,
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

		threads = []

		for row in rows:
			thread, parsed_forum_permissions_exist = row

			if not parsed_forum_permissions_exist:
				thread_without_parsed_forum_permissions_exists = True

				thread.forum.reparse_permissions(flask.g.user)

			threads.append(thread)

		if thread_without_parsed_forum_permissions_exists:
			flask.g.sa_session.commit()

	return flask.jsonify(threads), helpers.STATUS_OK


@thread_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Thread)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all threads that match the requested filter if there is one, and
	``flask.g.user`` has permission to both view and delete. If parsed permissions
	don't exist for their respective forums, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		models.Thread.forum_id == models.ForumParsedPermissions.forum_id,
		models.ForumParsedPermissions.user_id == flask.g.user.id
	)

	thread_ids = get_thread_ids_from_search(
		sqlalchemy.or_(
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
						models.ForumParsedPermissions.thread_view.is_(True),
						sqlalchemy.or_(
							sqlalchemy.and_(
								models.Thread.user_id == flask.g.user.id,
								models.ForumParsedPermissions.thread_delete_own.is_(True)
							),
							models.ForumParsedPermissions.thread_delete_any.is_(True)
						)
					)
				).
				exists()
			)
		),
		inner_conditions
	)

	if len(thread_ids) != 0:
		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Notification).
			where(
				sqlalchemy.or_(
					sqlalchemy.and_(
						models.Notification.type.in_(models.Thread.NOTIFICATION_TYPES),
						models.Notification.identifier.in_(thread_ids)
					),
					sqlalchemy.and_(
						models.Notification.type.in_(models.Post.NOTIFICATION_TYPES),
						models.Notification.identifier.in_(
							sqlalchemy.select(models.Post.id).
							where(models.Post.thread_id.in_(thread_ids))
						)
					)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Thread).
			where(models.Thread.id.in_(thread_ids))
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@thread_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Thread)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the thread with the requested ``id_``."""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"delete",
		thread
	)

	thread.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@thread_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", models.Thread)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the thread with the requested ``id_`` with the requested values."""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit",
		thread
	)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(thread, key) != value:
			unchanged = False
			setattr(thread, key, value)

	if unchanged:
		raise exceptions.APIThreadUnchanged

	if thread.forum_id != flask.g.json["forum_id"]:
		future_forum = find_forum_by_id(
			flask.g.json["forum_id"],
			flask.g.sa_session,
			flask.g.user
		)

		thread.future_forum = future_forum

		validate_permission(
			flask.g.user,
			"move",
			thread
		)

		thread.forum = future_forum

	if thread.is_locked is not flask.g.json["is_locked"]:
		validate_permission(
			flask.g.user,
			"edit_lock",
			thread
		)

	if thread.is_pinned is not flask.g.json["is_pinned"]:
		validate_permission(
			flask.g.user,
			"edit_pin",
			thread
		)

	thread.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(thread), helpers.STATUS_OK


@thread_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Thread)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the thread with the requested ``id_``."""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	return flask.jsonify(thread), helpers.STATUS_OK


@thread_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Thread)
def authorized_actions_thread(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on the
	thread with the requested ``id_``.
	"""

	return flask.jsonify(
		find_thread_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		).get_allowed_instance_actions(flask.g.user)
	)


@thread_blueprint.route("/<uuid:id_old>/merge/<uuid:id_new>", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("merge", models.Thread)
def merge(
	id_old: uuid.UUID,
	id_new: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Moves all posts from the thread with the given ``id_old`` to the one with
	the ``id_new``, then deletes the old thread.
	"""

	old_thread = find_thread_by_id(
		id_old,
		flask.g.sa_session,
		flask.g.user
	)
	new_thread = find_thread_by_id(
		id_new,
		flask.g.sa_session,
		flask.g.user
	)

	old_thread.future_thread = new_thread

	validate_permission(
		flask.g.user,
		"merge",
		old_thread
	)

	flask.g.sa_session.execute(
		sqlalchemy.update(models.Post).
		where(models.Post.id == old_thread.id).
		values(id=new_thread.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(models.ThreadVote).
		where(models.ThreadVote.thread_id == old_thread.id).
		values(thread_id=new_thread.id)
	)
	flask.g.sa_session.execute(
		sqlalchemy.update(models.Notification).
		where(
			sqlalchemy.and_(
				models.Notification.type.in_(models.Thread.NOTIFICATION_TYPES),
				models.Notification.identifier == old_thread.id
			)
		).
		values(
			identifier=new_thread.id
		)
	)

	old_thread.delete()
	new_thread.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(new_thread), helpers.STATUS_OK


@thread_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", models.Thread)
def create_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a subscription for ``flask.g.user`` to the thread with the
	requested ``id_``.
	"""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_subscription",
		thread
	)

	if (
		flask.g.sa_session.execute(
			sqlalchemy.select(models.thread_subscribers).
			where(
				sqlalchemy.and_(
					models.thread_subscribers.c.thread_id == thread.id,
					models.thread_subscribers.c.user_id == flask.g.user.id
				)
			)
		).scalars().one_or_none()
	) is not None:
		raise exceptions.APIThreadSubscriptionAlreadyExists

	flask.g.sa_session.execute(
		sqlalchemy.insert(models.thread_subscribers).
		values(
			thread_id=thread.id,
			user_id=flask.g.user.id
		)
	)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@thread_blueprint.route("/<uuid:id_>/subscription", methods=["PUT"])
@authentication.authenticate_via_jwt
@requires_permission("edit_subscription", models.Thread)
def delete_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Removes ``flask.g.user``'s subscription to the thread with the requested
	``id_``.
	"""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_subscription",
		thread
	)

	existing_subscription = flask.g.sa_session.execute(
		sqlalchemy.select(models.thread_subscribers).
		where(
			sqlalchemy.and_(
				models.thread_subscribers.c.thread_id == thread.id,
				models.thread_subscribers.c.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_subscription is None:
		raise exceptions.APIThreadSubscriptionNotFound

	flask.g.sa_session.delete(existing_subscription)

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@thread_blueprint.route("/<uuid:id_>/subscription", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Thread)
def view_subscription(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns whether or not ``flask.g.user`` is subscribed to the thread with the
	requested ``id_``.
	"""

	return flask.jsonify(
		flask.g.sa_session.execute(
			sqlalchemy.select(models.thread_subscribers.c.thread_id).
			where(
				sqlalchemy.and_(
					models.thread_subscribers.c.thread_id == find_thread_by_id(
						id_,
						flask.g.sa_session,
						flask.g.user
					).id,
					models.thread_subscribers.c.user_id == flask.g.user.id
				)
			).
			exists().
			select()
		).scalars().one()
	)


@thread_blueprint.route("/<uuid:id_>/vote", methods=["PUT"])
@validators.validate_json({
	"upvote": {
		"type": "boolean",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_vote", models.Thread)
def create_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a vote from ``flask.g.user`` for the thread with the requested
	``id_``, or updates the existing one. It can either be a downvote or an
	upvote. (``upvote`` -> ``True`` or ``False``)
	"""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_vote",
		thread
	)

	vote = flask.g.sa_session.execute(
		sqlalchemy.select(models.ThreadVote).
		where(
			sqlalchemy.and_(
				models.ThreadVote.thread_id == thread.id,
				models.ThreadVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if (
		vote is not None and
		vote.upvote is flask.g.json["upvote"]
	):
		raise exceptions.APIThreadVoteUnchanged

	if vote is None:
		vote = models.ThreadVote.create(
			flask.g.sa_session,
			thread_id=thread.id,
			user_id=flask.g.user.id,
			upvote=flask.g.json["upvote"]
		)

		status = helpers.STATUS_CREATED
	else:
		vote.upvote = flask.g.json["upvote"]

		vote.edited()

		status = helpers.STATUS_OK

	flask.g.sa_session.commit()

	return flask.jsonify(vote), status


@thread_blueprint.route("/<uuid:id_>/vote", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_vote", models.Thread)
def delete_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes ``flask.g.user``'s vote on the thread with the requested ``id_``,
	if there is one.
	"""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_vote",
		thread
	)

	existing_vote = flask.g.sa_session.execute(
		sqlalchemy.select(models.ThreadVote).
		where(
			sqlalchemy.and_(
				models.ThreadVote.thread_id == thread.id,
				models.ThreadVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_vote is None:
		raise exceptions.APIThreadVoteNotFound

	existing_vote.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@thread_blueprint.route("/<uuid:id_>/vote", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view_vote", models.Thread)
def view_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns ``flask.g.user``'s vote on the thread with the requested
	``id_``.
	"""

	thread = find_thread_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"view_vote",
		thread
	)

	return flask.jsonify(
		flask.g.sa_session.get(
			models.ThreadVote,
			(
				thread.id,
				flask.g.user.id
			)
		)
	), helpers.STATUS_OK


@thread_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on
	threads without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		models.Thread.get_allowed_class_actions(flask.g.user)
	), helpers.STATUS_OK
