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
	"""A ``Post`` helper model for storing votes.

	Contains:

	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A ``post_id`` column, associating the instance with a ``Post``.
	#. A ``user_id`` column, associating the instance with a ``User``.
	#. An ``upvote`` column, signifying whether this is a downvote or an upvote.
	"""

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
	user_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)

	upvote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		index=True,
		nullable=False
	)


class Post(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Post model.

	Contains:

	#. An ``id`` column from the ``IdMixin``.
	#. A ``creation_timestamp`` column from the ``CreationTimestampMixin``.
	#. ``edit_timestamp`` and ``edit_count`` columns from the ``EditInfoMixin``.
	#. A ``thread_id`` foreign key column, associating this post with its
	   ``Thread``.
	#. A ``user_id`` foreign key column, associating this post with its author,
	   a ``User``.
	#. A ``content`` column.
	#. A dynamic ``vote_value`` column, corresponding to the total count of this
	   post's upvotes, with the downvotes' count subtracted.
	"""

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

	subject = sqlalchemy.Column(
		sqlalchemy.String(256),
		nullable=True
	)
	content = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=False
	)

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

	# Shortcut
	# This can probably be better
	forum = sqlalchemy.orm.relationship(
		"Forum",
		uselist=False,
		secondary="threads",
		passive_deletes="all",
		overlaps="forum",
		lazy=True
	)

	thread = sqlalchemy.orm.relationship(
		"Thread",
		uselist=False,
		passive_deletes="all",
		overlaps="forum",
		lazy=True
	)

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

	static_actions = {
		"create": lambda user: (
			Post.instance_actions["view"](self, user) and
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
	""" TODO """

	instance_actions = {
		"delete": lambda self, user: (
			self.instance_actions["view"](self, user) and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).post_delete_own
				) or
				self.forum.get_parsed_permissions(user).post_delete_any
			)
		),
		"edit": lambda self, user: (
			self.instance_actions["view"](self, user) and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).post_edit_own
				) or
				self.forum.get_parsed_permissions(user).post_edit_any
			)
		),
		"edit_vote": lambda self, user: (
			self.instance_actions["view"](self, user) and
			self.forum.get_parsed_permissions(user).post_edit_vote
		),
		"move": lambda self, user: (
			self.instance_actions["view"](self, user) and (
				(
					self.thread.user_id == user.id and
					self.forum.get_parsed_permissions(user).post_move_own
				) or
				self.forum.get_parsed_permissions(user).post_move_any
			) and (
				not hasattr(self, "future_thread") or
				self.future_thread.instance_actions["move_post_to"](self, user)
			)
		),
		"view": lambda self, user: (
			self.forum.get_parsed_permissions(user).post_view
		),
		"view_vote": lambda self, user: (
			self.instance_actions["view"](self, user)
		)
	}
	""" TODO """

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
