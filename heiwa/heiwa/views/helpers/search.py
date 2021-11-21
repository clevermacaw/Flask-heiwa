import typing

import sqlalchemy
import sqlalchemy.orm

import heiwa.models

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
		typing.Union[typing.Dict, typing.Any]
	],
	model: heiwa.models.Base
):
	"""Converts the given dictionary formatted conditions to SQLAlchemy ones."""

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
