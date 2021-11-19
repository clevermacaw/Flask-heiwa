from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .helpers import (
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
	ToNotificationMixin,
	UUID
)
from .notification import Notification
from .post import Post

__all__ = [
	"Thread",
	"ThreadVote",
	"thread_subscribers",
	"thread_viewers"
]


class ThreadVote(
	CDWMixin,
	ReprMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Heiwa thread vote model. Allows for both downvoting and upvoting."""

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

	user = sqlalchemy.orm.relationship(
		"User",
		uselist=False,
		lazy=True
	)

	def __repr__(self: ThreadVote) -> str:
		"""Creates a `__repr__` of the current instance. Overrides the mixin 
method,
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


thread_viewers = sqlalchemy.Table(
	"thread_viewers",
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
	ToNotificationMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Heiwa thread model. Supports voting, subscribing and storing views."""

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
			sqlalchemy.func.count(
				ThreadVote.upvote
			)
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
			sqlalchemy.func.count(Post.id)
		).
		where(Post.thread_id == sqlalchemy.text("threads.id")).
		scalar_subquery()
	)

	subscriber_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(
				thread_subscribers.c.thread_id
			)
		).
		where(thread_subscribers.c.thread_id == sqlalchemy.text("threads.id")).
		scalar_subquery()
	)

	viewer_count = sqlalchemy.orm.column_property(
		sqlalchemy.select(
			sqlalchemy.func.count(
				thread_viewers.c.thread_id
			)
		).
		where(thread_viewers.c.thread_id == sqlalchemy.text("threads.id")).
		scalar_subquery()
	)

	last_post_timestamp = sqlalchemy.orm.column_property(
		sqlalchemy.select(Post.creation_timestamp).
		where(Post.thread_id == sqlalchemy.text("threads.id")).
		order_by(
			sqlalchemy.desc(Post.creation_timestamp)
		).
		limit(1).
		scalar_subquery()
	)

	posts = sqlalchemy.orm.relationship(
		"Post",
		order_by="desc(Post.creation_timestamp)",
		backref=sqlalchemy.orm.backref(
			"thread",
			uselist=False
		),
		passive_deletes="all",
		lazy=True
	)
	subscribers = sqlalchemy.orm.relationship(
		"User",
		secondary=thread_subscribers,
		order_by="desc(User.creation_timestamp)",
		lazy=True
	)
	viewers = sqlalchemy.orm.relationship(
		"User",
		secondary=thread_viewers,
		order_by="desc(User.creation_timestamp)",
		lazy=True
	)

	votes = sqlalchemy.orm.relationship(
		ThreadVote,
		order_by=sqlalchemy.desc(ThreadVote.creation_timestamp),
		backref=sqlalchemy.orm.backref(
			"thread",
			uselist=False
		),
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
			Post.get_class_permission(user, "view") and
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
			Post.get_class_permission(user, "view") and
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

	def delete(self: Thread) -> None:
		"""Creates an instance with the provided arguments and adds it to the session.
		Deletes all notifications associated with this thread.

		Deletes this instance.
		"""

		sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.delete(Notification).
			where(
				sqlalchemy.and_(
					(
						Notification.type_
						== enums.NotificationTypes.NEW_THREAD_IN_SUBSCRIBED_FORUM
					),
					Notification.content["id"].as_string() == str(self.id)
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self)

	def write(
		self: Thread,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Creates a notification about this thread for:
			Users subscribed to the parent forum.
			The author's followers.

		Adds the current instance to the `session`.
		"""

		for subscriber in self.forum.subscribers:
			Notification.create(
				session,
				user=subscriber,
				type_=enums.NotificationTypes.NEW_THREAD_IN_SUBSCRIBED_FORUM,
				content=self.to_notification()
			)

		for follower in self.user.followers:
			Notification.create(
				session,
				user=follower,
				type_=enums.NotificationTypes.NEW_THREAD_FROM_FOLLOWED_USER,
				content=self.to_notification()
			)

		CDWMixin.write(
			self,
			session
		)
