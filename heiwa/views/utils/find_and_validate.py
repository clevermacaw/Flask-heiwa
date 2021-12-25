import uuid

import sqlalchemy.orm

import heiwa.database
import heiwa.exceptions

__all__ = [
	"find_forum_by_id",
	"find_group_by_id",
	"find_thread_by_id",
	"find_user_by_id",
	"validate_forum_exists",
	"validate_thread_exists",
	"validate_user_exists"
]


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

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Forum,
				(
					sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Forum.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.forum_view.is_(True)
								)
							).
							exists()
						)
					)
				)
			)
		).one_or_none()

		if row is not None:
			forum, parsed_permissions_exist = row

			if parsed_permissions_exist:
				break

			forum.reparse_permissions(user)

			session.commit()
		else:
			raise heiwa.exceptions.APIForumNotFound

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

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Thread,
				(
					sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Thread.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.thread_view.is_(True)
								)
							).
							exists()
						)
					)
				)
			)
		).one_or_none()

		if row is not None:
			thread, parsed_forum_permissions_exist = row

			if parsed_forum_permissions_exist:
				break

			thread.forum.reparse_permissions(user)

			session.commit()
		else:
			raise heiwa.exceptions.APIThreadNotFound

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


def validate_forum_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.database.User
) -> None:
	"""Raises ``heiwa.exceptions.APIForumNotFound`` if the forum with the given
	``id_`` doesn't exist, or ``user`` does not have permission to view it. If
	parsed permissions don't exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		heiwa.database.Forum.id == heiwa.database.ForumParsedPermissions.forum_id,
		heiwa.database.ForumParsedPermissions.user_id == user.id
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Forum.id,
				(
					sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Forum.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.forum_view.is_(True)
								)
							).
							exists()
						)
					)
				)
			)
		).one_or_none()

		if row is not None:
			forum_id, parsed_permissions_exist = row

			if parsed_permissions_exist:
				break

			session.execute(
				sqlalchemy.select(heiwa.database.Forum).
				where(heiwa.database.Forum.id == forum_id)
			).scalars().one().reparse_permissions(user)

			session.commit()
		else:
			raise heiwa.exceptions.APIForumNotFound


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

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.database.Thread.forum_id,
				(
					sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.database.Thread.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.database.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.database.ForumParsedPermissions.thread_view.is_(True)
								)
							).
							exists()
						)
					)
				)
			)
		).one_or_none()

		if row is not None:
			forum_id, parsed_forum_permissions_exist = row

			if parsed_forum_permissions_exist:
				break

			session.execute(
				sqlalchemy.select(heiwa.database.Forum).
				where(heiwa.database.Forum.id == forum_id)
			).scalars().one().reparse_permissions(user)

			session.commit()
		else:
			raise heiwa.exceptions.APIThreadNotFound


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
