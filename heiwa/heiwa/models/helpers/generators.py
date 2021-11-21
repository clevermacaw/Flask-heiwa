import uuid

import sqlalchemy
import sqlalchemy.engine

__all__ = ["generate_uuid"]


def generate_uuid(ctx: sqlalchemy.engine.ExecutionContext) -> str:
	"""Keeps generating an UUID4,
	until it is not present in the current column.
	"""

	first_iteration = True

	while first_iteration or (
		ctx.connection.execute(
			sqlalchemy.select(ctx.current_column).
			where(ctx.current_column == uuid4)
		).one_or_none()
	) is not None:
		first_iteration = False

		uuid4 = uuid.uuid4()

	return uuid4
