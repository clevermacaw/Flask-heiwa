"""Enums. Currently only contains Notification types."""

__all__ = ["NotificationTypes"]
__version__ = "1.3.0"


class NotificationTypes(enum.Enum):
	"""Enums for different types of notifications."""

	NEW_POST_FROM_FOLLOWEE = "NewPostFromFollowee"
	NEW_POST_IN_SUBSCRIBED_THREAD = "NewPostInSubscribedThread"
	NEW_THREAD_FROM_FOLLOWEE = "NewThreadFromFollowee"
	NEW_THREAD_IN_SUBSCRIBED_FORUM = "NewThreadInSubscribedForum"
