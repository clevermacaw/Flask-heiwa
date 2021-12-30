from __future__ import annotations

import datetime
import typing

import sqlalchemy
import sqlalchemy.orm

from .generators import generate_uuid
from .types import UUID

__all__ = [
	"BasePermissionMixin",
	"CDWMixin",
	"CreationTimestampMixin",
	"EditInfoMixin",
	"IdMixin",
	"PermissionControlMixin",
	"ReprMixin"
]


@sqlalchemy.orm.declarative_mixin
class BasePermissionMixin:
	"""A helper mixin with columns corresponding to all permissions recognized
	by default, as well as the ``to_permissions`` method to convert them to a
	dictionary, and a static ``DEFAULT_PERMISSIONS`` dictionary with their default
	values.
	"""

	category_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	category_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	group_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	group_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	group_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	group_edit_permissions = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	post_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_lock_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_lock_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_pin = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_edit_vote = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_move_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	thread_view = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	user_delete = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	user_edit = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	user_edit_ban = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	user_edit_groups = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	user_edit_permissions = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)

	DEFAULT_PERMISSIONS = {
		"category_create": None,
		"category_delete": None,
		"category_edit": None,
		"category_view": None,
		"forum_create": None,
		"forum_delete": None,
		"forum_edit": None,
		"forum_merge": None,
		"forum_move": None,
		"forum_view": None,
		"group_create": None,
		"group_delete": None,
		"group_edit": None,
		"group_edit_permissions": None,
		"post_create": None,
		"post_delete_own": None,
		"post_delete_any": None,
		"post_edit_own": None,
		"post_edit_any": None,
		"post_edit_vote": None,
		"post_move_own": None,
		"post_move_any": None,
		"post_view": None,
		"thread_create": None,
		"thread_delete_own": None,
		"thread_delete_any": None,
		"thread_edit_own": None,
		"thread_edit_any": None,
		"thread_edit_lock_own": None,
		"thread_edit_lock_any": None,
		"thread_edit_pin": None,
		"thread_edit_vote": None,
		"thread_merge_own": None,
		"thread_merge_any": None,
		"thread_move_own": None,
		"thread_move_any": None,
		"thread_view": None,
		"user_delete": None,
		"user_edit": None,
		"user_edit_ban": None,
		"user_edit_groups": None,
		"user_edit_permissions": None
	}

	def to_permissions(self: BasePermissionMixin) -> typing.Dict[
		str,
		typing.Union[
			None,
			bool
		]
	]:
		"""Transforms the values in this instance to the standard format for
		permissions. (A dictionary, where string keys represent permissions,
		and their value represents whether or not they're granted.
		"""

		return {
			permission_name: getattr(self, permission_name)
			for permission_name in self.DEFAULT_PERMISSIONS
		}


