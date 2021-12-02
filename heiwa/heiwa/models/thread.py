from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .forum import forum_subscribers
from .helpers import (
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
	UUID
)
from .notification import Notification
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
	"""A `Thread` helper model for storing votes. Contains:
		- A `creation_timestamp` column from the `CreationTimestampMixin`.
		- `edit_timestamp` and `edit_count` columns from the `EditInfoMixin`.
		- A `thread_id` column, associating the instance with a `Thread`.
		- A `user_id` column, associating the instance with a `User`.
		- An `upvote` column, signifying whether this is a downvote or an upvote.
	"""

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

	def __repr__(self: ThreadVote) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin method,
		which uses the `id` attribute this model lacks.
		"""

		return self._repr(
			thread_id=self.thread_id,
			user_id=self.user_id
		)


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
	"""Thread model. Contains:
		- An `id` column from the `IdMixin`.
		- A `creation_timestamp` column from the `CreationTimestampMixin`.
		- `edit_timestamp` and `edit_count` columns from the `EditInfoMixin`.
		- A `forum_id` foreign key column, associating this thread with a `Forum`.
		- A `user_id` foreign key column, associating this thread with its author,
		a `User`.
		- An `is_locked` column, signifying whether or not this thread is locked.
		- An `is_pinned` column, signifying whether or not this thread is pinned.
		On frontend applications, this should make pinned threads float to the top
		of their respective lists.
		- A `tags` column, signifying this thread's tags
		(e.g. `'Support'`, `'Important'`).
		- `name` and `content` columns.
		- A dynamic `vote_value` column, corresponding to the total count of this
		thread's upvotes, with the downvotes' count subtracted.
		- A dynamic `post_count` column, corresponding to how many posts exist
		with this thread's `id` defined as their `thread_id`.
		- A dynamic `subscriber_count` column, corresponding to how many users
		have subscribed to this thread.
		- A dynamic `last_post_timestamp` column, corresponding to the latest
		post in this thread's `creation_timestamp`.
	"""

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

	is_locked = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)
	is_pinned = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=False
	)

	tags = sqlalchemy.Column(
		sqlalchemy.ARRAY(sqlalchemy.String(128)),
		nullable=False
	)
	name = sqlalchemy.Column(
		sqlalchemy.String(128),
		nullable=False
	)
	content = sqlalchemy.Column(
		sqlalchemy.String(262144),
		nullable=False
	)

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

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(thread_subscribers.c.thread_id)
		).
		where(thread_subscribers.c.thread_id == sqlalchemy.text("threads.id")).
		scalar_subquery()
	)

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
				not hasattr(self, "future_thread") or
				(
					(
						self.future_thread.user_id == user.id and
						self.future_thread.forum.get_parsed_permissions(user.id).thread_move_own
					) or
					self.future_thread.forum.get_parsed_permissions(user.id).thread_move_any
				)
			)
		),
		"view": lambda self, user: (
			self.forum.get_parsed_permissions(user.id).thread_view
		),
		"view_vote": lambda self, user: self.get_instance_permission(user, "view")
	}

	def delete(
		self: Thread,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Deletes all notifications associated with this thread, as well as the
		thread itself. If the `session` argument is `None`, it's set to this
		object's session.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		session.execute(
			sqlalchemy.delete(Notification).
			where(
				sqlalchemy.and_(
					(
						Notification.type
						== enums.NotificationTypes.NEW_THREAD_IN_SUBSCRIBED_FORUM
					),
					Notification.identifier == self.id
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self, session)

	def write(
		self: Thread,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Creates a notification about this thread for:
			Users subscribed to the parent forum.
			The author's followers. (Who aren't subscribed to the forum)

		Adds the current instance to the `session`.
		"""

		subscriber_ids = session.execute(
			sqlalchemy.select(forum_subscribers.c.user_id).
			where(forum_subscribers.c.forum_id == self.forum_id)
		).scalars().all()

		# Premature session add and flush. We have to access the ID later.
		CDWMixin.write(self, session)
		session.flush()

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
