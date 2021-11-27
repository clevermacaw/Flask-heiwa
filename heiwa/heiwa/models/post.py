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
	"""Heiwa post vote model. Allows for both downvoting and upvoting."""

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

	def __repr__(self: PostVote) -> str:
		"""Creates a __repr__ of the current instance. Overrides the mixin method,
		which uses the "id" attribute this model lacks.
		"""

		return self._repr(
			post_id=self.post_id,
			user_id=self.user_id
		)


class Post(
	CDWMixin,
	PermissionControlMixin,
	ReprMixin,
	ToNotificationMixin,
	IdMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	Base
):
	"""Heiwa post model. Supports voting."""

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

	content = sqlalchemy.Column(
		sqlalchemy.String(262144),
		nullable=True
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

	class_actions = {
		"create": lambda cls, user: (
			cls.get_instance_permission(user, "view") and
			user.parsed_permissions["post_create"]
		),
		"delete": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["post_delete_own"] or
				user.parsed_permissions["post_delete_any"]
			)
		),
		"edit": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["post_edit_own"] or
				user.parsed_permissions["post_edit_any"]
			)
		),
		"edit_vote": lambda cls, user: (
			cls.get_class_permission(user, "view") and
			user.parsed_permissions["post_edit_vote"]
		),
		"move": lambda cls, user: (
			cls.get_class_permission(user, "view") and (
				user.parsed_permissions["post_move_own"] or
				user.parsed_permissions["post_move_any"]
			)
		),
		"view": lambda cls, user: user.parsed_permissions["post_view"],
		"view_vote": lambda cls, user: cls.get_class_permission(user, "view")
	}

	instance_actions = {
		"delete": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.thread.forum.get_parsed_permissions(user.id).post_delete_own
				) or
				self.thread.forum.get_parsed_permissions(user.id).post_delete_any
			)
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.thread.forum.get_parsed_permissions(user.id).post_edit_own
				) or
				self.thread.forum.get_parsed_permissions(user.id).post_edit_any
			)
		),
		"edit_vote": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.thread.forum.get_parsed_permissions(user.id).post_edit_vote
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.thread.user_id == user.id and
					self.thread.forum.get_parsed_permissions(user.id).post_move_own
				) or
				self.thread.forum.get_parsed_permissions(user.id).post_move_any
			) and (
				not hasattr(self, "future_thread") or
				(
					(
						self.future_thread.user_id == user.id and
						self.future_thread.forum.get_parsed_permissions(user.id).post_move_own
					) or
					self.future_thread.forum.get_parsed_permissions(user.id).post_move_any
				)
			)
		),
		"view": lambda self, user: (
			self.thread.forum.get_parsed_permissions(user.id).post_view
		),
		"view_vote": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}

	def delete(self: Post) -> None:
		"""Deletes all notifications associated with this post.

		Deletes this instance.
		"""

		sqlalchemy.orm.object_session(self).execute(
			sqlalchemy.delete(sqlalchemy.text("notifications")).
			select_from(sqlalchemy.text("notifications")).
			where(
				sqlalchemy.and_(
					(
						sqlalchemy.text("notifications.type")
						== enums.NotificationTypes.NEW_POST_IN_SUBSCRIBED_THREAD
					),
					sqlalchemy.text("notifications.content") == {
						"id": str(self.id)
					}  # TODO?
				)
			).
			execution_options(synchronize_session="fetch")
		)

		CDWMixin.delete(self)

	def write(
		self: Post,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Creates a notification about this post for:
			Users subscribed to the parent thread.
			The author's followers.

		Adds the current instance to the `session`.
		"""

		# TODO
		#for subscriber in self.thread.subscribers:
			#Notification.create(
				#session,
				#user=subscriber,
				#type_=enums.NotificationTypes.NEW_POST_IN_SUBSCRIBED_THREAD,
				#content=self.to_notification()
			#)

		#for follower in self.user.followers:
			#Notification.create(
				#session,
				#user=follower,
				#type_=enums.NotificationTypes.NEW_POST_FROM_FOLLOWED_USER,
				#content=self.to_notification()
			#)

		CDWMixin.write(self, session)
