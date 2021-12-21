"""Exceptions."""

from __future__ import annotations

import typing

from .. import helpers

__all__ = [
	"APIException",
	"APIAuthorizationHeaderInvalid",
	"APIAuthorizationHeaderMissing",
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
__version__ = "1.31.0"


class APIException(Exception):
	"""The base class for all API exceptions. Default values:

	* (HTTP) ``code``: ``500``
	* ``details``: ``None``
	"""

	code = helpers.STATUS_INTERNAL_SERVER_ERROR
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
		"""Sets the ``details`` class variable to the given value. If this method
		isn't used, it remains ``None``.
		"""

		self.details = details

		Exception.__init__(self, *args, **kwargs)


class APIAuthorizationHeaderInvalid(APIException):
	"""Exception class for when the ``'Authorization'`` header is required and
	present, but not valid. (e.g. Basic instead of Bearer, when only Bearer
	is supported)
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIAuthorizationHeaderMissing(APIException):
	"""Exception class for when the ``'Authorization'`` header is required,
	but not present.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIForumChildLevelLimitReached(APIException):
	"""Exception class for when a user attempts to create a forum whose
	child level is above the config's `` 'FORUM_MAX_CHILD_LEVEL'`` key.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumNotFound(APIException):
	"""Exception class for when a requested forum
	(e.g. ``'/forums/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIForumParentIsChild(APIException):
	"""Exception class for when a user attempts to assign a parent forum,
	but its ID is the same as the child forum's.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumPermissionsGroupNotFound(APIException):
	"""Exception class for when a user attempts to delete a group's permissions
	permissions for a certain forum, but there are none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIForumPermissionsGroupUnchanged(APIException):
	"""Exception class for when a user attempts to edit another group's
	permissions for a certain forum, but all values are the exact same as
	the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumPermissionsUserNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's
	permissions permissions for a certain forum, but there are none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIForumPermissionsUserUnchanged(APIException):
	"""Exception class for when a user attempts to edit another user's permissions
	for a certain forum, but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumSubscriptionAlreadyExists(APIException):
	"""Exception class for when a user attempts to subscribe to a forum,
	but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumSubscriptionNotFound(APIException):
	"""Exception class for when a user attempts to unsubscribe from a forum,
	but there is no subscription in the first place.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIForumUnchanged(APIException):
	"""Exception class for when a user attempts to edit a forum,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotDeleteLastDefault(APIException):
	"""Exception class for when a user attempts to delete the last group
	which is default for ``*``.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotDeletePermissionsForLastDefault(APIException):
	"""Exception class for when a user attempts to delete permissions
	for the last group whose ``default_for`` column contains ``'*'``.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotLeavePermissionNullForLastDefault(APIException):
	"""Exception class for when a user attempts to set a permission whose
	value is ``None`` for the last group whose ``default_for`` column is ``'*'``.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupNotFound(APIException):
	"""Exception class for when a requested group
	(e.g. ``'/groups/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIGroupPermissionsNotFound(APIException):
	"""Exception class for when a user attempts to delete a group's permissions,
	but there are none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIGroupPermissionsUnchanged(APIException):
	"""Exception class for when a user attempts to edit a group's permissions,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupUnchanged(APIException):
	"""Exception class for when a user attempts to edit a group,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGuestSessionLimitReached(APIException):
	"""Exception class for when a visitor attempts to obtain a guest token,
	but already has too many existing accounts with the same IP address
	(``external_id``) which haven't yet expired.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIJSONInvalid(APIException):
	"""Exception class for when the JSON data sent to the API is invalid,
	as per the predefined Cerberus schema.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJSONMissing(APIException):
	"""Exception class for when a route expects to receive JSON data,
	but there is none.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJWTInvalid(APIException):
	"""Exception class for when the provided JWT is not valid and
	cannot be decoded. (e.g. missing a character, corrupted)
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJWTInvalidClaims(APIException):
	"""Exception class for when the provided JWT is valid,
	but its claims are not. (e.g. it is expired)
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJWTUserNotFound(APIException):
	"""Exception class for when the provided JWT and its claims are valid,
	but its specified user has since been deleted.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIMessageCannotSendToSelf(APIException):
	"""Exception class for when a user attempts to send a message to
	themselves.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIMessageCannotChangeIsReadOfSent(APIException):
	"""Exception class for when a user attempts to mark a message as read / unread,
	but they're also its sender.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIMessageNotFound(APIException):
	"""Exception class for when a requested message
	(e.g. ``'/messages/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIMessageReceiverBlockedSender(APIException):
	"""Exception class for when a user attempts to send a message to another user,
	but they've blocked them.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIMessageUnchanged(APIException):
	"""Exception class for when a user attempts to edit a message,
	but all values are the exact same as the existing ones.
	"""


class APINoPermission(APIException):
	"""Exception class for when a user attempts to perform an action they do not
	have permission to.
	"""

	code = helpers.STATUS_UNAUTHORIZED


class APINotificationNotFound(APIException):
	"""Exception class for when a requested notification
	(e.g. ``'/notifications/inexistent-id``') does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIOpenIDAuthenticationFailed(APIException):
	"""Exception class for when there was an issue authenticating via OpenID.
	(for example, requests sent to the authentication server failing)
	"""

	code = helpers.STATUS_UNAUTHORIZED


class APIOpenIDNonceInvalid(APIException):
	"""Exception class for when a user tries to authorize via OpenID and
	presents a correct state, but the retrieved nonce does not match.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIOpenIDServiceNotFound(APIException):
	"""Exception class for when a requested OpenID service
	(e.g. ``'/openid/login/inexistent-service'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIOpenIDStateInvalid(APIException):
	"""Exception class for when a user attempts to authorize with OpenID,
	but presents an invalid state.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIPostNotFound(APIException):
	"""Exception class for when a requested post
	(e.g. ``'/posts/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIPostUnchanged(APIException):
	"""Exception class for when a user attempts to edit a post,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIPostVoteNotFound(APIException):
	"""Exception class for when a user attempts to delete their vote on a post,
	but there is none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIPostVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a post,
	but has already done so before and hasn't changed their vote.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIRateLimitExceeded(APIException):
	"""Exception class for when a given user has exceeded the rate limit
	for a specific endpoint.
	"""

	code = 429


class APIThreadLocked(APIException):
	"""Exception for when a user attempts to make posts in a locked thread."""

	code = helpers.STATUS_FORBIDDEN


class APIThreadNotFound(APIException):
	"""Exception class for when a requested thread
	(e.g. ``'/threads/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIThreadSubscriptionAlreadyExists(APIException):
	"""Exception class for when a user attempts to subscribe to a thread,
	but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIThreadSubscriptionNotFound(APIException):
	"""Exception class for when a user attempts to unsubscribe from a thread,
	but there is no subscription in the first place.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIThreadUnchanged(APIException):
	"""Exception class for when a user attempts to edit a thread,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIThreadVoteNotFound(APIException):
	"""Exception class for when a user attempts to delete their vote on a thread,
	but there is none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIThreadVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a thread,
	but has already done so before and hasn't changed their vote.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserAvatarInvalid(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but the data contained within it is invalid or corrupted.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIUserAvatarNotFound(APIException):
	"""Exception class for when a user attempts to delete an avatar,
	but there is none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserAvatarNotAllowedType(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but its MIME type does not equal any of those allowed in the config.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIUserAvatarTooLarge(APIException):
	"""Exception class for when a user attempts to set an avatar,
	but its size is greater than what is allowed in the config.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserBanAlreadyExpired(APIException):
	"""Exception class for when a user attempts to ban another user,
	but the expiration timestamp is in the past.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserBanNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's ban,
	but there is none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserBanUnchanged(APIException):
	"""Exception class for when a user attempts to ban / unban another user,
	but has already done so with the same reason & expiration timestamp.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserBanned(APIException):
	"""Exception class for when an authenticated user attempts to access the API,
	but has been banned in the past and the ban hasn't expired yet.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserBlockAlreadyExists(APIException):
	"""Exception class for when a user attempts to block another user,
	but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserBlockNotFound(APIException):
	"""Exception class for when a user attempts to unblock another user,
	but has never blocked them in the first place.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserCannotRemoveLastDefaultGroup(APIException):
	"""Exception class for when a user attempts to remove the last group whose
	``default_for`` column contains ``'*'`` from another user.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserFollowAlreadyExists(APIException):
	"""Exception class for when a user attempts to follow another user,
	but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserFollowNotFound(APIException):
	"""Exception class for when a user attempts to unfollow another user,
	but has never followed them in the first place.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserGroupAlreadyAdded(APIException):
	"""Exception class for when a user attempts to add a group to another user,
	but it's already been added before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserGroupNotAdded(APIException):
	"""Exception class for when a user attempts to remove a group from another
	user, but it's been removed before or never added in the first place.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserNotFound(APIException):
	"""Exception class for when a requested user
	(e.g. ``'/users/inexistent-id'``) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserPermissionsNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's
	permissions (specific to them), but there are none.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIUserPermissionsUnchanged(APIException):
	"""Exception class for when a user attempts to edit another user's
	permissions, but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserUnchanged(APIException):
	"""Exception class for when a user attempts to edit another user,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN
