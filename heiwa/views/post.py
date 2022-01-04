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
	SEARCH_MAX_IN_LIST_LENGTH,
	find_thread_by_id,
	generate_parsed_forum_permissions_exist_query,
	generate_search_schema,
	generate_search_schema_registry,
	parse_search,
	requires_permission,
	validate_permission
)

__all__ = ["post_blueprint"]

post_blueprint = flask.Blueprint(
	"post",
	__name__,
	url_prefix="/posts"
)
post_blueprint.json_encoder = encoders.JSONEncoder

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
	"thread_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"user_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"subject": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.Post.subject.property.columns[0].type.length
	},
	"content": {
		"type": "string",
		"minlength": 1,
		"maxlength": database.Post.content.property.columns[0].type.length
	},
	"vote_value": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	}
}

CREATE_EDIT_SCHEMA = {
	"thread_id": {
		**ATTR_SCHEMAS["thread_id"],
		"required": True
	},
	"subject": {
		**ATTR_SCHEMAS["subject"],
		"nullable": True,
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
		"vote_value"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"],
	"vote_value": ATTR_SCHEMAS["vote_value"]
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
			"thread_id": ATTR_SCHEMAS["thread_id"],
			"user_id": ATTR_SCHEMAS["user_id"],
			"subject": {
				**ATTR_SCHEMAS["subject"],
				"nullable": True
			},
			"content": ATTR_SCHEMAS["content"],
			"vote_value": ATTR_SCHEMAS["vote_value"]
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
			"thread_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["thread_id"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"user_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["user_id"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"subject": {
				"type": "list",
				"schema": ATTR_SCHEMAS["subject"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"content": {
				"type": "list",
				"schema": ATTR_SCHEMAS["content"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			},
			"vote_value": {
				"type": "list",
				"schema": ATTR_SCHEMAS["vote_value"],
				"minlength": 2,
				"maxlength": SEARCH_MAX_IN_LIST_LENGTH
			}
		},
		"maxlength": 1
	},
	"$re": {
		"type": "dict",
		"schema": {
			"subject": {
				**ATTR_SCHEMAS["subject"],
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


def find_post_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: database.User
) -> database.Post:
	"""Returns the post with the given ID. Raises ``exceptions.APIPostNotFound``
	if it doesn't exist, or ``flask.g.user`` doesn't have permission to view it.
	If parsed permissions don't exist for the respective forum, they're
	automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		database.Thread.forum_id == database.ForumParsedPermissions.forum_id,
		database.ForumParsedPermissions.user_id == user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				database.Post,
				parsed_forum_permissions_exist_query,
				database.Thread.forum_id
			).
			join(
				database.Thread.forum_id,
				database.Post.thread_id == database.Thread.id
			).
			where(
				sqlalchemy.and_(
					database.Post.id == id_,
					sqlalchemy.or_(
						~parsed_forum_permissions_exist_query,
						generate_parsed_forum_permissions_exist_query(
							sqlalchemy.and_(
								inner_conditions,
								database.ForumParsedPermissions.post_view.is_(True)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is not None:
			post, parsed_forum_permissions_exist, forum_id = row

			if parsed_forum_permissions_exist:
				break

			session.execute(
				sqlalchemy.select(database.Forum).
				where(database.Forum.id == forum_id)
			).scalars().one().reparse_permissions(user)

			session.commit()
		else:
			raise exceptions.APIPostNotFound

	return post


def get_post_ids_from_search(
	conditions: typing.Union[
		sqlalchemy.sql.expression.BinaryExpression,
		sqlalchemy.sql.expression.ClauseList
	],
	parsed_forum_permissions_exist_query: sqlalchemy.sql.selectable.Exists
) -> typing.List[uuid.UUID]:
	"""Returns the IDs of posts that match the current search query, and
	``conditions``.
	"""

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Post
			)
		)

	order_column = getattr(
		database.Post,
		flask.g.json["order"]["by"]
	)

	post_without_parsed_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or post_without_parsed_forum_permissions_exists:
		first_iteration = False
		post_without_parsed_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				database.Post.id,
				parsed_forum_permissions_exist_query,
				database.Thread.forum_id
			).
			join(
				database.Thread.forum_id,
				database.Post.thread_id == database.Thread.id
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

		post_ids = []

		for row in rows:
			post_id, parsed_forum_permissions_exist, forum_id = row

			if not parsed_forum_permissions_exist:
				post_without_parsed_forum_permissions_exists = True

				flask.g.sa_session.execute(
					sqlalchemy.select(database.Forum).
					where(database.Forum.id == forum_id)
				).scalars().one().reparse_permissions(flask.g.user)

			post_ids.append(post_id)

		if post_without_parsed_forum_permissions_exists:
			flask.g.sa_session.commit()

	return post_ids


@post_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create_post", database.Thread)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a post with the requested ``thread_id``, ``subject`` and
	``content``.
	"""

	thread = find_thread_by_id(
		flask.g.json["thread_id"],
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"create_post",
		thread
	)

	if thread.is_locked:
		raise exceptions.APIThreadLocked

	post = database.Post.create(
		flask.g.sa_session,
		user_id=flask.g.user.id,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(post), statuses.CREATED


@post_blueprint.route("", methods=["GET"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", database.Post)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all posts that match the requested filter if there is one, and
	``flask.g.user`` has permission to view. If parsed permissions don't exist
	for their respective threads' forums, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		database.Thread.forum_id == database.ForumParsedPermissions.forum_id,
		database.ForumParsedPermissions.user_id == flask.g.user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	conditions = sqlalchemy.or_(
		~parsed_forum_permissions_exist_query,
		generate_parsed_forum_permissions_exist_query(
			sqlalchemy.and_(
				inner_conditions,
				database.ForumParsedPermissions.post_view.is_(True)
			)
		)
	)

	if "filter" in flask.g.json:
		conditions = sqlalchemy.and_(
			conditions,
			parse_search(
				flask.g.json["filter"],
				database.Post
			)
		)

	order_column = getattr(
		database.Post,
		flask.g.json["order"]["by"]
	)

	post_without_parsed_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or post_without_parsed_forum_permissions_exists:
		first_iteration = False
		post_without_parsed_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				database.Post,
				parsed_forum_permissions_exist_query,
				database.Thread.forum_id
			).
			join(
				database.Thread.forum_id,
				database.Post.thread_id == database.Thread.id
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

		posts = []

		for row in rows:
			post, parsed_forum_permissions_exist, forum_id = row

			if not parsed_forum_permissions_exist:
				post_without_parsed_forum_permissions_exists = True

				flask.g.sa_session.execute(
					sqlalchemy.select(database.Forum).
					where(database.Forum.id == forum_id)
				).scalars().one().reparse_permissions(flask.g.user)

			posts.append(post)

		if post_without_parsed_forum_permissions_exists:
			flask.g.sa_session.commit()

	return flask.jsonify(posts), statuses.OK


@post_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	SEARCH_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Post)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all posts that match the requested filter if there is one, and
	``flask.g.user`` has permission to both view and delete. If parsed permissions
	don't exist for their respective threads' forums, they're automatically
	calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		database.Thread.forum_id == database.ForumParsedPermissions.forum_id,
		database.ForumParsedPermissions.user_id == flask.g.user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	post_ids = get_post_ids_from_search(
		sqlalchemy.or_(
			~parsed_forum_permissions_exist_query,
			generate_parsed_forum_permissions_exist_query(
				sqlalchemy.and_(
					inner_conditions,
					database.ForumParsedPermissions.post_view.is_(True),
					sqlalchemy.or_(
						sqlalchemy.and_(
							database.Post.id == flask.g.user.id,
							database.ForumParsedPermissions.post_delete_own.is_(True)
						),
						database.ForumParsedPermissions.post_delete_any.is_(True)
					)
				)
			)
		),
		parsed_forum_permissions_exist_query
	)

	if len(post_ids) != 0:
		flask.g.sa_session.execute(
			sqlalchemy.delete(database.Notification).
			where(
				sqlalchemy.and_(
					database.Notification.type.in_(database.Post.NOTIFICATION_TYPES),
					database.Notification.identifier.in_(post_ids)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		flask.g.sa_session.execute(
			sqlalchemy.delete(database.Post).
			where(database.Post.id.in_(post_ids))
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@post_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	{
		**SEARCH_SCHEMA,
		"values": {
			"type": "dict",
			"minlength": 1,
			"schema": {
				"thread_id": {
					**ATTR_SCHEMAS["thread_id"],
					"required": False
				},
				"subject": {
					**ATTR_SCHEMAS["subject"],
					"nullable": True,
					"required": False
				},
				"content": {
					**ATTR_SCHEMAS["content"],
					"required": False
				}
			}
		}
	},
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Post)
def mass_edit() -> typing.Tuple[flask.Response, int]:
	"""Updates all posts matching the requested filter if there is one, and
	``flask.g.user`` has permission to both view and delete, with the requested
	values. If parsed permissions don't exist for their respective threads'
	forums, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		database.Thread.forum_id == database.ForumParsedPermissions.forum_id,
		database.ForumParsedPermissions.user_id == flask.g.user.id
	)

	parsed_forum_permissions_exist = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	post_ids = get_post_ids_from_search(
		sqlalchemy.or_(
			~parsed_forum_permissions_exist,
			generate_parsed_forum_permissions_exist_query(
				sqlalchemy.and_(
					inner_conditions,
					database.ForumParsedPermissions.post_view.is_(True),
					sqlalchemy.or_(
						sqlalchemy.and_(
							database.Post.id == flask.g.user.id,
							database.ForumParsedPermissions.post_edit_own.is_(True)
						),
						database.ForumParsedPermissions.post_edit_any.is_(True)
					)
				)
			)
		),
		parsed_forum_permissions_exist
	)

	if len(post_ids) != 0:
		flask.g.sa_session.execute(
			sqlalchemy.update(database.Post).
			where(database.Post.id.in_(post_ids)).
			values(**flask.g.json["values"])
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@post_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", database.Post)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the post with the requested ``id_``."""

	post = find_post_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"delete",
		post
	)

	post.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@post_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", database.Post)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the post with the requested ``id_`` with the requested values."""

	post = find_post_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit",
		post
	)

	unchanged = True

	for key, value in flask.g.json.items():
		if getattr(post, key) != value:
			unchanged = False
			setattr(post, key, value)

	if unchanged:
		raise exceptions.APIPostUnchanged

	if post.thread_id != flask.g.json["thread_id"]:
		future_thread = find_thread_by_id(
			flask.g.json["thread_id"],
			flask.g.sa_session,
			flask.g.user
		)

		post.future_thread = future_thread

		validate_permission(
			flask.g.user,
			"move",
			post
		)

		if future_thread.is_locked:
			raise exceptions.APIThreadLocked

		post.thread = future_thread

	post.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(post), statuses.OK


@post_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Post)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the post with the requested ``id_``."""

	return flask.jsonify(
		find_post_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		)
	), statuses.OK


@post_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", database.Post)
def authorized_actions_post(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on the
	post with the requested ``id_``.
	"""

	return flask.jsonify(
		find_post_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		).get_allowed_instance_actions(flask.g.user)
	)


@post_blueprint.route("/<uuid:id_>/vote", methods=["PUT"])
@validators.validate_json({
	"upvote": {
		"type": "boolean",
		"required": True
	}
})
@authentication.authenticate_via_jwt
@requires_permission("edit_vote", database.Post)
def create_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a vote from ``flask.g.user`` for the post with the requested
	``id_``, or updates the existing one. It can either be a downvote or an
	upvote. (``upvote`` -> ``True`` or ``False``)
	"""

	post = find_post_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_vote",
		post
	)

	vote = flask.g.sa_session.execute(
		sqlalchemy.select(database.PostVote).
		where(
			sqlalchemy.and_(
				database.PostVote.post_id == post.id,
				database.PostVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if (
		vote is not None and
		vote.upvote is flask.g.json["upvote"]
	):
		raise exceptions.APIPostVoteUnchanged

	if vote is None:
		vote = database.PostVote.create(
			flask.g.sa_session,
			post_id=post.id,
			user_id=flask.g.user.id,
			upvote=flask.g.json["upvote"]
		)

		status = statuses.CREATED
	else:
		vote.upvote = flask.g.json["upvote"]

		vote.edited()

		status = statuses.OK

	flask.g.sa_session.commit()

	return flask.jsonify(vote), status


@post_blueprint.route("/<uuid:id_>/vote", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_vote", database.Post)
def delete_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes ``flask.g.user``'s vote on the post with the requested ``id_``,
	if there is one.
	"""

	post = find_post_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"edit_vote",
		post
	)

	existing_vote = flask.g.sa_session.execute(
		sqlalchemy.select(database.PostVote).
		where(
			sqlalchemy.and_(
				database.PostVote.post_id == post.id,
				database.PostVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_vote is None:
		raise exceptions.APIPostVoteNotFound

	existing_vote.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), statuses.NO_CONTENT


@post_blueprint.route("/<uuid:id_>/vote", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view_vote", database.Post)
def view_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns ``flask.g.user``'s vote on the post with the requested ``id_``."""

	post = find_post_by_id(
		id_,
		flask.g.sa_session,
		flask.g.user
	)

	validate_permission(
		flask.g.user,
		"view_vote",
		post
	)

	return flask.jsonify(
		flask.g.sa_session.get(
			database.PostVote,
			(
				post.id,
				flask.g.user.id
			)
		)
	), statuses.OK


@post_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that ``flask.g.user`` is authorized to perform on posts
	without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		database.Post.get_allowed_static_actions(flask.g.user)
	), statuses.OK
