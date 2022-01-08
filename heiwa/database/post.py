"""Post models."""

from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .utils import (
	UUID,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin
)

__all__ = [
	"Post",
	"PostVote"
]


class PostVote(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""A helper model for storing :class:`.Post` votes."""

	__tablename__ = "post_votes"

	post_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"posts.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.Post.id>` of the :class:`.Post` a vote relates to."""

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` who created a vote."""

	upvote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		index=True,
		nullable=False
	)
	"""Whether or not a vote is an upvote, or a downvote, if :data:`True`, it's
	considered an upvote, otherwise, it's considered a downvote.

	.. seealso::
		:attr:`.Forum.vote_value`
	"""


class Post(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Post model."""

	__tablename__ = "posts"

	thread_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"threads.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=False
	)
	"""The :attr:`id <.Thread.id>` of the :class:`.Thread` a post is in."""

	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=False
	)
	"""The :attr:`id <.User.id>` of the :class:`.User` who created a post. This
	cannot be changed.
	"""

	subject = sqlalchemy.Column(
		sqlalchemy.String(256),
		nullable=True
	)
	"""The subject of a post."""

	content = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=False
	)
	"""A post's content."""

	vote_value = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(PostVote.upvote)
		).
		where(
			sqlalchemy.and_(
				PostVote.post_id == sqlalchemy.text("posts.id"),
				PostVote.upvote.is_(True)
			)
		).
		scalar_subquery()
		- sqlalchemy.select(
			sqlalchemy.func.count(
				PostVote.upvote
			)
		).
		where(
			sqlalchemy.and_(
				PostVote.post_id == sqlalchemy.text("posts.id"),
				PostVote.upvote.is_(False)
			)
		).
		scalar_subquery()
	)
	"""The final value of a post's votes. Upvotes will add ``1``, downvotes
	will subtract ``1``. If there are no votes at all, this will be ``0``.
	Negative numbers are allowed.

	.. seealso::
		:class:`.PostVote`
	"""

	# Shortcut
	forum = sqlalchemy.orm.relationship(
		"Forum",
		uselist=False,
		secondary="threads",
		passive_deletes="all",
		overlaps="forum",
		lazy=True
	)
	"""A post's :class:`.Thread`'s :class:`.Forum`."""

	thread = sqlalchemy.orm.relationship(
		"Thread",
		uselist=False,
		passive_deletes="all",
		overlaps="forum",
		lazy=True
	)
	"""A post's :class:`.Thread`."""

	votes = sqlalchemy.orm.relationship(
		PostVote,
		backref=sqlalchemy.orm.backref(
			"post",
			uselist=False
		),
		order_by=sqlalchemy.desc(PostVote.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)
	"""A post's votes.

	.. seealso::
		:class:`.PostVote`
	"""

	static_actions = {
		"create": lambda user: (
			Post.static_actions["view"](user) and
			user.parsed_permissions["post_create"]
		),
		"delete": lambda user: (
			Post.static_actions["view"](user) and (
				user.parsed_permissions["post_delete_own"] or
				user.parsed_permissions["post_delete_any"]
			)
		),
		"edit": lambda user: (
			Post.static_actions["view"](user) and (
				user.parsed_permissions["post_edit_own"] or
				user.parsed_permissions["post_edit_any"]
			)
		),
		"edit_vote": lambda user: (
			Post.static_actions["view"](user) and
			user.parsed_permissions["post_edit_vote"]
		),
		"move": lambda user: (
			Post.static_actions["view"](user) and (
				user.parsed_permissions["post_move_own"] or
				user.parsed_permissions["post_move_any"]
			)
		),
		"view": lambda user: user.parsed_permissions["post_view"],
		"view_vote": lambda user: Post.static_actions["view"](user)
	}
	r"""Actions :class:`User`\ s are allowed to perform on all posts, without
	any indication of which post it is.

	``create``:
		Whether or not the user can create posts. This depends on them
		being able to ``view`` them, as well as the ``post_create`` value in
		their permissions.

	``delete``:
		Whether or not a user can delete posts. This depends on them
		being able to ``view`` them, as well as either the ``post_delete_own``
		or the ``post_delete_any`` value in their permissions.

	``edit``:
		Whether or not a user can edit posts. This depends on them being able
		to ``view`` them, as well as either the ``post_edit_own`` or
		the ``post_edit_any`` value in their permissions.

	``edit_vote``:
		Whether or not a user can edit their votes on posts. This depends
		on them being able to ``view`` posts, as well as the ``post_edit_vote``
		value in their permissions.

	``move``:
		Whether or not a user can move posts. This depends on them being able
		to ``view`` them, as well as either the ``post_move_own`` or
		the ``post_move_any`` value in their permissions.

	``view``:
		Whether or not a user is allowed to view posts. This depends on the
		``post_view`` value in their permissions.

	``view_vote``:
		Whether or not a user is allowed to view their vote on posts.
		As long as they're allowed to ``view`` them, this will always be
		:data:`True` by default.

	.. seealso::
		:attr:`.Post.static_actions`

		:attr:`.Post.action_queries`
	"""

	def _instance_action_delete(self: Post, user) -> bool:
		"""Checks whether or not ``user`` is allowed to delete this post.

		:param user: The user, a :class:`.User`.

		:returns: The result of the check.
		"""

		parsed_permissions = self.forum.get_parsed_permissions(user)

		return (
			self.instance_actions["view"](self, user) and (
				(
					self.user_id == user.id and
					parsed_permissions.post_delete_own
				) or
				parsed_permissions.post_delete_any
			)
		)

	def _instance_action_edit(self: Post, user) -> bool:
		"""Checks whether or not ``user`` is allowed to edit this post.

		:param user: The user, a :class:`.User`.

		:returns: The result of the check.
		"""

		parsed_permissions = self.forum.get_parsed_permissions(user)

		return (
			self.instance_actions["view"](self, user) and (
				(
					self.user_id == user.id and
					parsed_permissions.post_edit_own
				) or
				parsed_permissions.post_edit_any
			)
		)

	def _instance_action_move(self: Post, user) -> bool:
		"""Checks whether or not ``user`` is allowed to move this post to another
		:class:`.Thread`.

		:param user: The user, a :class:`.User`.

		:returns: The result of the check.
		"""

		parsed_permissions = self.forum.get_parsed_permissions(user)

		return (
			self.instance_actions["view"](self, user) and (
				(
					self.thread.user_id == user.id and
					parsed_permissions.post_move_own
				) or
				parsed_permissions.post_move_any
			) and (
				not hasattr(self, "future_thread") or
				self.future_thread.instance_actions["move_post_to"](self, user)
			)
		)

	instance_actions = {
		"delete": _instance_action_delete,
		"edit": _instance_action_edit,
		"edit_vote": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.forum.get_parsed_permissions(user).post_edit_vote
		),
		"move": _instance_action_move,
		"view": lambda self, user: (
			self.forum.get_parsed_permissions(user).post_view
		),
		"view_vote": lambda self, user: (
			self.instance_actions["view"](self, user)
		)
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given post. Unlike
	:attr:`static_actions <.Thread.static_actions>`, this can vary by each post.

	``delete``:
		Whether or not a user is allowed to delete this post. This depends on
		them being allowed to ``view`` it, as well as them either owning it
		and having the ``post_delete_own`` forum permission, or them having
		the ``post_delete_any`` permission.

	``edit``:
		Whether or not a user is allowed to edit this post. This depends on
		them being allowed to ``view`` it, as well as them either owning it
		and having the ``post_edit_own`` forum permission, or them having
		the ``post_edit_any`` permission.

	``edit_vote``:
		Whether or not a user is allowed to edit their vote on this post.
		This depends on them being allowed to ``view`` it, as well as the
		``post_edit_vote`` forum permission.

	``move``:
		Whether or not a user is allowed to move this post to another
		:class:`.Thread`. This depends on them being allowed to ``view`` it,
		as well as them either owning it and having the ``post_move_own``
		forum permission, or them having the ``post_move_any`` permission.
		If the ``future_thread`` attribute is assigned, the user must also
		be allowed to perform the ``move_post_to`` action on that thread.

	``view``:
		Whether or not a user is allowed to view this post. This depends on
		the ``post_view`` forum permission.

	``view_vote``:
		Whether or not a user is allowed to view their votes on this post.
		As long as they have permission to ``view`` it, this will always be
		:data:`True` by default.

	.. seealso::
		:attr:`.Post.static_actions`

		:attr:`.Post.action_queries`
	"""

	@staticmethod
	def _action_query_delete(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to delete posts.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Post.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					Post.user_id == user.id,
					ForumParsedPermissions.post_delete_own.is_(True)
				),
				ForumParsedPermissions.post_delete_any.is_(True)
			)
		)

	@staticmethod
	def _action_query_edit(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to edit posts.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Post.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					Post.user_id == user.id,
					ForumParsedPermissions.post_edit_own.is_(True)
				),
				ForumParsedPermissions.post_edit_any.is_(True)
			)
		)

	@staticmethod
	def _action_query_edit_vote(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to edit their votes on posts.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Post.action_queries["view"](user),
			ForumParsedPermissions.post_edit_vote.is_(True)
		)

	@staticmethod
	def _action_query_move(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to move posts to other threads.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return sqlalchemy.and_(
			Post.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					Post.user_id == user.id,
					ForumParsedPermissions.post_move_own.is_(True)
				),
				ForumParsedPermissions.post_move_any.is_(True)
			)
		)

	@staticmethod
	def _action_query_view(user) -> sqlalchemy.sql.Selectable:
		"""Generates a selectable condition representing whether or not ``user`` is
		allowed to view posts.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .forum import ForumParsedPermissions

		return ForumParsedPermissions.post_view.is_(True)

	action_queries = {
		"delete": _action_query_delete,
		"edit": _action_query_edit,
		"edit_vote": _action_query_edit_vote,
		"move": _action_query_move,
		"view": _action_query_view,
		"view_vote": lambda user: Post.action_queries["view"](user)
	}
	"""Actions and their required permissions translated to be evaluable within
	SQL queries. Unless arbitrary additional attributes come into play, these
	permissions will generally be the same as
	:attr:`instance_actions <.Post.instance_actions>`.

	.. seealso::
		:attr:`.Post.instance_actions`

		:attr:`.Post.static_actions`
	"""

	NOTIFICATION_TYPES = (
		enums.NotificationTypes.NEW_POST_FROM_FOLLOWEE,
		enums.NotificationTypes.NEW_POST_IN_SUBSCRIBED_THREAD
	)

	def delete(
		self: Post,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Deletes all notifications associated with this post, as well as the
		post itself. If the ``session`` argument is ``None``, it's set to this
		object's session.
		"""

		from .notification import Notification

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		session.execute(
			sqlalchemy.delete(Notification).
			where(
				sqlalchemy.and_(
					Notification.type.in_(self.NOTIFICATION_TYPES),
					Notification.identifier == self.id
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self, session)

	def write(
		self: Post,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Creates a notification about this post for:

		#. Users subscribed to the parent thread.
		#. The author's followers. (Who aren't subscribed to the thread)
		"""

		from .notification import Notification
		from .user import user_follows

		# Premature session add and flush. We have to access the ID later.
		CDWMixin.write(self, session)
		session.flush()

		subscriber_ids = self.thread.get_subscriber_ids(session)

		for subscriber_id in subscriber_ids:
			Notification.create(
				session,
				user_id=subscriber_id,
				type=enums.NotificationTypes.NEW_POST_IN_SUBSCRIBED_THREAD,
				identifier=self.id
			)

		for follower_id in session.execute(
			sqlalchemy.select(user_follows.c.follower_id).
			where(
				sqlalchemy.and_(
					user_follows.c.followee_id == self.user_id,
					~user_follows.c.followee_id.in_(subscriber_ids)
				)
			)
		).scalars().all():
			Notification.create(
				session,
				user_id=follower_id,
				type=enums.NotificationTypes.NEW_POST_FROM_FOLLOWEE,
				identifier=self.id
			)

		CDWMixin.write(self, session)

	@classmethod
	def get(
		cls: Post,
		user,
		session: sqlalchemy.orm.Session,
		additional_actions: typing.Union[
			None,
			typing.Iterable[str]
		] = None,
		conditions: typing.Union[
			bool,
			sqlalchemy.sql.expression.BinaryExpression,
			sqlalchemy.sql.expression.ClauseList
		] = True,
		order_by: typing.Union[
			None,
			sqlalchemy.sql.elements.UnaryExpression
		] = None,
		limit: typing.Union[
			None,
			int
		] = None,
		offset: typing.Union[
			None,
			int
		] = None,
		ids_only: bool = False
	) -> sqlalchemy.sql.Select:
		"""Generates a selection query with permissions already handled.

		Since the posts' :class:`.Thread`'s :class:`.Forum`'s permissions may
		not be parsed, this will always emit additional queries to check.

		:param user: The user whose permissions should be evaluated.
		:param session: The SQLAlchemy session to execute additional queries with.
		:param additional_actions: Additional actions that a user must be able to
			perform on posts, other than the default ``view`` action.
		:param conditions: Any additional conditions. :data:`True` by default,
			meaning there are no conditions.
		:param order_by: An expression to order by.
		:param limit: A limit.
		:param offset: An offset.
		:param ids_only: Whether or not to only return a query for IDs.

		:returns: The query.
		"""

		from .forum import Forum, ForumParsedPermissions
		from .thread import Thread

		inner_conditions = (
			sqlalchemy.and_(
				ForumParsedPermissions.forum_id == Thread.forum_id,
				ForumParsedPermissions.user_id == user.id
			)
		)

		first_iteration = True
		post_without_parsed_forum_permissions_exists = False

		while (first_iteration or post_without_parsed_forum_permissions_exists):
			first_iteration = False

			rows = session.execute(
				sqlalchemy.select(
					cls.id,
					Thread.forum_id,
					(
						sqlalchemy.select(ForumParsedPermissions.forum_id).
						where(inner_conditions).
						exists()
					)
				).
				where(
					sqlalchemy.and_(
						conditions,
						Thread.id == Post.thread_id,
						sqlalchemy.or_(
							~(
								sqlalchemy.select(ForumParsedPermissions.forum_id).
								where(inner_conditions).
								exists()
							),
							(
								sqlalchemy.select(ForumParsedPermissions.forum_id).
								where(
									sqlalchemy.and_(
										inner_conditions,
										cls.action_queries["view"](user),
										sqlalchemy.and_(
											cls.action_queries[action](user)
											for action in additional_actions
										) if additional_actions is not None else True
									)
								).
								exists()
							)
						)
					)
				).
				order_by(order_by).
				limit(limit).
				offset(offset)
			).all()

			if len(rows) == 0:
				# No need to hit the database with a complicated query twice
				return (
					sqlalchemy.select(cls if not ids_only else cls.id).
					where(False)
				)

			post_ids = []
			unparsed_permission_forum_ids = []

			for row in rows:
				(
					post_id,
					forum_id,
					parsed_forum_permissions_exist
				) = row

				if not parsed_forum_permissions_exist:
					post_without_parsed_forum_permissions_exists = True
					unparsed_permission_forum_ids.append(forum_id)

					continue

				post_ids.append(post_id)

			if post_without_parsed_forum_permissions_exists:
				for forum in (
					session.execute(
						sqlalchemy.select(Forum).
						where(Forum.id.in_(unparsed_permission_forum_ids))
					).scalars()
				):
					forum.reparse_permissions(user)

				session.commit()

			if ids_only:
				return sqlalchemy.select(post_ids)

			return (
				sqlalchemy.select(cls).
				where(cls.id.in_(post_ids)).
				order_by(order_by)
			)
