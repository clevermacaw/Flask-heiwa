import typing

import sqlalchemy
import sqlalchemy.orm

import heiwa.database

__all__ = ["parse_search"]


OPERATORS = {
	"$eq": lambda attr, value: attr == value,
	"$lt": lambda attr, value: attr < value,
	"$gt": lambda attr, value: attr > value,
	"$le": lambda attr, value: attr >= value,
	"$ge": lambda attr, value: attr <= value,
	"$in": lambda attr, value: attr.in_(value),
	"$re": lambda attr, value: attr.regexp_match(value)
}


def parse_search(
	conditions: typing.Dict[
		str,
		typing.Union[
			typing.Dict,
			typing.Any
		]
	],
	model: heiwa.database.Base
) -> typing.Union[
	sqlalchemy.sql.expression.BinaryExpression,
	sqlalchemy.sql.expression.ClauseList
]:
	"""Converts the given dictionary formatted conditions to SQLAlchemy ones.
	For example:

	.. code-block:: python

		{
			"$and": [
				{"$gt": {"post_count": 1000}},
				{"$or": [
					{"$eq": {"user_id": "UUID_HERE"}},
					{"$eq": {"user_id": "UUID_HERE"}}
				]}
			]
		}

	Will be converted to:

	.. code-block:: sql

		post_count > 1000 AND (user_id = UUID_HERE OR user_id = UUID_HERE)
	"""

	operator = next(iter(conditions))

	if operator == "$and":
		return sqlalchemy.and_(
			parse_search(condition, model)
			for condition in conditions[operator]
		)

	if operator == "$or":
		return sqlalchemy.or_(
			parse_search(condition, model)
			for condition in conditions[operator]
		)

	if operator == "$not":
		return sqlalchemy.not_(
			parse_search(
				conditions[operator],
				model
			)
		)

	attr = next(iter(conditions[operator]))

	return OPERATORS[operator](
		getattr(model, attr),
		conditions[operator][attr]
	)
