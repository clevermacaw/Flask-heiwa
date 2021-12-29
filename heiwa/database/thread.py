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
from .notification import Notification
from .post import Post
from .user import user_follows

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
		sqlalchemy.String(262144),
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
	"""The final value of a thread's votes. Upvotes will add 1, downvotes will
	subtract 1. If there are no votes at all, this will be 0. Negative numbers
	are allowed.

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

	class_actions = {
		"create": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["thread_create"]
		),
		"create_post": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["post_view"] and
			user.parsed_permissions["post_create"]
		),
		"delete": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["thread_delete_own"] or
				user.parsed_permissions["thread_delete_any"]
			)
		),
		"edit": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["thread_edit_own"] or
				user.parsed_permissions["thread_edit_any"]
			)
		),
		"edit_lock": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["thread_edit_lock_own"] or
				user.parsed_permissions["thread_edit_lock_any"]
			)
		),
		"edit_pin": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["thread_edit_pin"]
		),
		"edit_subscription": lambda cls, user: (
			cls.get_class_permission(user, "view")
		),
		"edit_vote": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["thread_edit_vote"]
		),
		"merge": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["thread_merge_own"] or
				user.parsed_permissions["thread_merge_any"]
			)
		),
		"move": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["thread_move_own"] or
				user.parsed_permissions["thread_move_any"]
			)
		),
		"view": lambda cls, user: user.parsed_permissions["thread_view"],
		"view_vote": lambda cls, user: cls.get_class_permission(user, "view")
	}
	r"""Actions :class:`User`\ s are allowed to perform on all threads, without
	any indication of which thread it is.

	``create``:
		Whether or not a user can create threads. This depends on the
		``thread_create`` and ``thread_view`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``create_post``:
		Whether or not a user can create posts within threads. This depends on
		the ``post_create`` and ``post_view`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``delete``:
		Whether or not a user can delete threads. This depends on the
		``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as
		either ``thread_delete_own``, or ``thread_delete_any``.

	``edit``:
		Whether or not a user can edit threads. This depends on the
		``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as
		either ``thread_edit_own``, or ``thread_edit_any``.

	``edit_lock``:
		Whether or not a user can lock / unlock threads. This depends on the
		``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as
		either ``thread_edit_lock_own``, or ``thread_edit_lock_any``.

	``edit_pin``:
		Whether or not a user can pin / unpin threads. This depends on the
		``thread_view`` and ``thread_edit_pin`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``edit_subscription``:
		Whether or not a user can subscribe to / unsubscribe from threads. Always
		:data:`True` by default, as long as the user has permission to view them.

	``edit_vote``:
		Whether or not a user can pin / unpin threads. This depends on the
		``thread_view`` and ``thread_edit_vote`` values in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``merge``:
		Whether or not a user can merge threads with other threads. This depends
		on the ``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as
		either ``thread_merge_own``, or ``thread_merge_any``.

	``move``:
		Whether or not a user can move threads to other forums. This depends
		on the ``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`, as well as
		either ``thread_move_own``, or ``thread_move_any``.

	``view``:
		Whether or not a user can view this thread. This depends on the
		``thread_view`` value in the user's
		:attr:`parsed_permissions <.User.parsed_permissions>`.

	``view_vote``:
		Whether or not a user can view their votes for threads. As long as they
		have permission to view threads, this will always be :data:`True` by
		default.
	"""

	instance_actions = {
		"create_post": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user.id).post_view and
			self.forum.get_parsed_permissions(user.id).post_create
		),
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).thread_delete_own
				) or
				self.forum.get_parsed_permissions(user.id).thread_delete_any
			)
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).thread_edit_own
				) or
				self.forum.get_parsed_permissions(user.id).thread_edit_any
			)
		),
		"edit_lock": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).thread_edit_lock_own
				) or
				self.forum.get_parsed_permissions(user.id).thread_edit_lock_any
			)
		),
		"edit_pin": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user.id).thread_edit_pin
		),
		"edit_subscription": lambda self, user: (
			self.get_instance_permission(user, "view")
		),
		"edit_vote": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user.id).thread_edit_vote
		),
		"merge": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).thread_merge_own
				) or
				self.forum.get_parsed_permissions(user.id).thread_merge_any
			) and (
				not hasattr(self, "future_thread") or
				(
					(
						self.future_thread.user_id == user.id and
						self.future_thread.forum.get_parsed_permissions(user.id).thread_merge_own
					) or
					self.future_thread.forum.get_parsed_permissions(user.id).thread_merge_any
				)
			)
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).thread_move_own
				) or
				self.forum.get_parsed_permissions(user.id).thread_move_any
			) and (
				not hasattr(self, "future_forum") or
				(
					(
						self.future_forum.user_id == user.id and
						self.future_forum.get_parsed_permissions(user.id).thread_move_own
					) or
					self.future_forum.get_parsed_permissions(user.id).thread_move_any
				)
			)
		),
		"view": lambda self, user: (
			self.forum.get_parsed_permissions(user.id).thread_view
		),
		"view_vote": lambda self, user: self.get_instance_permission(user, "view")
	}
	r"""Actions :class:`User`\ s are allowed to perform on a given thread. Unlike
	:attr:`class_actions <.Thread.class_actions>`, this can vary by each thread.

	``create_post``:
		Whether or not a user can create posts in this thread. This depends on the
		``thread_view``, ``post_view`` and ``post_create`` values in the thread's
		forum's parsed permissions.

	``delete``:
		Whether or not a user can delete this thread. This depends on the
		``thread_view`` value in the thread's forum's parsed permissions, as well
		as either ``thread_delete_own`` when the thread belongs to the user, or
		``thread_delete_any`` when it does not.

	``edit``:
		Whether or not a user can edit this thread. This depends on the
		``thread_view`` value in the thread's forum's parsed permissions, as well
		as either ``thread_edit_own`` when the thread belongs to the user, or
		``thread_edit_any`` when it does not.

	``edit_lock``:
		Whether or not a user can lock / unlock this thread. This depends on the
		``thread_view`` value in the thread's forum's parsed permissions, as well
		as either ``thread_edit_lock_own`` when the thread belongs to the user,
		or ``thread_edit_lock_any`` when it does not.

	``edit_pin``:
		Whether or not a user can pin / unpin this thread. This depends on the
		``thread_view`` and ``thread_edit_pin`` values in the thread's forum's
		parsed permissions.

	``edit_subscription``:
		Whether or not a user can subscribe to / unsubscribe from this thread.
		As long as they have permission to view it, this will always be
		:data:`True` by default.

	``edit_vote``:
		Whether or not a user can vote on this thread. This depends on the
		``thread_view`` and ``thread_edit_vote`` values in the thread's forum's
		parsed permissions.

	``merge``:
		Whether or not a user can merge this thread with another thread. This
		depends on the ``thread_view`` value in the thread's forum's parsed
		permissions, as well as either ``thread_merge_own`` when the thread
		belongs to the user, or ``thread_merge_any`` when it does not. If the
		``future_thread`` atrribute has been assigned to this thread, the same
		conditions must also apply to the thread contained within it.

	``move``:
		Whether or not a user can move this thread to a different forum. This
		depends on the ``thread_view`` value in the thread's forum's parsed
		permissions, as well as either ``thread_move_own`` when the thread
		belongs to the user, or ``thread_move_any`` when it does not. If the
		``future_forum`` atrribute has been assigned to this thread, the same
		conditions must also apply to the forum contained within it.

	``view``:
		Whether or not a user can view this thread. This depends on the
		``thread_view`` value in the thread's forum's parsed permissions.

	``view_vote``:
		Whether or not a user can view their vote on this thread. As long as they
		have permission to view the thread, this will always be :data:`True` by
		default.

	.. seealso::
		:class:`.ForumParsedPermissions`

		:meth:`.Forum.reparse_permissions`
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
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		return session.execute(
			sqlalchemy.select(thread_subscribers.c.user_id).
			where(thread_subscribers.c.thread_id == self.id)
		).scalars().all()
