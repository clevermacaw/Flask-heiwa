"""Models and tables for threads."""

from __future__ import annotations

import typing
import uuid

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
	"Thread",
	"ThreadVote",
	"thread_subscribers"
]


class ThreadVote(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	r"""A model for storing votes on :class:`.Thread`\ s."""

	__tablename__ = "thread_votes"

	thread_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"threads.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
	"""The :attr:`id <.Thread.id>` of the :class:`.Thread` a vote belongs to."""

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
		:attr:`.Thread.vote_value`
	"""


thread_subscribers = sqlalchemy.Table(
	"thread_subscribers",
	Base.metadata,
	sqlalchemy.Column(
		"thread_id",
		UUID,
		sqlalchemy.ForeignKey(
			"threads.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	),
	sqlalchemy.Column(
		"user_id",
		UUID,
		sqlalchemy.ForeignKey(
			"users.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		primary_key=True
	)
)


class Thread(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Thread model."""

	__tablename__ = "threads"

	forum_id = sqlalchemy.Column(
		UUID,
		sqlalchemy.ForeignKey(
			"forums.id",
			ondelete="CASCADE",
			onupdate="CASCADE"
		),
		index=True,
		nullable=False
	)
	"""The :attr:`id <.Forum.id>` of the :class:`.Forum` a thread is in. This
	can be changed after the thread has been created, as long as the user
	attempting to do so has sufficient permissions.
	"""

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
	"""The :attr:`id <.User.id>` of the :class:`.User` who created a thread."""

	is_locked = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	"""Whether or not a thread has been locked. :data:`False` by default. If
	:data:`True`, creating any new posts in the thread will be disabled for
	everyone, including administrators.
	"""

	is_pinned = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	"""Whether or not a thread is pinned. :data:`False` by default. If
	:data:`True`, the thread should float to the top of lists on frontend
	programs and be marked as such, or even appear in a separate section.
	This, however, is not mandatory and API endpoints for listing threads will
	not apply this order by default.
	"""

	tags = sqlalchemy.Column(
		sqlalchemy.ARRAY(sqlalchemy.String(128)),
		nullable=False
	)
	"""A thread's tags. For example, when a thread is related to tech support,
	the tags can be ``tech support`` and ``help requested``.
	"""

	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	"""A thread's name."""

	content = sqlalchemy.Column(
		sqlalchemy.String(65536),
		nullable=False
	)
	"""A thread's content. Generally, this will often be shown as the first post
	in a thread.
	"""

	vote_value = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(ThreadVote.upvote)
		).
		where(
			sqlalchemy.and_(
				ThreadVote.thread_id == sqlalchemy.text("threads.id"),
				ThreadVote.upvote.is_(True)
			)
		).
		scalar_subquery()
		- sqlalchemy.select(
			sqlalchemy.func.count(
				ThreadVote.upvote
			)
		).
		where(
			sqlalchemy.and_(
				ThreadVote.thread_id == sqlalchemy.text("threads.id"),
				ThreadVote.upvote.is_(False)
			)
		).
		scalar_subquery()
	)
	"""The final value of a thread's votes. Upvotes will add ``1``, downvotes
	will subtract ``1``. If there are no votes at all, this will be ``0``.
	Negative numbers are allowed.

	.. seealso::
		:class:`.ThreadVote`
	"""

	post_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(sqlalchemy.text("posts.id"))
		).
		select_from(sqlalchemy.text("posts")).
		where(
			sqlalchemy.text("posts.thread_id = threads.id")
		).
		scalar_subquery()
	)
	r"""The amount of :class:`.Post`\ s in a thread."""

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(thread_subscribers.c.thread_id)
		).
		where(sqlalchemy.text("thread_subscribers.thread_id = threads.id")).
		scalar_subquery()
	)
	r"""The amount of :class:`.User`\ s who have subscribed to a thread.

	.. seealso::
		:data:`.thread_subscribers`
	"""

	last_post_timestamp = sqlalchemy.orm.column_property(
		sqlalchemy.select(sqlalchemy.text("posts.creation_timestamp")).
		select_from(sqlalchemy.text("posts")).
		where(
			sqlalchemy.text("posts.thread_id = threads.id")
		).
		order_by(
			sqlalchemy.desc(sqlalchemy.text("posts.creation_timestamp"))
		).
		limit(1).
		scalar_subquery()
	)
	"""The time the latest :class:`.Post` in a thread was made. If there haven't
	been any posts so far, this will be :data:`None`.
	"""

	forum = sqlalchemy.orm.relationship(
		"Forum",
		uselist=False,
		passive_deletes="all",
		lazy=True
	)
	"""The :class:`.Forum` a thread is in."""

	votes = sqlalchemy.orm.relationship(
		ThreadVote,
		backref=sqlalchemy.orm.backref(
			"thread",
			uselist=False
		),
		order_by=sqlalchemy.desc(ThreadVote.creation_timestamp),
		passive_deletes="all",
		lazy=True
	)
	"""The votes that have been made on this thread.

	.. seealso::
		:class:`.ThreadVote`
	"""

	static_actions = {
		"create": lambda user: (
			Post.get_static_permission(user, "view") and
			user.parsed_permissions["thread_create"]
		),
		"create_post": lambda user: (
			Post.get_static_permission(user, "view") and
			user.parsed_permissions["post_view"] and
			user.parsed_permissions["post_create"]
		),
		"delete": lambda user: (
			Post.get_static_permission(user, "view") and (
				user.parsed_permissions["thread_delete_own"] or
				user.parsed_permissions["thread_delete_any"]
			)
		),
		"edit": lambda user: (
			Post.get_static_permission(user, "view") and (
				user.parsed_permissions["thread_edit_own"] or
				user.parsed_permissions["thread_edit_any"]
			)
		),
		"edit_lock": lambda user: (
			Post.get_static_permission(user, "view") and (
				user.parsed_permissions["thread_edit_lock_own"] or
				user.parsed_permissions["thread_edit_lock_any"]
			)
		),
		"edit_pin": lambda user: (
			Post.get_static_permission(user, "view") and
			user.parsed_permissions["thread_edit_pin"]
		),
		"edit_subscription": lambda user: (
			Post.get_static_permission(user, "view")
		),
		"edit_vote": lambda user: (
			Post.get_static_permission(user, "view") and
			user.parsed_permissions["thread_edit_vote"]
		),
		"merge": lambda user: (
			Post.get_static_permission(user, "view") and (
				user.parsed_permissions["thread_merge_own"] or
				user.parsed_permissions["thread_merge_any"]
			)
		),
		"move": lambda user: (
			Post.get_static_permission(user, "view") and (
				user.parsed_permissions["thread_move_own"] or
				user.parsed_permissions["thread_move_any"]
			)
		),
		"view": lambda user: user.parsed_permissions["thread_view"],
		"view_vote": lambda user: Post.get_static_permission(user, "view")
	}
	r"""Actions :class:`User`\ s are allowed to perform on all threads, without
	any indication of which thread it is.

	``create``:
		Whether or not a user can create threads. This depends on the
		user being allowed to view them, as well as the ``thread_create``
		value in the user's :attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_post``:
		Whether or not a user can create posts within threads. This depends on
		the ``post_view`` and ``post_create`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as the
		user being allowed to view threads.

	``delete``:
		Whether or not a user can delete threads. This depends on the user being
		allowed to view them, as well as either the ``thread_delete_own`` or
		``thread_delete_any`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit``:
		Whether or not a user can edit threads. This depends on the user being
		allowed to view them, as well as either the ``thread_edit_own`` or
		``thread_delete_any`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_lock``:
		Whether or not a user can lock / unlock threads. This depends on the user
		being allowed to view them, as well as either the
		``thread_edit_lock_own`` or ``thread_edit_lock_any`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_pin``:
		Whether or not a user can pin / unpin threads. This depends on the user
		being allowed to view them, as well as the ``thread_edit_pin`` value
		in the user's :attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_subscription``:
		Whether or not a user can subscribe to / unsubscribe from threads. Always
		:data:`True` by default, as long as the user has permission to view them.

	``edit_vote``:
		Whether or not a user can vote on threads. This depends on the user being
		allowed to view them, as well as the ``thread_edit_vote`` value in their
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``merge``:
		Whether or not a user can merge threads with other threads. This depends
		on the user being allowed to view them, as well as either the
		``thread_merge_own`` or ``thread_merge_any`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``move``:
		Whether or not a user can move threads to other forums. This depends
		on the user being allowed to view them, as well as either the
		``thread_move_own`` or ``thread_move_any`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view``:
		Whether or not a user can view threads. This depends on the
		``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view_vote``:
		Whether or not a user can view their votes for threads. As long as they
		have permission to view them, this will always be :data:`True` by default.

	.. seealso::
		:attr:`.Thread.instance_actions`

		:attr:`.Thread.action_queries`
	"""

	instance_actions = {
		"create_post": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user).post_view and
			self.forum.get_parsed_permissions(user).post_create
		),
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).thread_delete_own
				) or
				self.forum.get_parsed_permissions(user).thread_delete_any
			)
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).thread_edit_own
				) or
				self.forum.get_parsed_permissions(user).thread_edit_any
			)
		),
		"edit_lock": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).thread_edit_lock_own
				) or
				self.forum.get_parsed_permissions(user).thread_edit_lock_any
			)
		),
		"edit_pin": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user).thread_edit_pin
		),
		"edit_subscription": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"edit_vote": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user).thread_edit_vote
		),
		"merge": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).thread_merge_own
				) or
				self.forum.get_parsed_permissions(user).thread_merge_any
			) and (
				not hasattr(self, "future_thread") or
				self.future_thread.get_instance_permission(user, "merge")
			)
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user).thread_move_own
				) or
				self.forum.get_parsed_permissions(user).thread_move_any
			) and (
				not hasattr(self, "future_forum") or
				(
					self.future_forum.get_instance_permission(user, "view") and
					(
						(
							self.future_forum.user_id == user.id and
							self.future_forum.get_parsed_permissions(user).thread_move_own
						) or
						self.future_forum.get_parsed_permissions(user).thread_move_any
					)
				)
			)
		),
		"view": lambda self, user: (
			self.forum.get_parsed_permissions(user).thread_view
		),
		"view_vote": lambda self, user: self.get_instance_permission(user, "view")
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given thread. Unlike
	:attr:`static_actions <.Thread.static_actions>`, this can vary by each thread.

	``create_post``:
		Whether or not a user can create posts this thread. This depends on the
		``post_view`` and ``post_create`` values in the forum's permissions.

	``delete``:
		Whether or not a user can delete this thread. This depends on the user
		being allowed to view it, as well as them either owning this thread and
		the ``thread_delete_own`` value in the forum's permissions, or them not
		owning it and the ``thread_delete_any`` value.

	``edit``:
		Whether or not a user can edit this thread. This depends on the user
		being allowed to view it, as well as them either owning this thread and
		the ``thread_edit_own`` value in the forum's permissions, or them not
		owning it and the ``thread_edit_any`` value.

	``edit_lock``:
		Whether or not a user can lock / unlock this thread. This depends on the
		user being allowed to view it, as well as them either owning this thread
		and the ``thread_edit_lock_own`` value in the forum's permissions, or
		them not owning it and the ``thread_edit_lock_any`` value.

	``edit_pin``:
		Whether or not a user can pin / unpin this thread. This depends on the
		``thread_edit_pin`` value in the forum's permissions, as well as the user
		being allowed to view it.

	``edit_subscription``:
		Whether or not a user can subscribe to / unsubscribe from this thread.
		Always :data:`True` by default, as long as the user has permission to
		view it.

	``edit_vote``:
		Whether or not a user can vote on this thread. This depends on the user
		being allowed to view it, as well as the ``thread_edit_vote`` value in
		the forum's permissions.

	``merge``:
		Whether or not a user can merge this thread with other threads. This
		depends on the user being allowed to view it, as well as them either
		owning this thread and the ``thread_merge_own`` value in the forum's
		permissions, or them not owning it and the ``thread_merge_any`` value. If
		the ``future_thread`` attribute has been set, the same conditions must
		also apply to it.

	``move``:
		Whether or not a user can move this thread to another :class:`.Forum`.
		This depends on the user being allowed to view it, as well as them either
		owning this thread and the ``thread_move_own`` value in the forum's
		permissions, or them not owning it and the ``thread_move_any`` value. If
		the ``future_forum`` attribute has been set, the same conditions must
		also apply to it, and the user must have permission to view it.

	``view``:
		Whether or not a user is allowed to view this thread. This depends on the
		``thread_view`` value in the forum's permissions.

	``view_vote``:
		Whether or not a user is allowed to view their votes on this thread. As
		long as they have permission to view the thread itself, this will always
		be :data:`True` by default.

	.. seealso::
		:class:`.ForumParsedPermissions`

		:meth:`.Forum.reparse_permissions`

		:attr:`.Thread.static_actions`

		:attr:`.Thread.action_queries`
	"""

	@staticmethod
	def _action_query_create_post(user) -> bool:
		r"""Generates a SQLAlchemy query representing whether or not ``user`` is
		allowed to create :class:`.Post`\ s in threads.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		from .post import Post

		return sqlalchemy.and_(
			Thread._action_query_view(user),
			Post.action_queries["view"](user),
			Post.action_queries["create"](user)
		)

	@staticmethod
	def _action_query_delete(user) -> bool:
		"""Generates a SQLAlchemy query representing whether or not ``user`` is
		allowed to delete threads.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		return sqlalchemy.and_(
			Thread.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					Thread.user_id == user.id,
					ForumParsedPermissions.thread_delete_own.is_(True)
				),
				ForumParsedPermissions.thread_delete_any.is_(True)
			)
		)

	@staticmethod
	def _action_query_edit(user) -> bool:
		"""Generates a SQLAlchemy query representing whether or not ``user`` is
		allowed to delete threads.

		:param user: The user, a :class:`.User`.

		:returns: The query.
		"""

		return sqlalchemy.and_(
			Thread.action_queries["view"](user),
			sqlalchemy.or_(
				sqlalchemy.and_(
					Thread.user_id == user.id,
					ForumParsedPermissions.thread_edit_own.is_(True)
				),
				ForumParsedPermissions.thread_edit_any.is_(True)
			)
		)

	# TODO: py 3.10
	action_queries = {
		"create_post": _action_query_create_post,
		"delete": _action_query_delete,
		"edit": _action_query_edit,
	}
	"""Actions and their required permissions translated to be evaluable within
	SQL queries. Unless arbitrary additional attributes come into play, these
	permissions will generally be the same as
	:attr:`instance_actions <.Thread.instance_actions>`.

	.. seealso::
		:attr:`.Thread.instance_actions`
		:attr:`.Thread.static_actions`
	"""

	NOTIFICATION_TYPES = (
		enums.NotificationTypes.NEW_THREAD_FROM_FOLLOWEE,
		enums.NotificationTypes.NEW_THREAD_IN_SUBSCRIBED_FORUM
	)
	r"""The types of :class:`.Notification`\ s that can refer to threads."""

	def delete(
		self: Thread,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		r"""Deletes all :class:`.Notification`\ s associated with this thread,
		as well as the thread itself. If the ``session`` argument is :data:`None`,
		it's set to this object's session.
		"""

		from .notification import Notification
		from .post import Post

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		session.execute(
			sqlalchemy.delete(Notification).
			where(
				sqlalchemy.or_(
					sqlalchemy.and_(
						Notification.type.in_(self.NOTIFICATION_TYPES),
						Notification.identifier == self.id
					),
					sqlalchemy.and_(
						Notification.type.in_(Post.NOTIFICATION_TYPES),
						Notification.identifier.in_(
							sqlalchemy.select(Post.id).
							where(Post.thread_id == self.id)
						)
					)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self, session)

	def write(
		self: Thread,
		session: sqlalchemy.orm.Session
	) -> None:
		r"""Creates a :class:`.Notification` about this thread for:

		#. :class:`.User`\ s subscribed to the :class:`.Forum` this thread is in.
		#. The author's followers, as long as they aren't also subscribed to
		   the forum.

		Then adds this thread to the given ``session``.
		"""

		from .notification import Notification
		from .user import user_follows

		# Premature session add and flush. We have to access the ID later.
		CDWMixin.write(self, session)
		session.flush()

		subscriber_ids = self.forum.get_subscriber_ids(session)

		for subscriber_id in subscriber_ids:
			Notification.create(
				session,
				user_id=subscriber_id,
				type=enums.NotificationTypes.NEW_THREAD_IN_SUBSCRIBED_FORUM,
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
				type=enums.NotificationTypes.NEW_THREAD_FROM_FOLLOWEE,
				identifier=self.id
			)

		CDWMixin.write(self, session)

	def get_subscriber_ids(
		self: Thread,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> typing.List[uuid.UUID]:
		r"""Returns this thread's subscribers' :attr:`id <.User.id>`\ s. If the
		``session`` argument is :data:`None`, it's set to this object's session.

		.. seealso::
			:data:`.thread_subscribers`
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		return session.execute(
			sqlalchemy.select(thread_subscribers.c.user_id).
			where(thread_subscribers.c.thread_id == self.id)
		).scalars().all()
