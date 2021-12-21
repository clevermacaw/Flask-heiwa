from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from .. import enums
from . import Base
from .helpers import (
	UUID,
	CDWMixin,
	CreationTimestampMixin,
	EditInfoMixin,
	IdMixin,
	PermissionControlMixin,
	ReprMixin,
)
from .notification import Notification
from .user import user_follows

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

	content = sqlalchemy.Column(
		sqlalchemy.String(262144),
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
					self.forum.get_parsed_permissions(user.id).post_delete_own
				) or
				self.forum.get_parsed_permissions(user.id).post_delete_any
			)
		),
		"edit": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).post_edit_own
				) or
				self.forum.get_parsed_permissions(user.id).post_edit_any
			)
		),
		"edit_vote": lambda self, user: (
			self.get_instance_permission(user, "view") and
			self.forum.get_parsed_permissions(user.id).post_edit_vote
		),
		"move": lambda self, user: (
			self.get_instance_permission(user, "view") and (
				(
					self.thread.user_id == user.id and
					self.forum.get_parsed_permissions(user.id).post_move_own
				) or
				self.forum.get_parsed_permissions(user.id).post_move_any
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
			self.forum.get_parsed_permissions(user.id).post_view
		),
		"view_vote": lambda self, user: (
			self.get_instance_permission(user, "view")
		)
	}

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
