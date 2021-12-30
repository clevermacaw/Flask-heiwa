import typing

import sqlalchemy

import heiwa.database

__all__ = ["generate_parsed_forum_permissions_exist_query"]


def generate_parsed_forum_permissions_exist_query(
	conditions: typing.Union[
		sqlalchemy.sql.expression.BinaryExpression,
		sqlalchemy.sql.expression.ClauseList
	]
) -> sqlalchemy.sql.selectable.Exists:
	"""Returns a query which returns whether or not an instance of
	:class:`ForumParsedPermissions <heiwa.database.ForumParsedPermissions>`
	exists, when searched for with the given ``conditions``.

	This is useful in queries where this condition repeats a lot. For example,
	the :func:`thread.list_ <heiwa.views.thread.list_>` endpoint, where we need
	to look for cached calculated forum permissions based on translated
	permissions, as well as the permissions' existence.

	.. seealso::
		:class:`heiwa.database.ForumParsedPermissions`
	"""

	return (
		sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
		where(conditions).
		exists()
	)
