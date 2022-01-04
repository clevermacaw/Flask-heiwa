from __future__ import annotations

import abc
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
	by default, as well as methods to use them.
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
	"""The default values of all permissions. In this case, :data:`None`."""

	def to_permissions(self: BasePermissionMixin) -> typing.Dict[
		str,
		typing.Union[
			None,
			bool
		]
	]:
		"""Transforms the values in this instance to the standard format for
		permissions - a dictionary, where string keys represent permissions,
		and their boolean value represents whether or not they're granted.
		"""

		return {
			permission_name: getattr(self, permission_name)
			for permission_name in self.DEFAULT_PERMISSIONS
		}


@sqlalchemy.orm.declarative_mixin
class CDWMixin:
	"""A mixin used to simplify the creation and deletion of objects."""

	@classmethod
	def create(
		cls: CDWMixin,
		session: sqlalchemy.orm.Session,
		*args,
		**kwargs
	) -> CDWMixin:
		"""Creates an instance of the mixed-in class with the provided arguments,
		and calls the :meth:`write <.CDWMixin.write>` method.
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
		"""Deletes the current instance of the mixed-in class from the given
		``session``. If the argument is :data:`None`, it's set to the instance's
		session.
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
	"""A helper mixin used to store the time an object was created."""

	creation_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		default=datetime.datetime.now,
		nullable=False
	)
	"""The time an object was created."""


@sqlalchemy.orm.declarative_mixin
class EditInfoMixin:
	"""A helper mixin which contains information about the mixed-in object's
	edits.
	"""

	edit_timestamp = sqlalchemy.Column(
		sqlalchemy.DateTime(timezone=True),
		nullable=True
	)
	"""The last time an object was edited. If :data:`None`, that has never
	happened so far.

	.. note::
		Originally, this used the ``onupdate`` property and changed each time
		an object was updated no matter the attribute, but since internal
		changes not requested by users will happen fairly often, we have to
		make an explicit :meth:`edited <.EditInfoMixin.edited>` method.
	"""

	edit_count = sqlalchemy.Column(
		sqlalchemy.Integer,
		default=0,
		nullable=False
	)
	"""The amount of times an object was edited. Increments by ``1`` each time
	:meth:`edited <.EditInfoMixin.edited>` is called, and defaults to ``0``.
	"""

	def edited(self: EditInfoMixin) -> None:
		"""Sets the :attr:`edit_timestamp <.EditInfoMixin.edit_timestamp>`
		attribute to the current date and time. Also increments the
		:attr:`edit_count <.EditInfoMixin.edit_timestamp>` attribute by ``1``,
		provided that it's under ``2147483647``, the maximum 4-byte integer value.
		"""

		self.edit_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

		if self.edit_count < 2147483647:
			self.edit_count += 1


@sqlalchemy.orm.declarative_mixin
class IdMixin:
	"""A helper mixin used to uniquely identify objects."""

	id = sqlalchemy.Column(
		UUID,
		primary_key=True,
		default=generate_uuid
	)
	"""The ID of an object, in the form of a UUID4. Uses the :func:`.generate_uuid`
	function to ensure there are no duplicates within the table, even if the
	chances of a collision occuring are extremely slim.
	"""


class PermissionControlMixin:
	"""A helper mixin used to handle permissions."""

	static_actions = {}
	"""The actions a user is / isn't allowed to perform on any instance of the
	mixed-in object.

	.. seealso::
		:meth:`.PermissionControlMixin.get_allowed_static_actions`
	"""

	instance_actions = {}
	"""The actions a user is / isn't allowed to perform on one given instance of
	the mixed-in object. Unlike
	:attr:`static_actions <.PermissionControlMixin.static_actions>`, this can and
	should vary with each instance.

	.. seealso::
		:meth:`.PermissionControlMixin.get_allowed_instance_actions`
	"""

	action_queries = {}
	"""Permissions for actions specified for the mixed-in object, but formatted
	in such a way that they are evaluable within SQL queries. Since a user can
	change the result, these should be callables with a single ``user`` argument.

	.. seealso::
		:meth:`.PermissionControlMixin.get`
	"""

	# If this class should not be viewed, this mixin won't be used anyway.
	viewable_columns = {}
	"""The columns in the mixed-in object a given user is allowed to view. By
	default, this value is an empty dictionary, meaning they're allowed to view
	all columns.

	.. seealso::
		:meth:`.PermissionControlMixin.get_allowed_columns`
	"""

	@classmethod
	def get_allowed_static_actions(
		cls: PermissionControlMixin,
		user
	) -> typing.List[str]:
		"""Returns all actions that ``user`` is allowed to perform as per the
		mixed-in class's
		:attr:`static_actions <.PermissionControlMixin.static_actions>`.
		"""

		return [
			action_name
			for action_name, action_func in cls.static_actions.items()
			if action_func(cls, user)
		]

	def get_allowed_instance_actions(
		self: PermissionControlMixin,
		user
	) -> typing.List[str]:
		"""Returns all actions that ``user`` is allowed to perform as per the
		current instance of the mixed-in class's
		:attr:`static_actions <.PermissionControlMixin.instance_actions>`.
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
		"""Finds all columns in the current instance of the mixed-in class that
		``user`` is allowed to view, as per the
		:attr:`viewable_columns <.PermissionControlMixin.viewable_columns>`.
		If the value is an empty dictionary, all columns in this object are
		returned.

		:param user: The user whose permissions should be evaluated.

		:returns: The list of allowed actions.
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

	@staticmethod
	@abc.abstractmethod
	def get(
		user,
		session: sqlalchemy.orm.Session,
		additional_actions: typing.Union[
			None,
			typing.Iterable[str]
		] = None,
		conditions: typing.Union[
			bool,
			sqlalchemy.sql.expression.BinaryExpression,
			sqlalchemy.sql.expression.ClauseList
		] = True,
		order_by: typing.Union[
			None,
			sqlalchemy.sql.elements.UnaryExpression
		] = None,
		limit: typing.Union[
			None,
			int
		] = None,
		offset: typing.Union[
			None,
			int
		] = None,
		ids_only: bool = False
	):
		"""Generates a selection query with permissions already handled. This
		may execute additional queries with some models.

		:param user: The user whose permissions should be evaluated.
		:param session: The SQLAlchemy session to execute additional queries with.
		:param additional_actions: Additional actions that a user must be able to
			perform on instances of the mixed-in class, other than the default
			``view`` action.
		:param conditions: Any additional conditions. :data:`True` by default,
			meaning there are no conditions.
		:param order_by: An expression to order by.
		:param limit: A limit.
		:param offset: An offset.
		:param ids_only: Whether or not to only return a query for IDs.

		:returns: The query.
		"""

		raise NotImplementedError


class ReprMixin:
	"""A helper mixin used to help with the stringication of objects."""

	def __repr__(self: ReprMixin) -> str:
		"""Returns the :meth:`_repr <.ReprMixin._repr>` method with all of the
		mixed-in model's primary keys.
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

		.. note::
			Brilliant function borrowed from Stephen Fuhry, at:
			`https://stackoverflow.com/a/55749579`_.
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
