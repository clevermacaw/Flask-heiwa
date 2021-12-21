import uuid

import sqlalchemy.orm

import heiwa.exceptions
import heiwa.models

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
	user: heiwa.models.User
) -> heiwa.models.Forum:
	"""Returns the forum with the given ``id_``. Raises
	``heiwa.exceptions.APIForumNotFound`` if it doesn't exist, or the given
	``user`` doesn't have permission to view it. If parsed permissions don't
	exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		heiwa.models.Forum.id == heiwa.models.ForumParsedPermissions.forum_id,
		heiwa.models.ForumParsedPermissions.user_id == user.id
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.models.Forum,
				(
					sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.models.Forum.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.models.ForumParsedPermissions.forum_view.is_(True)
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
) -> heiwa.models.Group:
	"""Returns the group with the given ``id_``. Raises
	``heiwa.exceptions.APIGroupNotFound`` if it doesn't exist.
	"""

	group = session.execute(
		sqlalchemy.select(heiwa.models.Group).
		where(heiwa.models.Group.id == id_)
	).scalars().one_or_none()

	if group is None:
		raise heiwa.exceptions.APIGroupNotFound(id_)

	return group


def find_thread_by_id(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.models.User
) -> heiwa.models.Thread:
	"""Returns the thread with the given ``id_``. Raises
	``heiwa.exceptions.APIThreadNotFound`` if it doesn't exist, or the given
	``user`` doesn't have permission to view it. If parsed permissions don't
	exist for the respective forum, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.models.Thread.forum_id
			== heiwa.models.ForumParsedPermissions.forum_id
		),
		heiwa.models.ForumParsedPermissions.user_id == user.id
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.models.Thread,
				(
					sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.models.Thread.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.models.ForumParsedPermissions.thread_view.is_(True)
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
) -> heiwa.models.User:
	"""Returns the user with the given ``id_``. Raises
	``heiwa.exceptions.APIUserNotFound`` if they don't exist.
	"""

	user = session.execute(
		sqlalchemy.select(heiwa.models.User).
		where(heiwa.models.User.id == id_)
	).scalars().one_or_none()

	if user is None:
		raise heiwa.exceptions.APIUserNotFound(id_)

	return user


def validate_forum_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.models.User
) -> None:
	"""Raises ``heiwa.exceptions.APIForumNotFound`` if the forum with the given
	``id_`` doesn't exist, or ``user`` does not have permission to view it. If
	parsed permissions don't exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		heiwa.models.Forum.id == heiwa.models.ForumParsedPermissions.forum_id,
		heiwa.models.ForumParsedPermissions.user_id == user.id
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.models.Forum.id,
				(
					sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.models.Forum.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.models.ForumParsedPermissions.forum_view.is_(True)
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
				sqlalchemy.select(heiwa.models.Forum).
				where(heiwa.models.Forum.id == forum_id)
			).scalars().one().reparse_permissions(user)

			session.commit()
		else:
			raise heiwa.exceptions.APIForumNotFound


def validate_thread_exists(
	id_: uuid.UUID,
	session: sqlalchemy.orm.Session,
	user: heiwa.models.User
) -> heiwa.models.Thread:
	"""Raises ``heiwa.exceptions.APIThreadNotFound`` if the thread with the given
	``id_`` doesn't exist, or ``user`` does not have permission to view it. If
	its forum's parsed permissions don't exist, they're automatically calculated.
	"""

	inner_conditions = sqlalchemy.and_(
		(
			heiwa.models.Thread.forum_id
			== heiwa.models.ForumParsedPermissions.forum_id
		),
		heiwa.models.ForumParsedPermissions.user_id == user.id
	)

	while True:
		row = session.execute(
			sqlalchemy.select(
				heiwa.models.Thread.forum_id,
				(
					sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
					where(inner_conditions).
					exists()
				)
			).
			where(
				sqlalchemy.and_(
					heiwa.models.Thread.id == id_,
					sqlalchemy.or_(
						~(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(inner_conditions).
							exists()
						),
						(
							sqlalchemy.select(heiwa.models.ForumParsedPermissions.forum_id).
							where(
								sqlalchemy.and_(
									inner_conditions,
									heiwa.models.ForumParsedPermissions.thread_view.is_(True)
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
				sqlalchemy.select(heiwa.models.Forum).
				where(heiwa.models.Forum.id == forum_id)
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
		sqlalchemy.select(heiwa.models.User.id).
		where(heiwa.models.User.id == id_).
		exists().
		select()
	).scalars().one():
		raise heiwa.exceptions.APIUserNotFound(id_)
