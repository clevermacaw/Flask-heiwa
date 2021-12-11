import enum

__all__ = ["NotificationTypes"]


class NotificationTypes(enum.Enum):
	"""Enums for different types of notifications."""

	NEW_POST_FROM_FOLLOWEE = "NewPostFromFollowee"
	NEW_POST_IN_SUBSCRIBED_THREAD = "NewPostInSubscribedThread"
	NEW_THREAD_FROM_FOLLOWEE = "NewThreadFromFollowee"
	NEW_THREAD_IN_SUBSCRIBED_FORUM = "NewThreadInSubscribedForum"
	FORUM_CHANGED_OWNERSHIP = "ForumChangedOwnership"
