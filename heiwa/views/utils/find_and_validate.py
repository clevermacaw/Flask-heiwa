import uuid

import sqlalchemy.orm

import heiwa.database
import heiwa.exceptions

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
	"""Finds the :class:`Category <heiwa.database.Category>` with the given ID.

	:param id_: The :attr:`id <heiwa.database.Category.id>` of the category to
		find.
	:param session: The session to find the category with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the category.

	:raises heiwa.exceptions.APICategoryNotFound: Raised when the category doesn't
		exist, or the user does not have permission to view it.

	:returns: The category.
	"""

	category = session.execute(
		heiwa.database.Category.get(
			user,
			session,
			conditions=(heiwa.database.Category.id == id_)
		)
	).scalars().one_or_none()

	if category is None:
		raise heiwa.exceptions.APICategoryNotFound

	return category


def find_forum_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Forum:
	"""Finds the :class:`Forum <heiwa.database.Forum>` with the given ID.

	:param id_: The :attr:`id <heiwa.database.Forum.id>` of the forum to find.
	:param session: The session to find the forum with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the forum.

	:raises heiwa.exceptions.APIForumNotFound: Raised when the forum doesn't
		exist, or the user does not have permission to view it.

	:returns: The forum.
	"""

	forum = session.execute(
		heiwa.database.Forum.get(
			user,
			session,
			conditions=(heiwa.database.Forum.id == id_)
		)
	).scalars().one_or_none()

	if forum is None:
		raise heiwa.exceptions.APIForumNotFound

	return forum


def find_group_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Group:
	"""Finds the :class:`Group <heiwa.database.Group>` with the given ID.

	:param id_: The :attr:`id <heiwa.database.Group.id>` of the group to find.
	:param session: The session to find the group with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the group.

	:raises heiwa.exceptions.APIGroupNotFound: Raised when the group doesn't
		exist, or the user does not have permission to view it.

	:returns: The group.
	"""

	group = session.execute(
		heiwa.database.Group.get(
			user,
			session,
			conditions=(heiwa.database.Group.id == id_)
		)
	).scalars().one_or_none()

	if group is None:
		raise heiwa.exceptions.APIGroupNotFound(id_)

	return group


def find_thread_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Thread:
	"""Finds the :class:`Thread <heiwa.database.Thread>` with the given ID.

	:param id_: The :attr:`id <heiwa.database.Thread.id>` of the thread to find.
	:param session: The session to find the thread with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the thread.

	:raises heiwa.exceptions.APIThreadNotFound: Raised when the thread doesn't
		exist, or the user does not have permission to view it.

	:returns: The thread.
	"""

	thread = session.execute(
		heiwa.database.Thread.get(
			user,
			session,
			conditions=(heiwa.database.Thread.id == id_)
		)
	).scalars().one_or_none()

	if thread is None:
		raise heiwa.exceptions.APIThreadNotFound(id_)

	return thread


def find_user_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.User:
	"""Finds the :class:`User <heiwa.database.User>` with the given ID.

	:param id_: The :attr:`id <heiwa.database.User.id>` of the user to find.
	:param session: The session to find the user with.
	:param user: The user who must have permission to view the requested user.

	:raises heiwa.exceptions.APIUserNotFound: Raised when the requested user
		doesn't exist, or ``user`` lacks the permission to view them.

	:returns: The user.
	"""

	user = session.execute(
		heiwa.database.User.get(
			user,
			session,
			conditions=(heiwa.database.User.id == id_)
		)
	).scalars().one_or_none()

	if user is None:
		raise heiwa.exceptions.APIUserNotFound(id_)

	return user


def validate_category_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Validates that the :class:`Category <heiwa.database.Category>` with the
	given ID exists.

	:param id_: The :attr:`id <heiwa.database.Category.id>` of the category to
		find.
	:param session: The session to find the category with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the category.

	:raises heiwa.exceptions.APICategoryNotFound: Raised when the category doesn't
		exist, or the user does not have permission to view it.
	"""

	if (
		session.execute(
			heiwa.database.Category.get(
				user,
				session,
				conditions=(heiwa.database.Category.id == id_),
				ids_only=True
			)
		).scalars().one_or_none()
	) is None:
		raise heiwa.exceptions.APICategoryNotFound(id_)


def validate_forum_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Validates that the :class:`Forum <heiwa.database.Forum>` with the given
	ID exists.

	:param id_: The :attr:`id <heiwa.database.Forum.id>` of the forum to find.
	:param session: The session to find the forum with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the forum.

	:raises heiwa.exceptions.APIForumNotFound: Raised when the forum doesn't
		exist, or the user does not have permission to view it.
	"""

	if not session.execute(
		sqlalchemy.select(
			heiwa.database.Forum.get(
				user,
				session,
				conditions=(heiwa.database.Forum.id == id_),
				ids_only=True
			)
		).
		exists().
		select()
	).scalars().one():
		raise heiwa.exceptions.APIForumNotFound(id_)


def validate_thread_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> heiwa.database.Thread:
	"""Validates that the :class:`Thread <heiwa.database.Thread>` with the given
	ID exists.

	:param id_: The :attr:`id <heiwa.database.Thread.id>` of the thread to find.
	:param session: The session to find the thread with.
	:param user: The :class:`User <heiwa.database.User>` who must have permission
		to view the thread.

	:raises heiwa.exceptions.APIThreadNotFound: Raised when the thread doesn't
		exist, or the user does not have permission to view it.
	"""

	if not session.execute(
		sqlalchemy.select(
			heiwa.database.Forum.get(
				user,
				session,
				conditions=(heiwa.database.Forum.id == id_),
				ids_only=True
			)
		).
		exists().
		select()
	).scalars().one():
		raise heiwa.exceptions.APIForumNotFound(id_)


def validate_user_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Validates that the :class:`User <heiwa.database.User>` with the given ID
	exists.

	:param id_: The :attr:`id <heiwa.database.User.id>` of the user to find.
	:param session: The session to find the user with.
	:param user: The user who must have permission to view the requested user.

	:raises heiwa.exceptions.APIUserNotFound: Raised when the requested user
		doesn't exist, or ``user`` lacks the permission to view them.
	"""

	if not session.execute(
		sqlalchemy.select(
			heiwa.database.User.get(
				user,
				session,
				conditions=(heiwa.database.User.id == id_),
				ids_only=True
			)
		).
		exists().
		select()
	).scalars().one():
		raise heiwa.exceptions.APIUserNotFound(id_)
