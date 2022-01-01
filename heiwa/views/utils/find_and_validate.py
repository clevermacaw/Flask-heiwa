import uuid

import sqlalchemy.orm

import heiwa.database
import heiwa.exceptions

from .query import generate_parsed_forum_permissions_exist_query

__all__ = [
	"find_category_by_id",
	"find_forum_by_id",
	"find_group_by_id",
	"find_thread_by_id",
	"find_user_by_id",
	"validate_category_exists",
	"validate_forum_exists",
	"validate_thread_exists",
	"validate_user_exists"
]


def find_category_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Category:
	"""Returns the :class:`Category <heiwa.database.Category>` with the given
	``id_``, as long as there is one and the ``user`` has permission to view it.
	If the category falls under a :class:`Forum <heiwa.database.Forum>`, its
	permissions are taken into account - and parsed, if that hasn't happened
	already.

	.. seealso::
		:meth:`Forum.reparse_permissions <heiwa.database.Forum.reparse_permissions>`
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.database.Category.forum_id
			== heiwa.database.ForumParsedPermissions.forum_id
		),
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Category,
				parsed_forum_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Category.id == id_,
					sqlalchemy.or_(
						sqlalchemy.and_(
							# Evaluating here is the shortest option, line-wise.
							user.parsed_permissions["category_view"],
							heiwa.database.Category.forum_id.is_(None)
						),
						sqlalchemy.or_(
							~parsed_forum_permissions_exist_query,
							generate_parsed_forum_permissions_exist_query(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.category_view.is_(True)
								)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APICategoryNotFound

		category, parsed_forum_permissions_exist = row

		if parsed_forum_permissions_exist:
			break

		session.execute(
			sqlalchemy.select(heiwa.database.Forum).
			where(heiwa.database.Forum.id == category.forum_id)
		).scalars().one().reparse_permissions(user)

		session.commit()

	return category


def find_forum_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Forum:
	"""Returns the forum with the given ``id_``. Raises
	``heiwa.exceptions.APIForumNotFound`` if it doesn't exist, or the given
	``user`` doesn't have permission to view it. If parsed permissions don't
	exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		heiwa.database.Forum.id == heiwa.database.ForumParsedPermissions.forum_id,
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Forum.id,
				parsed_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Forum.id == id_,
					sqlalchemy.or_(
						~parsed_permissions_exist_query,
						generate_parsed_forum_permissions_exist_query(
							sqlalchemy.and_(
								inner_conditions,
								heiwa.database.ForumParsedPermissions.forum_view.is_(True)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APIForumNotFound

		forum, parsed_permissions_exist = row

		if parsed_permissions_exist:
			break

		forum.reparse_permissions(user)

		session.commit()

	return forum


def find_group_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session
) -> heiwa.database.Group:
	"""Returns the group with the given ``id_``. Raises
	``heiwa.exceptions.APIGroupNotFound`` if it doesn't exist.
	"""

	group = session.execute(
		sqlalchemy.select(heiwa.database.Group).
		where(heiwa.database.Group.id == id_)
	).scalars().one_or_none()

	if group is None:
		raise heiwa.exceptions.APIGroupNotFound(id_)

	return group


def find_thread_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Thread:
	"""Returns the thread with the given ``id_``. Raises
	``heiwa.exceptions.APIThreadNotFound`` if it doesn't exist, or the given
	``user`` doesn't have permission to view it. If parsed permissions don't
	exist for the respective forum, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.database.Thread.forum_id
			== heiwa.database.ForumParsedPermissions.forum_id
		),
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Thread,
				parsed_forum_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Thread.id == id_,
					sqlalchemy.or_(
						~parsed_forum_permissions_exist_query,
						generate_parsed_forum_permissions_exist_query(
							sqlalchemy.and_(
								inner_conditions,
								heiwa.database.ForumParsedPermissions.thread_view.is_(True)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APIThreadNotFound

		thread, parsed_forum_permissions_exist = row

		if parsed_forum_permissions_exist:
			break

		thread.forum.reparse_permissions(user)

		session.commit()

	return thread


def find_user_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session
) -> heiwa.database.User:
	"""Returns the user with the given ``id_``. Raises
	``heiwa.exceptions.APIUserNotFound`` if they don't exist.
	"""

	user = session.execute(
		sqlalchemy.select(heiwa.database.User).
		where(heiwa.database.User.id == id_)
	).scalars().one_or_none()

	if user is None:
		raise heiwa.exceptions.APIUserNotFound(id_)

	return user


def validate_category_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Raises
	:exc:`APICategoryNotFound <heiwa.exceptions.APICategoryNotFound>` if the
	:class:`Category <heiwa.database.Category>` with the given ``id_`` does not
	exist, or ``user`` does not have permission to view it.

	.. seealso::
		:meth:`Forum.reparse_permissions <heiwa.database.Forum.reparse_permissions>`
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.database.Category.forum_id
			== heiwa.database.ForumParsedPermissions.forum_id
		),
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Category,
				parsed_forum_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Category.id == id_,
					sqlalchemy.or_(
						sqlalchemy.and_(
							# Evaluating here is the shortest option, line-wise.
							user.parsed_permissions["category_view"],
							heiwa.database.Category.forum_id.is_(None)
						),
						sqlalchemy.or_(
							~parsed_forum_permissions_exist_query,
							generate_parsed_forum_permissions_exist_query(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.category_view.is_(True)
								)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APICategoryNotFound

		category, parsed_forum_permissions_exist = row

		if parsed_forum_permissions_exist:
			break

		session.execute(
			sqlalchemy.select(heiwa.database.Forum).
			where(heiwa.database.Forum.id == category.forum_id)
		).scalars().one().reparse_permissions(user)

		session.commit()


def validate_forum_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Raises ``heiwa.exceptions.APIForumNotFound`` if the forum with the given
	``id_`` doesn't exist, or ``user`` does not have permission to view it. If
	parsed permissions don't exist, they're automatically calculated. If the
	category falls under a :class:`Forum <heiwa.database.Forum>`, its permissions
	are taken into account - and parsed, if that hasn't happened already.
	"""

	inner_conditions = sqlalchemy.and_(
		heiwa.database.Forum.id == heiwa.database.ForumParsedPermissions.forum_id,
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Forum.id,
				parsed_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Forum.id == id_,
					sqlalchemy.or_(
						~parsed_permissions_exist_query,
						generate_parsed_forum_permissions_exist_query(
							sqlalchemy.and_(
								inner_conditions,
								heiwa.database.ForumParsedPermissions.forum_view.is_(True)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APIForumNotFound

		forum_id, parsed_permissions_exist = row

		if parsed_permissions_exist:
			break

		session.execute(
			sqlalchemy.select(heiwa.database.Forum).
			where(heiwa.database.Forum.id == forum_id)
		).scalars().one().reparse_permissions()

		session.commit()


def validate_thread_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Thread:
	"""Raises ``heiwa.exceptions.APIThreadNotFound`` if the thread with the given
	``id_`` doesn't exist, or ``user`` does not have permission to view it. If
	its forum's parsed permissions don't exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.database.Thread.forum_id
			== heiwa.database.ForumParsedPermissions.forum_id
		),
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	parsed_forum_permissions_exist_query = (
		generate_parsed_forum_permissions_exist_query(inner_conditions)
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Thread.forum_id,
				parsed_forum_permissions_exist_query
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Thread.id == id_,
					sqlalchemy.or_(
						~parsed_forum_permissions_exist_query,
						generate_parsed_forum_permissions_exist_query(
							sqlalchemy.and_(
								inner_conditions,
								heiwa.database.ForumParsedPermissions.thread_view.is_(True)
							)
						)
					)
				)
			)
		).one_or_none()

		if row is None:
			raise heiwa.exceptions.APIThreadNotFound

		forum_id, parsed_forum_permissions_exist = row

		if parsed_forum_permissions_exist:
			break

		session.execute(
			sqlalchemy.select(heiwa.database.Forum).
			where(heiwa.database.Forum.id == forum_id)
		).scalars().one().reparse_permissions(user)

		session.commit()


def validate_user_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session
) -> None:
	"""Raises ``heiwa.exceptions.APIUserNotFound`` if the user with the given
	``id_`` doesn't exist.
	"""

	if not session.execute(
		sqlalchemy.select(heiwa.database.User.id).
		where(heiwa.database.User.id == id_).
		exists().
		select()
	).scalars().one():
		raise heiwa.exceptions.APIUserNotFound(id_)
