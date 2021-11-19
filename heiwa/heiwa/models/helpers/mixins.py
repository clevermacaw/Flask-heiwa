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
	"ReprMixin",
	"ToNotificationMixin"
]


@sqlalchemy.orm.declarative_mixin
class BasePermissionMixin:
	"""Adds columns with all possible permissions,
	as well as the `to_permissions` method to convert them to a dict.
	"""

	forum_create = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_delete_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_edit_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_merge_any = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move_own = sqlalchemy.Column(
		sqlalchemy.Boolean,
		nullable=True
	)
	forum_move_any = sqlalchemy.Column(
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

	def to_permissions(self) -> dict:
		return {
			"forum_create": self.forum_create,
			"forum_delete_own": self.forum_delete_own,
			"forum_delete_any": self.forum_delete_any,
			"forum_edit_own": self.forum_edit_own,
			"forum_edit_any": self.forum_edit_any,
			"forum_merge_own": self.forum_merge_own,
			"forum_merge_any": self.forum_merge_any,
			"forum_move_own": self.forum_move_own,
			"forum_move_any": self.forum_move_any,
			"forum_view": self.forum_view,
			"group_create": self.group_create,
			"group_delete": self.group_delete,
			"group_edit": self.group_edit,
			"group_edit_permissions": self.group_edit_permissions,
			"post_create": self.post_create,
			"post_delete_own": self.post_delete_own,
			"post_delete_any": self.post_delete_any,
			"post_edit_own": self.post_edit_own,
			"post_edit_any": self.post_edit_any,
			"post_edit_vote": self.post_edit_vote,
			"post_move_own": self.post_move_own,
			"post_move_any": self.post_move_any,
			"post_view": self.post_view,
			"thread_create": self.thread_create,
			"thread_delete_own": self.thread_delete_own,
			"thread_delete_any": self.thread_delete_any,
			"thread_edit_own": self.thread_edit_own,
			"thread_edit_any": self.thread_edit_any,
			"thread_edit_lock_own": self.thread_edit_lock_own,
			"thread_edit_lock_any": self.thread_edit_lock_any,
			"thread_edit_pin": self.thread_edit_pin,
			"thread_edit_vote": self.thread_edit_vote,
			"thread_merge_own": self.thread_merge_own,
			"thread_merge_any": self.thread_merge_any,
			"thread_move_own": self.thread_move_own,
			"thread_move_any": self.thread_move_any,
			"thread_view": self.thread_view,
			"user_delete": self.user_delete,
			"user_edit": self.user_edit,
			"user_edit_ban": self.user_edit_ban,
			"user_edit_groups": self.user_edit_groups,
			"user_edit_permissions": self.user_edit_permissions
		}


@sqlalchemy.orm.declarative_mixin
class CDWMixin:
	"""A mixin that adds the create(), delete() and write() methods."""

	@classmethod
	def create(
		cls,
		session: sqlalchemy.orm.Session,
		*args,
		**kwargs
	):
		"""Creates an instance of the mixed-in class and runs
		the `write()` method.
		"""

		self = cls(
			*args,
			**kwargs
		)

		self.write(session)

		return self

	def delete(self: CDWMixin) -> None:
		"""Deletes the current instance of the mixed-in class."""

		sqlalchemy.orm.object_session(self).delete(self)

	def write(
		self: CDWMixin,
		session: sqlalchemy.orm.Session
	) -> None:
		"""Adds the current instance to the provided session."""

		session.add(self)


@sqlalchemy.orm.declarative_mixin
class CreationTimestampMixin:
	"""A mixin that adds a timezone-aware timestamp column named
	`creation_timestamp`, whose default value is the time of row insertion.
	"""

	creation_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		default=datetime.datetime.now,
		nullable=False
	)


@sqlalchemy.orm.declarative_mixin
class EditInfoMixin:
	"""Adds a timezone-aware timestamp column named `edit_timestamp`,
	which will be set to the current time whenever `edited()` is called.
	The `onupdate` property will unfortunately not work here, since counters
	such as `thread_count` being updated will also have an effect.

	Adds an `Integer` column named `edit_count`, which signals how many
	times this thread has been edited, and increments by 1 every time `edited()`
	is called. The default value is `0`. This is primarily for detecting
	database collisions, but is also useful for other things.

	When a row is first inserted, this column will remain NULL
	unless specified otherwise.
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
		"""Sets the `edit_timestamp` attribute to the current date and time.
		Increments the `edit_count` value by 1.
		"""

		self.edit_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
		self.edit_count += 1


@sqlalchemy.orm.declarative_mixin
class IdMixin:
	"""A mixin that adds a UUID column named `id`, whose default value is
	an automatically generated UUID4. On the off chance that the generated
	UUID collides with another one in the same column, it will try again.
	"""

	id = sqlalchemy.Column(
		UUID,
		primary_key=True,
		default=generate_uuid
	)


class PermissionControlMixin:
	"""A mixin to handle permissions for users performing different actions
	with the given model, as well as viewing different attributes.
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
		"""Returns all actions that `user` is allowed to perform as per this
		class's `class_actions`.
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
		"""Returns all actions that `user` is allowed to perform as per this
		instance's `instance_actions`.
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
		"""Returns all columns in this instance that `user` is allowed to view
		as per `viewable_columns`. If the variable is an empty `set`,
		all columns are returned.
		"""

		if self.viewable_columns == {}:
			return [
				column.key
				for column in sqlalchemy.inspect(self).mapper.column_attrs
			]
		else:
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
		"""Returns whether or not `user` is allowed to perform `action`,
		as per this class's `class_actions`. If `action` isn't present
		there, `True` is automatically returned.
		"""

		if action not in cls.class_actions:
			return True

		return cls.class_actions[action](cls, user)

	def get_instance_permission(
		self: PermissionControlMixin,
		user,
		action: str
	) -> bool:
		"""Returns whether or not `user` is allowed to perform `action`,
		as per this instance's `instance_actions`. If `action` isn't
		present there, `True` is automatically returned.
		"""

		if action not in self.instance_actions:
			return True

		return self.instance_actions[action](self, user)


class ReprMixin:
	"""A mixin which adds a default, pretty `__repr__` method."""

	def __repr__(self: ReprMixin) -> str:
		"""Returns the `self._repr` method with a mapped `id` column,
		assuming it exists.
		"""

		return self._repr(id=self.id)

	def _repr(
		self: ReprMixin,
		**fields: typing.Dict[str, typing.Any]
	) -> str:
		"""Automatically generates a pretty `__repr__`,
		based on keyword arguments.
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


class ToNotificationMixin:
	def to_notification(self: ToNotificationMixin) -> dict:
		"""Transforms this object into a JSON-compatible format for notifications.
		Since the ID should never change, this value can later be used to find
		notifications corresponding to this thread.
		"""

		return {
			"id": str(self.id)
		}