@sqlalchemy.orm.declarative_mixin
class CDWMixin:
	"""A helper mixin with ``create``, ``write`` and ``delete`` methods."""

	@classmethod
	def create(
		cls: CDWMixin,
		session: sqlalchemy.orm.Session,
		*args,
		**kwargs
	):
		"""Creates an instance of the mixed-in class and runs its the ``write``
		method.
		"""

		self = cls(
			*args,
			**kwargs
		)

		self.write(session)

		return self

	def delete(
		self: CDWMixin,
		session: typing.Union[
			None,
			sqlalchemy.orm.Session
		] = None
	) -> None:
		"""Deletes the current instance of the mixed-in class from the provided
		``session``. If the ``session`` argument is ``None``, it's set to this
		object's session.
		"""

		if session is None:
			session = sqlalchemy.orm.object_session(self)

		session.delete(self)

	def write(
		self: CDWMixin,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Adds the current instance of the mixed-in class to the provided
		``session``.
		"""

		session.add(self)


@sqlalchemy.orm.declarative_mixin
class CreationTimestampMixin:
	"""A helper mixin that adds a timezone-aware timestamp column named
	``creation_timestamp``, whose default value is the time of row insertion.
	"""

	creation_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		default=datetime.datetime.now,
		nullable=False
	)


@sqlalchemy.orm.declarative_mixin
class EditInfoMixin:
	"""A helper mixin which contains information about the mixed-in object's
	edits.

	Contains:

	#. A timezone-aware timestamp column named ``edit_timestamp``, which will
	   be set to the current time whenever the ``edited`` method is called.
	   The ``onupdate`` property will unfortunately not work here, since some
	   columns aren't changed explicitly by users, and updates on those columns
	   shouldn't be counted as "real".
	#. A nullable ``edit_count`` column, which signals how many times the
	   mixed-in object has been edited, and increments by 1 every time the
	   ``edited`` method is called. The default value is ``0``. This is primarily
	   for detecting database collisions, but is also useful for other things.
	   When a row is first inserted, this column will remain NULL unless
	   specified otherwise.
	"""

	edit_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		nullable=True
	)
	edit_count = sqlalchemy.Column(
		sqlalchemy.Integer,
		default=0,
		nullable=False
	)

	def edited(self: EditInfoMixin) -> None:
		"""Sets the ``edit_timestamp`` attribute to the current date and time.
		Increments the ``edit_count`` value by 1, as long as it's under 2147483647,
		the maximum 4-byte integer value.
		"""

		self.edit_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

		if self.edit_count < 2147483647:
			self.edit_count += 1


@sqlalchemy.orm.declarative_mixin
class IdMixin:
	"""A helper mixin that adds a UUID column named ``id``, whose default value is
	an automatically generated UUID4. On the off chance that the generated
	UUID collides with another one in the same column, it will try again.
	"""

	id = sqlalchemy.Column(
		UUID,
		primary_key=True,
		default=generate_uuid
	)


class PermissionControlMixin:
	"""A helper mixin to handle permissions for users performing different
	actions on the mixed-in class, as well as viewing different columns.
	"""

	class_actions = {}

	instance_actions = {}

	# If this class should not be viewed, this won't be used anyway.
	# Using an empty set as an alias for "all columns" should be fine.
	viewable_columns = {}

	@classmethod
	def get_allowed_class_actions(
		cls: PermissionControlMixin,
		user
	) -> typing.List[str]:
		"""Returns all actions that ``user`` is allowed to perform as per this
		class's ``class_actions``.
		"""

		return [
			action_name
			for action_name, action_func in cls.class_actions.items()
			if action_func(cls, user)
		]

	def get_allowed_instance_actions(
		self: PermissionControlMixin,
		user
	) -> typing.List[str]:
		"""Returns all actions that ``user`` is allowed to perform as per this
		instance's ``instance_actions``.
		"""

		return [
			action_name
			for action_name, action_func in self.instance_actions.items()
			if action_func(self, user)
		]

	def get_allowed_columns(
		self: PermissionControlMixin,
		user
	) -> typing.List[str]:
		"""Returns all columns in this instance that ``user`` is allowed to view
		as per ``viewable_columns``. If the variable is an empty set, all columns
		are returned.
		"""

		if self.viewable_columns == {}:
			return [
				column.key
				for column in sqlalchemy.inspect(self).mapper.column_attrs
			]

		return [
			column_name
			for column_name, column_func in self.viewable_columns.items()
			if column_func(self, user)
		]

	@classmethod
	def get_class_permission(
		cls: PermissionControlMixin,
		user,
		action: str
	) -> bool:
		"""Returns whether or not ``user`` is allowed to perform ``action``,
		as per this class's ``class_actions``. If ``action`` isn't present
		there, ``True`` is automatically returned.
		"""

		if action not in cls.class_actions:
			return True

		return cls.class_actions[action](cls, user)

	def get_instance_permission(
		self: PermissionControlMixin,
		user,
		action: str
	) -> bool:
		"""Returns whether or not ``user`` is allowed to perform ``action``,
		as per this instance's ``instance_actions``. If ``action`` isn't
		present there, ``True`` is automatically returned.
		"""

		if action not in self.instance_actions:
			return True

		return self.instance_actions[action](self, user)


class ReprMixin:
	"""A helper mixin which adds a default, pretty ``__repr__`` method."""

	def __repr__(self: ReprMixin) -> str:
		"""Returns the ``_repr`` method with all of the mixed-in model's primary
		keys.
		"""

		return self._repr(
			**{
				primary_key.key: getattr(self, primary_key.key)
				for primary_key in sqlalchemy.inspect(self).mapper.primary_key
			}
		)

	def _repr(
		self: ReprMixin,
		**fields: typing.Dict[str, typing.Any]
	) -> str:
		"""Automatically generates a pretty ``__repr__``, based on keyword
		arguments.
		"""

		field_strings = []
		at_least_one_attached_attribute = False

		for key, field in fields.items():
			try:
				field_strings.append(f"{key}={field!r}")
			except sqlalchemy.orm.exc.DetachedInstanceError:
				field_strings.append(f"{key}=DetachedInstanceError")
			else:
				at_least_one_attached_attribute = True

		if at_least_one_attached_attribute:
			return f"<{self.__class__.__name__}({','.join(field_strings)})>"

		return f"<{self.__class__.__name__} {id(self)}>"
