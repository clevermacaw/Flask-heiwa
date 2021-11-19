import enum

__all__ = ["NotificationTypes"]


class NotificationTypes(enum.Enum):
	NEW_POST_FROM_FOLLOWED_USER = "NewPostFromFollowedUser"
	NEW_POST_IN_SUBSCRIBED_THREAD = "NewPostInSubscribedThread"
	NEW_THREAD_FROM_FOLLOWED_USER = "NewThreadFromFollowedUser"
	NEW_THREAD_IN_SUBSCRIBED_FORUM = "NewThreadInSubscribedForum"
