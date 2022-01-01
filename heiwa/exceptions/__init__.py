"""API Exceptions."""

from __future__ import annotations

import typing

from .. import statuses

__all__ = [
	"APIException",
	"APIAuthorizationHeaderInvalid",
	"APIAuthorizationHeaderMissing",
	"APICategoryNotFound",
	"APIForumCategoryOutsideParent",
	"APIForumChildLevelLimitReached",
	"APIForumNotFound",
	"APIForumParentIsChild",
	"APIForumPermissionsGroupNotFound",
	"APIForumPermissionsGroupUnchanged",
	"APIForumPermissionsUserNotFound",
	"APIForumPermissionsUserUnchanged",
	"APIForumSubscriptionAlreadyExists",
	"APIForumSubscriptionNotFound",
	"APIForumUnchanged",
	"APIGroupCannotDeleteLastDefault",
	"APIGroupCannotDeletePermissionsForLastDefault",
	"APIGroupCannotLeavePermissionNullForLastDefault",
	"APIGroupNotFound",
	"APIGroupPermissionsNotFound",
	"APIGroupPermissionsUnchanged",
	"APIGroupUnchanged",
	"APIGuestSessionLimitReached",
	"APIJSONInvalid",
	"APIJSONMissing",
	"APIJWTInvalid",
	"APIJWTInvalidClaims",
	"APIJWTUserNotFound",
	"APIMessageCannotChangeIsReadOfSent",
	"APIMessageCannotSendToSelf",
	"APIMessageNotFound",
	"APIMessageReceiverBlockedSender",
	"APIMessageUnchanged",
	"APINoPermission",
	"APINotificationNotFound",
	"APIOpenIDAuthenticationFailed",
	"APIOpenIDNonceInvalid",
	"APIOpenIDServiceNotFound",
	"APIOpenIDStateInvalid",
	"APIPostNotFound",
	"APIPostUnchanged",
	"APIPostVoteNotFound",
	"APIPostVoteUnchanged",
	"APIRateLimitExceeded",
	"APIThreadLocked",
	"APIThreadNotFound",
	"APIThreadSubscriptionAlreadyExists",
	"APIThreadSubscriptionNotFound",
	"APIThreadUnchanged",
	"APIThreadVoteNotFound",
	"APIThreadVoteUnchanged",
	"APIUserAvatarInvalid",
	"APIUserAvatarNotAllowedType",
	"APIUserAvatarTooLarge",
	"APIUserBanAlreadyExpired",
	"APIUserBanNotFound",
	"APIUserBanUnchanged",
	"APIUserBanned",
	"APIUserBlockAlreadyExists",
	"APIUserBlockNotFound",
	"APIUserCannotRemoveLastDefaultGroup",
	"APIUserFollowAlreadyExists",
	"APIUserGroupAlreadyAdded",
	"APIUserGroupNotAdded",
	"APIUserNotFound",
	"APIUserPermissionsUnchanged",
	"APIUserUnchanged"
]
__version__ = "1.32.1"


class APIException(Exception):
	"""The base class for all API exceptions. Default values:

	* (HTTP) :attr:`code <.APIException.code>`:
	  :attr:`INTERNAL_SERVER_ERROR <heiwa.statuses.INTERNAL_SERVER_ERROR>`
	* :attr:`details <.APIException.details>`: :data:`None`
	"""

	code = statuses.INTERNAL_SERVER_ERROR
	details = None

	def __init__(
		self: APIException,
		details: typing.Union[
			None,
			str,
			int,
			typing.Dict[
				str,
				typing.Union[
					typing.Dict,
					typing.Any
				]
			],
		] = details,
		*args,
		**kwargs
	) -> None:
		"""Sets the :attr:`details <.APIException.details>` class variable to the
		given value. If this method isn't used, it remains :data:`None`.
		"""

		self.details = details

		Exception.__init__(self, *args, **kwargs)


class APIAuthorizationHeaderInvalid(APIException):
	"""Exception class for when the ``Authorization`` header is required and
	present, but not valid. (e.g. Basic instead of Bearer, when only Bearer
	is supported)
	"""

	code = statuses.BAD_REQUEST


class APIAuthorizationHeaderMissing(APIException):
	"""Exception class for when the ``Authorization`` header is required, but
	not present.
	"""

	code = statuses.BAD_REQUEST


