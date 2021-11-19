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
	conditions: dict,
	model: heiwa.models.Base,
	attr_fixers: dict = {}
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

	if attr not in attr_fixers:
		parsed_attr = getattr(model, attr)
	else:
		parsed_attr = attr_fixers[attr]()

	return OPERATORS[operator](parsed_attr, conditions[operator][attr])
