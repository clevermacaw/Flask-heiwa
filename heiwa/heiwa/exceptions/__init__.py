"""Exceptions for the Heiwa API."""

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
	"APIForumSubscriptionUnchanged",
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
	"APIMessageNotFound",
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
	"APIThreadLocked",
	"APIThreadNotFound",
	"APIThreadSubscriptionUnchanged",
	"APIThreadUnchanged",
	"APIThreadVoteNotFound",
	"APIThreadVoteUnchanged",
	"APIUserAvatarInvalid",
	"APIUserAvatarNotAllowedType",
	"APIUserAvatarTooLarge",
	"APIUserBanAlreadyExpired",
	"APIUserBanUnchanged",
	"APIUserBanned",
	"APIUserBlockUnchanged",
	"APIUserCannotRemoveLastDefaultGroup",
	"APIUserFollowUnchanged",
	"APIUserNotFound",
	"APIUserPermissionsUnchanged",
	"APIUserUnchanged"
]
__version__ = "1.26.0"


class APIException(Exception):
	"""The base class for all API exceptions.
	Has these default values:
		(HTTP) code: 500
		details: None
	"""

	code = helpers.STATUS_INTERNAL_SERVER_ERROR
	details = None

	def __init__(
		self: APIException,
		details: typing.Union[dict, str] = details  # TODO: PEP 604
	) -> None:
		self.details = details


class APIAuthorizationHeaderInvalid(APIException):
	"""Exception class for when the `"Authorization"; header is required and
	present, but not valid.
	(e.g. Basic instead of Bearer, when only Bearer is supported)
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIAuthorizationHeaderMissing(APIException):
	"""Exception class for when the `"Authorization"` header is required,
	but not present.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIForumChildLevelLimitReached(APIException):
	"""Exception class for when a user attempts to create a forum whose
	child level is above the config's `FORUM_MAX_CHILD_LEVEL` value.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumNotFound(APIException):
	"""Exception class for when a requested forum
	(e.g. /forums/invalid-uuid) does not exist.
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


class APIForumSubscriptionUnchanged(APIException):
	"""Exception class for when a user attempts to subscribe to /
	unsubscribe from a forum, but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIForumUnchanged(APIException):
	"""Exception class for when a user attempts to edit a forum,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotDeleteLastDefault(APIException):
	"""Exception class for when a user attempts to delete the last group
	which is default for `*`.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotDeletePermissionsForLastDefault(APIException):
	"""Exception class for when a user attempts to delete permissions
	for the last group which is default for `*`.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupCannotLeavePermissionNullForLastDefault(APIException):
	"""Exception class for when a user attempts to set a permission whose
	value is `None` for the last group which is default for `*`.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIGroupNotFound(APIException):
	"""Exception class for when a requested group
	(e.g. /groups/invalid-uuid) does not exist.
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
	"""Exception class for a user attempts to obtain a guest token,
	but already has too many existing accounts which haven't yet expired.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIJSONInvalid(APIException):
	"""Exception class for when the JSON data sent to our API is invalid,
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
	cannot be decoded. (e.g. missing a character)
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJWTInvalidClaims(APIException):
	"""Exception class for when the provided JWT is valid,
	but its claims are not.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIJWTUserNotFound(APIException):
	"""Exception class for when the provided JWT is valid,
	but its user has since been deleted.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIMessageNotFound(APIException):
	"""Exception class for when a requested message
	(e.g. /messages/invalid-uuid) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APINoPermission(APIException):
	"""Exception class for when a user attempts to perform an action they do not
	have permission to.
	"""

	code = helpers.STATUS_UNAUTHORIZED


class APINotificationNotFound(APIException):
	"""Exception class for when a requested notification
	(e.g. /notifications/invalid-uuid) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIOpenIDAuthenticationFailed(APIException):
	"""Exception class for when there was an issue contacting
	the OpenID server, etc.
	"""

	code = helpers.STATUS_UNAUTHORIZED


class APIOpenIDNonceInvalid(APIException):
	"""Exception class for when a user tries to authorize with OpenID and
	presents a correct state, but the retrieved nonce does not match.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIOpenIDServiceNotFound(APIException):
	"""Exception class for when a requested OpenID service
	(e.g. /openid/login/invalid_service) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIOpenIDStateInvalid(APIException):
	"""Exception class for when a user attempts to authorize with OpenID,
	but presents an invalid state.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIPostNotFound(APIException):
	"""Exception class for when a requested post
	(e.g. /posts/invalid-uuid) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIPostUnchanged(APIException):
	"""Exception class for when a user attempts to edit a post,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIPostVoteNotFound(APIException):
	"""Exception class for when a requested post vote
	(e.g. DELETE /posts/valid-uuid/vote) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIPostVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a post,
	but has already done so before and hasn't changed their vote.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIThreadLocked(APIException):
	"""Exception for when a user attempts to make posts in a locked thread."""

	code = helpers.STATUS_FORBIDDEN


class APIThreadNotFound(APIException):
	"""Exception class for when a requested thread
	(e.g. /threads/invalid-uuid) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIThreadSubscriptionUnchanged(APIException):
	"""Exception class for when a user attempts to subscribe to /
	unsubscribe from a thread, but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIThreadUnchanged(APIException):
	"""Exception class for when a user attempts to edit a thread,
	but all values are the exact same as the existing ones.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIThreadVoteNotFound(APIException):
	"""Exception class for when a requested thread vote
	(e.g. DELETE /threads/valid-uuid/vote) does not exist.
	"""

	code = helpers.STATUS_NOT_FOUND


class APIThreadVoteUnchanged(APIException):
	"""Exception class for when a user attempts to vote on a thread,
	but has already done so before and hasn't changed their vote.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserAvatarInvalid(APIException):
	"""Exception class for when a user attempts to set another user's avatar,
	but the base64 data contained within the request is somehow invalid.
	"""

	code = helpers.STATUS_BAD_REQUEST


class APIUserAvatarNotFound(APIException):
	"""Exception class for when a user attempts to delete another user's avatar,
	but they don't have one set.
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
	"""Exception class for when a user attempst to ban another user,
	but the expiration timestamp is in the past.
	"""

	code = helpers.STATUS_FORBIDDEN


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


class APIUserBlockUnchanged(APIException):
	"""Exception class for when a user attempts to block / unblock another user,
	but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserCannotRemoveLastDefaultGroup(APIException):
	"""Exception class for when a user attempts to remove the last group which
	is default for `*` from another user.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserFollowUnchanged(APIException):
	"""Exception class for when a user attempts to follow /
	unfollow another user, but has already done so before.
	"""

	code = helpers.STATUS_FORBIDDEN


class APIUserNotFound(APIException):
	"""Exception class for when a requested user
	(e.g. /users/invalid-uuid) does not exist.
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