class APICategoryNotFound(APIException):
	"""Exception class for when a requested
	:class:`Category <heiwa.database.Category>` does not exist.
	"""

	code = statuses.NOT_FOUND


class APIForumCategoryOutsideParent(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to assign a :class:`Category <heiwa.database.Category>` to a
	:class:`Forum <heiwa.database.Forum>`, while also assigning a parent forum
	whose :attr:`id <heiwa.database.Forum.id>` does not match the category's
	:attr:`forum_id <heiwa.database.Category.forum_id>`.
	"""

	code = statuses.FORBIDDEN


class APIForumChildLevelLimitReached(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to create a :class:`Forum <heiwa.database.Forum>` whose
	:attr:`child_level <heiwa.database.Forum.child_level>` is higher than the
	config's ``FORUM_MAX_CHILD_LEVEL`` key.
	"""

	code = statuses.FORBIDDEN


class APIForumNotFound(APIException):
	"""Exception class for when a requested :class:`Forum <heiwa.database.Forum>`
	(e.g. ``/forums/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIForumParentIsChild(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	assign a parent :class:`Forum <heiwa.database.Forum>`, but its ID is the same
	as the child forum's.
	"""

	code = statuses.FORBIDDEN


class APIForumPermissionsGroupNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to delete a :class:`Group <heiwa.database.Group>`'s permissions for a certain
	:class:`Forum <heiwa.database.Forum>`, but there are none.

	.. seealso::
		:class:`ForumPermissionsGroup <heiwa.database.ForumPermissionsGroup>`
	"""

	code = statuses.NOT_FOUND


class APIForumPermissionsGroupUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to edit a :class:`Group <heiwa.database.Group>`'s permissions for a certain
	:class:`Forum <heiwa.database.Forum>`, but there are none.

	.. seealso::
		:class:`ForumPermissionsGroup <heiwa.database.ForumPermissionsGroup>`
	"""

	code = statuses.FORBIDDEN


class APIForumPermissionsUserNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to delete another user's permissions for a certain
	:class:`Forum <heiwa.database.Forum>`, but there are none.

	.. seealso::
		:class:`ForumPermissionsUser <heiwa.database.ForumPermissionsUser>`
	"""

	code = statuses.NOT_FOUND


class APIForumPermissionsUserUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts
	to edit another user's permissions for a certain
	:class:`Forum <heiwa.database.Forum>`, but all values are the exact same as
	the existing ones.

	.. seealso::
		:class:`ForumPermissionsUser <heiwa.database.ForumPermissionsUser>`
	"""

	code = statuses.FORBIDDEN


class APIForumSubscriptionAlreadyExists(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	subscribe to a :class:`Forum <heiwa.database.Forum>`, but has already done so
	before.

	.. seealso::
		:data:`forum_subscribers <heiwa.database.forum_subscribers>`
	"""

	code = statuses.FORBIDDEN


class APIForumSubscriptionNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	unsubscribe from a :class:`Forum <heiwa.database.Forum>`, but there is no
	subscription in the first place.

	.. seealso::
		:data:`forum_subscribers <heiwa.database.forum_subscribers>`
	"""

	code = statuses.NOT_FOUND


class APIForumUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit a :class:`Forum <heiwa.database.Forum>`, but all values are the exact
	same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIGroupCannotDeleteLastDefault(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete the last :class:`Group <heiwa.database.Group>` whose
	:attr:`default_for <heiwa.database.Group.default_for>` column contains ``*``.
	"""

	code = statuses.FORBIDDEN


class APIGroupCannotDeletePermissionsForLastDefault(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete permissions for the last :class:`Group <heiwa.database.Group>` whose
	:attr:`default_for <heiwa.database.Group.default_for>` column contains ``*``.

	.. seealso::
		:class:`GroupPermissions <heiwa.database.GroupPermissions>`
	"""

	code = statuses.FORBIDDEN

# TODO from here


class APIGroupCannotLeavePermissionNullForLastDefault(APIException):
	"""Exception class for when a user attempts to set a permission whose
	value is :data:`None` for the last group whose
	:attr:`default_for <heiwa.database.Group.default_for>` column is ``*``.
	"""

	code = statuses.FORBIDDEN


class APIGroupNotFound(APIException):
	"""Exception class for when a requested group (e.g. ``/groups/inexistent-id``)
	does not exist.
	"""

	code = statuses.NOT_FOUND


class APIGroupPermissionsNotFound(APIException):
	"""Exception class for when a user attempts to delete a group's permissions,
	but there are none.
	"""

	code = statuses.NOT_FOUND


class APIGroupPermissionsUnchanged(APIException):
	"""Exception class for when a user attempts to edit a group's permissions,
	but all values are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIGroupUnchanged(APIException):
	"""Exception class for when a user attempts to edit a group, but all values
	are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIGuestSessionLimitReached(APIException):
	"""Exception class for when a visitor attempts to obtain a guest token,
	but already has too many existing accounts with the same IP address
	(``external_id``) which haven't yet expired.
	"""

	code = statuses.FORBIDDEN


class APIJSONInvalid(APIException):
	"""Exception class for when the JSON data sent to the API is invalid, as per
	the predefined Cerberus schema.
	"""

	code = statuses.BAD_REQUEST


class APIJSONMissing(APIException):
	"""Exception class for when a route expects to receive JSON data,
	but there is none.
	"""

	code = statuses.BAD_REQUEST


class APIJWTInvalid(APIException):
	"""Exception class for when the provided JWT is not valid and
	cannot be decoded. (e.g. missing a character, corrupted)
	"""

	code = statuses.BAD_REQUEST


class APIJWTInvalidClaims(APIException):
	"""Exception class for when the provided JWT is valid,
	but its claims are not. (e.g. it is expired)
	"""

	code = statuses.BAD_REQUEST


class APIJWTUserNotFound(APIException):
	"""Exception class for when the provided JWT and its claims are valid,
	but its specified user has since been deleted.
	"""

	code = statuses.NOT_FOUND


class APIMessageCannotSendToSelf(APIException):
	"""Exception class for when a user attempts to send a message to
	themselves.
	"""

	code = statuses.FORBIDDEN


class APIMessageCannotChangeIsReadOfSent(APIException):
	"""Exception class for when a user attempts to mark a message as read / unread,
	but they're also its sender.
	"""

	code = statuses.FORBIDDEN


class APIMessageNotFound(APIException):
	"""Exception class for when a requested message
	(e.g. ``/messages/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIMessageReceiverBlockedSender(APIException):
	"""Exception class for when a user attempts to send a message to another user,
	but they've blocked them.
	"""

	code = statuses.FORBIDDEN


class APIMessageUnchanged(APIException):
	"""Exception class for when a user attempts to edit a message,
	but all values are the exact same as the existing ones.
	"""


class APINoPermission(APIException):
	"""Exception class for when a user attempts to perform an action they do not
	have permission to.
	"""

	code = statuses.UNAUTHORIZED


class APINotificationNotFound(APIException):
	"""Exception class for when a requested notification
	(e.g. ``/notifications/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIOpenIDAuthenticationFailed(APIException):
	"""Exception class for when there was an issue authenticating via OpenID.
	(for example, requests sent to the authentication server failing)
	"""

	code = statuses.UNAUTHORIZED


class APIOpenIDNonceInvalid(APIException):
	"""Exception class for when a user tries to authorize via OpenID and
	presents a correct state, but the retrieved nonce does not match.
	"""

	code = statuses.BAD_REQUEST


class APIOpenIDServiceNotFound(APIException):
	"""Exception class for when a requested OpenID service
	(e.g. ``/openid/login/inexistent-service``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIOpenIDStateInvalid(APIException):
	"""Exception class for when a user attempts to authorize with OpenID,
	but presents an invalid state.
	"""

	code = statuses.BAD_REQUEST


class APIPostNotFound(APIException):
	"""Exception class for when a requested post
	(e.g. ``/posts/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIPostUnchanged(APIException):
	"""Exception class for when a user attempts to edit a post,
	but all values are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIPostVoteNotFound(APIException):
	"""Exception class for when a user attempts to delete their vote on a post,
	but there is none.
	"""

	code = statuses.NOT_FOUND


class APIPostVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a post,
	but has already done so before and hasn't changed their vote.
	"""

	code = statuses.FORBIDDEN


class APIRateLimitExceeded(APIException):
	"""Exception class for when a given user has exceeded the rate limit
	for a specific endpoint.
	"""

	code = 429


class APIThreadLocked(APIException):
	"""Exception for when a user attempts to make posts in a locked thread."""

	code = statuses.FORBIDDEN


class APIThreadNotFound(APIException):
	"""Exception class for when a requested thread
	(e.g. ``/threads/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIThreadSubscriptionAlreadyExists(APIException):
	"""Exception class for when a user attempts to subscribe to a thread,
	but has already done so before.
	"""

	code = statuses.FORBIDDEN


class APIThreadSubscriptionNotFound(APIException):
	"""Exception class for when a user attempts to unsubscribe from a thread,
	but there is no subscription in the first place.
	"""

	code = statuses.NOT_FOUND


class APIThreadUnchanged(APIException):
	"""Exception class for when a user attempts to edit a thread,
	but all values are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIThreadVoteNotFound(APIException):
	"""Exception class for when a user attempts to delete their vote on a thread,
	but there is none.
	"""

	code = statuses.NOT_FOUND


class APIThreadVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a thread,
	but has already done so before and hasn't changed their vote.
	"""

	code = statuses.FORBIDDEN


class APIUserAvatarInvalid(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but the data contained within it is invalid or corrupted.
	"""

	code = statuses.BAD_REQUEST


class APIUserAvatarNotFound(APIException):
	"""Exception class for when a user attempts to delete an avatar,
	but there is none.
	"""

	code = statuses.NOT_FOUND


class APIUserAvatarNotAllowedType(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but its MIME type does not equal any of those allowed in the config.
	"""

	code = statuses.BAD_REQUEST


class APIUserAvatarTooLarge(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but its size is greater than what is allowed in the config.
	"""

	code = statuses.FORBIDDEN


class APIUserBanAlreadyExpired(APIException):
	"""Exception class for when a user attempts to ban another user,
	but the expiration timestamp is in the past.
	"""

	code = statuses.FORBIDDEN


class APIUserBanNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's ban,
	but there is none.
	"""

	code = statuses.NOT_FOUND


class APIUserBanUnchanged(APIException):
	"""Exception class for when a user attempts to ban / unban another user,
	but has already done so with the same reason & expiration timestamp.
	"""

	code = statuses.FORBIDDEN


class APIUserBanned(APIException):
	"""Exception class for when an authenticated user attempts to access the API,
	but has been banned in the past and the ban hasn't expired yet.
	"""

	code = statuses.FORBIDDEN


class APIUserBlockAlreadyExists(APIException):
	"""Exception class for when a user attempts to block another user,
	but has already done so before.
	"""

	code = statuses.FORBIDDEN


class APIUserBlockNotFound(APIException):
	"""Exception class for when a user attempts to unblock another user,
	but has never blocked them in the first place.
	"""

	code = statuses.NOT_FOUND


class APIUserCannotRemoveLastDefaultGroup(APIException):
	"""Exception class for when a user attempts to remove the last group whose
	``default_for`` column contains ``*`` from another user.
	"""

	code = statuses.FORBIDDEN


class APIUserFollowAlreadyExists(APIException):
	"""Exception class for when a user attempts to follow another user,
	but has already done so before.
	"""

	code = statuses.FORBIDDEN


class APIUserFollowNotFound(APIException):
	"""Exception class for when a user attempts to unfollow another user,
	but has never followed them in the first place.
	"""

	code = statuses.NOT_FOUND


class APIUserGroupAlreadyAdded(APIException):
	"""Exception class for when a user attempts to add a group to another user,
	but it's already been added before.
	"""

	code = statuses.FORBIDDEN


class APIUserGroupNotAdded(APIException):
	"""Exception class for when a user attempts to remove a group from another
	user, but it's been removed before or never added in the first place.
	"""

	code = statuses.FORBIDDEN


class APIUserNotFound(APIException):
	"""Exception class for when a requested user
	(e.g. ``/users/inexistent-id``) does not exist.
	"""

	code = statuses.NOT_FOUND


class APIUserPermissionsNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's
	permissions (specific to them), but there are none.
	"""

	code = statuses.NOT_FOUND


class APIUserPermissionsUnchanged(APIException):
	"""Exception class for when a user attempts to edit another user's
	permissions, but all values are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN


class APIUserUnchanged(APIException):
	"""Exception class for when a user attempts to edit another user,
	but all values are the exact same as the existing ones.
	"""

	code = statuses.FORBIDDEN
