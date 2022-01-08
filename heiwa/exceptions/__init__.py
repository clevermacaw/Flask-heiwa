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
__version__ = "1.33.0"


class APIException(Exception):
	"""The base class for all API exceptions."""

	code = statuses.INTERNAL_SERVER_ERROR
	"""The HTTP error code of an exception. By default, this will be
	:attr:`INTERNAL_SERVER_ERROR <heiwa.statuses.INTERNAL_SERVER_ERROR>`.
	"""

	details = None
	"""The details about an exception. :data:`None` by default."""

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
		**kwargs
	) -> None:
		"""Sets the :attr:`details <.APIException.details>` class variable to the
		given value. If this method isn't used, it remains :data:`None`.
		"""

		self.details = details

		Exception.__init__(self, **kwargs)


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
	does not exist.
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
	:attr:`default_for <heiwa.database.Group.default_for>` column contains ``*``,
	or edit it in such a way that it no longer contains that value there.
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


class APIGroupCannotLeavePermissionNullForLastDefault(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` to set any
	permission as :data:`None` to the last :class:`Group <heiwa.database.Group>`
	whose :attr:`default_for <heiwa.database.Group.default_for>` column contains
	``*``.

	.. seealso::
		:class:`GroupPermissions <heiwa.database.GroupPermissions>`
	"""

	code = statuses.FORBIDDEN


class APIGroupNotFound(APIException):
	"""Exception class for when a requested :class:`Group <heiwa.database.Group>`
	was not found.
	"""

	code = statuses.NOT_FOUND


class APIGroupPermissionsNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete a :class:`Group <heiwa.database.Group>`'s permissions, but there are
	none.

	.. seealso::
		:class:`GroupPermissions <heiwa.database.GroupPermissions>`
	"""

	code = statuses.NOT_FOUND


class APIGroupPermissionsUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	change a :class:`Group <heiwa.database.Group>`'s permissions, but has not
	changed a single one of their values.
	"""

	code = statuses.FORBIDDEN


class APIGroupUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit a :class:`Group <heiwa.database.Group>`, but has not changed a single one
	of its attributes.
	"""

	code = statuses.FORBIDDEN


class APIGuestSessionLimitReached(APIException):
	"""Exception class for when a visitor attempts to obtain a guest
	:class:`User <heiwa.database.User>` account through the
	:mod:`guest <heiwa.views.guest>` endpoint, but too many guests have already
	registered with the same IP address within the specified amount of time.
	These values can be changed using the ``GUEST_MAX_SESSIONS_PER_IP`` and
	``GUEST_SESSION_EXPIRES_AFTER`` config values.
	"""

	code = statuses.FORBIDDEN


class APIJSONInvalid(APIException):
	"""Exception class for when the JSON data sent to an API endpoint which
	requires input validation did not pass it. This will usually also be raised
	with details about which data there was an issue with included in the details.

	.. seealso::
		:class:`heiwa.validators.APIValidator`
	"""

	code = statuses.BAD_REQUEST


class APIJSONMissing(APIException):
	"""Exception class for when an API endpoint was excepting to receive JSON
	data, but there was none.

	.. seealso::
		:decorator:`heiwa.validators.validate_json`
	"""

	code = statuses.BAD_REQUEST


class APIJWTInvalid(APIException):
	"""Exception class for when a JWT (usually provided in the ``Authorization``
	header) is not at all valid, and could not be decoded.

	.. seealso::
		:decorator:`heiwa.authentication.authenticate_via_jwt`
	"""

	code = statuses.BAD_REQUEST


class APIJWTInvalidClaims(APIException):
	"""Exception class for when a provided JWT is valid and could be decoded,
	but the claims contained within it are not. This can, for example, mean that
	it has expired.
	"""

	code = statuses.BAD_REQUEST


class APIJWTUserNotFound(APIException):
	"""Exception class for when a provided JWT and its claims are valid, but the
	:class:`User <heiwa.database.User>` they represent does not exist. Usually,
	this means that the user has been deleted.
	"""

	code = statuses.NOT_FOUND


class APIMessageCannotSendToSelf(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	send a :class:`Message <heiwa.database.Message>` to themselves.
	"""

	code = statuses.FORBIDDEN


class APIMessageCannotChangeIsReadOfSent(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	change the :attr:`is_read <heiwa.database.Message.is_read>` status of a
	:class:`Message <heiwa.database.Message>`, but they are also its sender.
	"""

	code = statuses.FORBIDDEN


class APIMessageNotFound(APIException):
	"""Exception class for when a requested
	:class:`Message <heiwa.database.Message>` was not found.
	"""

	code = statuses.NOT_FOUND


class APIMessageReceiverBlockedSender(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	send a :class:`Message <heiwa.database.Message>` to another user, but they
	have been blocked.

	.. seealso::
		:data:`heiwa.database.user_blocks`
	"""

	code = statuses.FORBIDDEN


class APIMessageUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit a :class:`Message <heiwa.database.Message>`, but has not changed a single
	one of its attributes.
	"""


class APINoPermission(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	perform an action they do not have permission to. For example, ``delete`` an
	instance of a :class:`Forum <heiwa.database.Forum>` when they are a default
	guest.

	.. seealso::
		:class:`heiwa.database.utils.PermissionControlMixin`
	"""

	code = statuses.UNAUTHORIZED


class APINotificationNotFound(APIException):
	"""Exception class for when a requested
	:class:`Notification <heiwa.database.Notification>` was not found.
	"""

	code = statuses.NOT_FOUND


class APIOpenIDAuthenticationFailed(APIException):
	"""Exception class for when an authentication via OpenID failed for any
	reason. This can, for example, be the specified server not responding or
	returning invalid data.
	"""

	code = statuses.UNAUTHORIZED


class APIOpenIDNonceInvalid(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` presents a
	correct state during an OpenID authentication process, but the nonce is
	invalid.
	"""

	code = statuses.BAD_REQUEST


class APIOpenIDServiceNotFound(APIException):
	"""Exception class for when a requested OpenID service was not found."""

	code = statuses.NOT_FOUND


class APIOpenIDStateInvalid(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` presents a
	correct nonce during an OpenID authentication process, but the state is
	invalid.
	"""

	code = statuses.BAD_REQUEST


class APIPostNotFound(APIException):
	"""Exception class for when a requested :class:`Post <heiwa.database.Post>`
	was not found.
	"""

	code = statuses.NOT_FOUND


class APIPostUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit a :class:`Post <heiwa.database.Post>`, but has not changed a single one
	of its attributes.
	"""

	code = statuses.FORBIDDEN


class APIPostVoteNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete their vote on a :class:`Post <heiwa.database.Post>`, but there is none
	to be found.

	.. seealso::
		:class:`heiwa.database.PostVote`
	"""

	code = statuses.NOT_FOUND


class APIPostVoteUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	change their vote on a :class:`Post <heiwa.database.Post>`, but has not
	changed any of its attributes. In this case, it will only be the
	:attr:`upvote <heiwa.database.PostVote.upvote>` attribute by default.

	.. seealso::
		:class:`heiwa.database.PostVote`
	"""

	code = statuses.FORBIDDEN


class APIRateLimitExceeded(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` has
	exceeded their rate limit for a specific API endpoint.

	.. seealso::
		:class:`heiwa.limiter.Limiter`
	"""

	code = 429


class APIThreadLocked(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	create a :class:`Post <heiwa.database.Post>` in, edit, or otherwise interact
	with a locked :class:`Thread <heiwa.database.Thread>`.
	"""

	code = statuses.FORBIDDEN


class APIThreadNotFound(APIException):
	"""Exception class for when a requested
	:class:`Thread <heiwa.database.Thread>` was not found.
	"""

	code = statuses.NOT_FOUND


class APIThreadSubscriptionAlreadyExists(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	subscribe to a :class:`Thread <heiwa.database.Thread>`, but has already done
	so before.

	.. seealso::
		:data:`heiwa.database.thread_subscribers`
	"""

	code = statuses.FORBIDDEN


class APIThreadSubscriptionNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	unsubscribe from a :class:`Thread <heiwa.database.Thread>`, but there is no
	subscription to be found.

	.. seealso::
		:data:`heiwa.database.thread_subscribers`
	"""

	code = statuses.NOT_FOUND


class APIThreadUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit a :class:`Thread <heiwa.database.Thread>`, but has not changed any of
	its attributes.
	"""

	code = statuses.FORBIDDEN


class APIThreadVoteNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete their vote on a :class:`Thread <heiwa.database.Thread>`, but there is
	none to be found.

	.. seealso::
		:class:`heiwa.database.ThreadVote`
	"""

	code = statuses.NOT_FOUND


class APIThreadVoteUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	change their vote on a :class:`Thread <heiwa.database.Thread>`, but has not
	changed any of its attributes. In this case, it will only be the
	:attr:`upvote <heiwa.database.ThreadVote.upvote>` attribute by default.

	.. seealso::
		:class:`heiwa.database.ThreadVote`
	"""

	code = statuses.FORBIDDEN


class APIUserAvatarInvalid(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	set an avatar, but the data contained within it is invalid.

	.. seealso::
		:attr:`heiwa.database.User.avatar`
	"""

	code = statuses.BAD_REQUEST


class APIUserAvatarNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete their (or someone else's) avatar, but there is none to be found.

	.. seealso::
		:attr:`heiwa.database.User.avatar`
	"""

	code = statuses.NOT_FOUND


class APIUserAvatarNotAllowedType(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	set an avatar, but its media type is not allowed. Which types are allowed is
	defined in the ``USER_AVATAR_TYPES`` config value.

	.. seealso::
		:attr:`heiwa.database.User.avatar`
	"""

	code = statuses.BAD_REQUEST


class APIUserAvatarTooLarge(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	set an avatar, but its file size is too large. The maximum allowed size is
	defined in the ``USER_MAX_AVATAR_SIZE`` config value.

	.. seealso::
		:attr:`heiwa.database.User.avatar`
	"""

	code = statuses.FORBIDDEN


class APIUserBanAlreadyExpired(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	ban another user, but the ban would've already expired by the time they've
	created it.

	.. seealso::
		:class:`heiwa.database.UserBan`
	"""

	code = statuses.FORBIDDEN


class APIUserBanNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	remove another user's ban, but there is none to be found.

	.. seealso::
		:class:`heiwa.database.UserBan`
	"""

	code = statuses.NOT_FOUND


class APIUserBanUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit another user's ban, but has not changed a single one of its attributes.

	.. seealso::
		:class:`heiwa.database.UserBan`
	"""

	code = statuses.FORBIDDEN


class APIUserBanned(APIException):
	"""Exception class for when an authenticated
	:class:`User <heiwa.database.User>` attempts to access an API endpoint, but
	they have been banned.

	.. seealso::
		:attr:`heiwa.database.User.is_banned`

		:class:`heiwa.database.UserBan`
	"""

	code = statuses.FORBIDDEN


class APIUserBlockAlreadyExists(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	block another user, but has already done so before.

	.. seealso::
		:data:`heiwa.database.user_blocks`
	"""

	code = statuses.FORBIDDEN


class APIUserBlockNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	unblock another user, but there is no block to be found.

	.. seealso::
		:data:`heiwa.database.user_blocks`
	"""

	code = statuses.NOT_FOUND


class APIUserCannotRemoveLastDefaultGroup(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	remove the last assigned :class:`Group <heiwa.database.Group>` whose
	:attr:`default_for <heiwa.database.Group.default_for>` column contains ``*``.

	.. seealso::
		:data:`heiwa.database.user_groups`
	"""

	code = statuses.FORBIDDEN


class APIUserFollowAlreadyExists(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	follow another user, but has already done so in the past.

	.. seealso::
		:data:`heiwa.database.user_follows`
	"""

	code = statuses.FORBIDDEN


class APIUserFollowNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	unfollow another user, but there is no follow to be found.

	.. seealso::
		:data:`heiwa.database.user_follows`
	"""

	code = statuses.NOT_FOUND


class APIUserGroupAlreadyAdded(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	assign a :class:`Group <heiwa.database.Group>` to another user (or
	themselves), but it's already been assigned before.

	.. seealso::
		:data:`heiwa.database.user_groups`
	"""

	code = statuses.FORBIDDEN


class APIUserGroupNotAdded(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	remove a :class:`Group <heiwa.database.Group>` from another user (or
	themselves), but it's never been assigned in the first place.

	.. seealso::
		:data:`heiwa.database.user_groups`
	"""

	code = statuses.FORBIDDEN


class APIUserNotFound(APIException):
	"""Exception class for when a requested :class:`User <heiwa.database.User>`
	does not exist.
	"""

	code = statuses.NOT_FOUND


class APIUserPermissionsNotFound(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	delete another user's (or their own) permissions, but there are none to be
	found.

	.. seealso::
		:class:`heiwa.database.UserPermissions`
	"""

	code = statuses.NOT_FOUND


class APIUserPermissionsUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit another user's (or their own) permissions, but has not changed a single
	one of their values.

	.. seealso::
		:class:`heiwa.database.UserPermissions`
	"""

	code = statuses.FORBIDDEN


class APIUserUnchanged(APIException):
	"""Exception class for when a :class:`User <heiwa.database.User>` attempts to
	edit another user (or themselves), but has not changed a single one of their
	attributes.
	"""

	code = statuses.FORBIDDEN
