import typing

import cerberus.schema

__all__ = [
	"generate_list_schema",
	"generate_search_schema_registry"
]


def generate_list_schema(
	allowed_order_attributes: typing.Iterable[str],
	use_filter: bool = True,
	default_order_by: str = None,
	default_order_asc: bool = None,
	limit_max: int = 512,
	offset_max: int = 512
) -> dict:
	result = {
		"order": {
			"type": "dict",
			"schema": {
				"by": {
					"type": "string",
					"allowed": allowed_order_attributes,
					"required": True
				},
				"asc": {
					"type": "boolean",
					"required": True
				}
			},
			"required": True
		},
		"limit": {
			"type": "integer",
			"min": 1,
			"max": limit_max,
			"required": True
		},
		"offset": {
			"type": "integer",
			"min": 0,
			"max": offset_max,
			"default": 0,
			"required": False
		}
	}

	if (
		default_order_by is not None and
		default_order_asc is not None
	):
		result["order"].update({
			"default": {
				"by": default_order_by,
				"asc": default_order_asc
			},
			"required": False
		})
	elif default_order_by is not None:
		result["order"]["schema"]["by"].update({
			"default": default_order_by,
			"required": False
		})
	elif default_order_asc is not None:
		result["order"]["schema"]["asc"].update({
			"default": default_order_asc,
			"required": False
		})

	if use_filter:
		result["filter"] = {
			"type": "dict",
			"schema": "search",
			"minlength": 1,
			"maxlength": 1,
			"required": False
		}

	return result


def generate_search_schema_registry(
	rules: dict,
	schema_name: str = "search"
) -> cerberus.schema.SchemaRegistry:
	"""Generates a search schema registry with `$and`, `$or` and `$not` rules
	combined with the given ones.
	"""

	inner_schema = {
		"type": "list",
		"schema": {
			"type": "dict",
			"schema": schema_name,
			"minlength": 1,
			"maxlength": 1
		},
		"minlength": 2
	}

	return cerberus.schema.SchemaRegistry({
		schema_name: {
			**rules,
			"$and": inner_schema,
			"$or": inner_schema,
			"$not": inner_schema["schema"]
		}
	})
