import typing
import uuid

import flask
import sqlalchemy
import sqlalchemy.orm

from .. import (
	authentication,
	encoders,
	enums,
	exceptions,
	helpers,
	models,
	validators
)
from .helpers import (
	find_thread_by_id,
	generate_list_schema,
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
	"content": {
		"type": "string",
		"minlength": 1,
		"maxlength": 65536
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
	"content": {
		**ATTR_SCHEMAS["content"],
		"required": True
	}
}
LIST_SCHEMA = generate_list_schema(
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
			"thread_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["thread_id"],
				"minlength": 1,
				"maxlength": 32
			},
			"user_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["user_id"],
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
			}
		},
		"maxlength": 1
	},
	"$re": {
		"type": "dict",
		"schema": {
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
	user: models.User
) -> models.Post:
	"""Returns the post with the given ID. Raises `exceptions.APIPostNotFound`
	if it doesn't exist, or `flask.g.user` doesn't have permission to view it.
	If parsed permissions don't exist for the respective forum, they're
	automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		models.Thread.forum_id == models.ForumParsedPermissions.forum_id,
		models.ForumParsedPermissions.user_id == user.id
	)

	first_iteration = True

	while first_iteration or (row is not None and not row[1]):
		if not first_iteration:
			session.execute(
				sqlalchemy.select(models.Forum).
				where(models.Forum.id == row[2])
			).scalars().one().reparse_permissions(user)

			session.commit()

		first_iteration = False

		row = session.execute(
			sqlalchemy.select(
				models.Post,
				(
					sqlalchemy.select(models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				),
				models.Thread.forum_id
			).
			join(
				models.Thread.forum_id,
				models.Post.thread_id == models.Thread.id
			).
			where(
				sqlalchemy.and_(
					models.Post.id == id_,
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
									models.ForumParsedPermissions.post_view.is_(True)
								)
							).
							exists()
						)
					)
				)
			)
		).one_or_none()

	if row is None:
		raise exceptions.APIPostNotFound(id)

	return row[0]


@post_blueprint.route("", methods=["POST"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("create_post", models.Thread)
def create() -> typing.Tuple[flask.Response, int]:
	"""Creates a post with the requested `thread_id` and `content`."""

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
		raise exceptions.APIThreadLocked(thread.id)

	post = models.Post.create(
		flask.g.sa_session,
		user_id=flask.g.user.id,
		**flask.g.json
	)

	flask.g.sa_session.commit()

	return flask.jsonify(post), helpers.STATUS_CREATED


@post_blueprint.route("", methods=["GET"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("view", models.Post)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Lists all posts that match the requested filter, and `flask.g.user` has
	permission to view. If parsed permissions don't exist for their respective
	threads' forums, they're automatically calculated.
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
					models.ForumParsedPermissions.post_view.is_(True)
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
				models.Post
			)
		)

	order_column = getattr(
		models.Post,
		flask.g.json["order"]["by"]
	)

	post_without_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or post_without_forum_permissions_exists:
		first_iteration = False
		post_without_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Post,
				(
					sqlalchemy.select(models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				),
				models.Thread.forum_id
			).
			join(
				models.Thread.forum_id,
				models.Post.thread_id == models.Thread.id
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
				post_without_forum_permissions_exists = True

				flask.g.sa_session.execute(
					sqlalchemy.select(models.Forum).
					where(models.Forum.id == row[2])
				).scalars().one().reparse_permissions(flask.g.user)

		if post_without_forum_permissions_exists:
			flask.g.sa_session.commit()

	return flask.jsonify(
		[
			row[0]
			for row in rows
		]
	), helpers.STATUS_OK


@post_blueprint.route("", methods=["DELETE"])
@validators.validate_json(
	LIST_SCHEMA,
	schema_registry=SEARCH_SCHEMA_REGISTRY
)
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Post)
def mass_delete() -> typing.Tuple[flask.Response, int]:
	"""Deletes all posts that match the requested filter, and `flask.g.user` has
	permission to both view and delete. If parsed permissions don't exist for
	their respective threads' forums, they're automatically calculated.
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
					models.ForumParsedPermissions.post_view.is_(True),
					sqlalchemy.or_(
						sqlalchemy.and_(
							models.Post.id == flask.g.user.id,
							models.ForumParsedPermissions.post_delete_own.is_(True)
						),
						models.ForumParsedPermissions.post_delete_any.is_(True)
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
				models.Post
			)
		)

	order_column = getattr(
		models.Post,
		flask.g.json["order"]["by"]
	)

	post_without_forum_permissions_exists = False
	first_iteration = True

	while first_iteration or post_without_forum_permissions_exists:
		first_iteration = False
		post_without_forum_permissions_exists = False

		rows = flask.g.sa_session.execute(
			sqlalchemy.select(
				models.Post,
				(
					sqlalchemy.select(models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				),
				models.Thread.forum_id
			).
			join(
				models.Thread.forum_id,
				models.Post.thread_id == models.Thread.id
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
				post_without_forum_permissions_exists = True

				flask.g.sa_session.execute(
					sqlalchemy.select(models.Forum).
					where(models.Forum.id == row[2])
				).scalars().one().reparse_permissions(flask.g.user)

		if post_without_forum_permissions_exists:
			flask.g.sa_session.commit()

	if len(ids) != 0:
		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Post).
			where(models.Post.id.in_(ids))
		)

		flask.g.sa_session.execute(
			sqlalchemy.delete(models.Notification).
			where(
				sqlalchemy.and_(
					(
						models.Notification.type
						== enums.NotificationTypes.NEW_POST_IN_SUBSCRIBED_THREAD
					),
					models.Notification.identifier.in_(ids)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@post_blueprint.route("/<uuid:id_>", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("delete", models.Post)
def delete(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes the post with the requested `id_`."""

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

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@post_blueprint.route("/<uuid:id_>", methods=["PUT"])
@validators.validate_json(CREATE_EDIT_SCHEMA)
@authentication.authenticate_via_jwt
@requires_permission("edit", models.Post)
def edit(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Updates the post with the requested `id_` with the requested values."""

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
		raise exceptions.APIPostUnchanged(post.id)

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
			raise exceptions.APIThreadLocked(future_thread.id)

		post.thread = future_thread

	post.edited()

	flask.g.sa_session.commit()

	return flask.jsonify(post), helpers.STATUS_OK


@post_blueprint.route("/<uuid:id_>", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Post)
def view(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns the post with the requested `id_`."""

	return flask.jsonify(
		find_post_by_id(
			id_,
			flask.g.sa_session,
			flask.g.user
		)
	), helpers.STATUS_OK


@post_blueprint.route("/<uuid:id_>/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view", models.Post)
def authorized_actions_post(
	id_: uuid.UUID
) -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that `flask.g.user` is authorized to perform on the
	post with the requested `id_`.
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
@requires_permission("edit_vote", models.Post)
def create_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Creates a vote from `flask.g.user` for the post with the requested `id_`,
	or updates the existing one. It can either be a downvote or an upvote.
	(`upvote` -> `True` or `False`)
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
		sqlalchemy.select(models.PostVote).
		where(
			sqlalchemy.and_(
				models.PostVote.post_id == post.id,
				models.PostVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if (
		vote is not None and
		vote.upvote is flask.g.json["upvote"]
	):
		raise exceptions.APIPostVoteUnchanged(flask.g.json["upvote"])

	if vote is None:
		vote = models.PostVote.create(
			flask.g.sa_session,
			post_id=post.id,
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


@post_blueprint.route("/<uuid:id_>/vote", methods=["DELETE"])
@authentication.authenticate_via_jwt
@requires_permission("edit_vote", models.Post)
def delete_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Deletes `flask.g.user`'s vote on the post with the requested `id_`,
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
		sqlalchemy.select(models.PostVote).
		where(
			sqlalchemy.and_(
				models.PostVote.post_id == post.id,
				models.PostVote.user_id == flask.g.user.id
			)
		)
	).scalars().one_or_none()

	if existing_vote is None:
		raise exceptions.APIPostVoteNotFound(id)

	existing_vote.delete()

	flask.g.sa_session.commit()

	return flask.jsonify({}), helpers.STATUS_NO_CONTENT


@post_blueprint.route("/<uuid:id_>/vote", methods=["GET"])
@authentication.authenticate_via_jwt
@requires_permission("view_vote", models.Post)
def view_vote(id_: uuid.UUID) -> typing.Tuple[flask.Response, int]:
	"""Returns `flask.g.user`'s vote on the post with the requested `id_`."""

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
			models.PostVote,
			(
				post.id,
				flask.g.user.id
			)
		)
	), helpers.STATUS_OK


@post_blueprint.route("/authorized-actions", methods=["GET"])
@authentication.authenticate_via_jwt
def authorized_actions_root() -> typing.Tuple[flask.Response, int]:
	"""Returns all actions that `flask.g.user` is authorized to perform on posts
	without any knowledge on which one they'll be done on.
	"""

	return flask.jsonify(
		models.Post.get_allowed_class_actions(flask.g.user)
	)
