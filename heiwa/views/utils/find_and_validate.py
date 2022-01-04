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
	""" TODO """

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
	""" TODO """

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
	""" TODO """

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
	""" TODO """

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
	""" TODO """

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
	""" TODO """

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

	return


def validate_forum_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	""" TODO """

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
	""" TODO """

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
	""" TODO """

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
