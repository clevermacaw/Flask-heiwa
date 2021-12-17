import flask

from .. import encoders

from .helpers import generate_list_schema, generate_search_schema_registry

__all__ = ["message_blueprint"]

message_blueprint = flask.Blueprint(
	"messages",
	__name__,
	url_prefix="/messages"
)
message_blueprint.json_encoder = encoders.JSONEncoder

ATTR_SCHEMAS = {
	"id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"creation_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"edit_timestamp": {
		"type": "datetime",
		"coerce": "convert_to_datetime"
	},
	"edit_count": {
		"type": "integer",
		"min": 0,
		"max": 2147483647
	},
	"receiver_id": {
		"type": "uuid",
		"coerce": "convert_to_uuid"
	},
	"is_read": {
		"type": "boolean"
	},
	"encrypted_session_key": {
		"type": "binary",
		"coerce": "decode_base64",
		"minlength": 128,  # encrypted with 1024-bit RSA
		"maxlength": 512   # encrypted with 4096-bit RSA
	},
	"tag": {
		"type": "string",
		"minlength": 1,  # Both values are completely arbitrary.
		"maxlength": 64
	},
	"encrypted_content": {
		"type": "binary",
		"coerce": "decode_base64",
		"minlength": 16,  # Min. AES-CBC length
		"maxlength": 65552  # ~65536 character message, padding
	}
}

CREATE_EDIT_SCHEMA = {
	"receiver_id": {
		**ATTR_SCHEMAS["receiver_id"],
		"required": True
	},
	"encrypted_session_key": {
		**ATTR_SCHEMAS["encrypted_session_key"],
		"required": True
	},
	"tag": {
		**ATTR_SCHEMAS["tag"],
		"nullable": True,
		"required": True
	},
	"encrypted_content": {
		**ATTR_SCHEMAS["encrypted_content"],
		"required": True
	}
}
LIST_SCHEMA = generate_list_schema(
	(
		"creation_timestamp",
		"edit_timestamp",
		"edit_count"
	),
	default_order_by="creation_timestamp",
	default_order_asc=False
)

LT_GT_SEARCH_SCHEMA = {
	"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
	"edit_timestamp": ATTR_SCHEMAS["edit_timestamp"],
	"edit_count": ATTR_SCHEMAS["edit_count"]
}
SEARCH_SCHEMA_REGISTRY = generate_search_schema_registry({
	"$eq": {
		"type": "dict",
		"schema": {
			"id": ATTR_SCHEMAS["id"],
			"creation_timestamp": ATTR_SCHEMAS["creation_timestamp"],
			"edit_timestamp": {
				**ATTR_SCHEMAS["edit_timestamp"],
				"nullable": True
			},
			"edit_count": ATTR_SCHEMAS["edit_count"],
			"receiver_id": ATTR_SCHEMAS["receiver_id"],
			"is_read": ATTR_SCHEMAS["is_read"],
			"encrypted_session_key": ATTR_SCHEMAS["encrypted_session_key"],
			"tag": {
				**ATTR_SCHEMAS["tag"],
				"nullable": True
			},
			"encrypted_content": ATTR_SCHEMAS["encrypted_content"]
		},
		"maxlength": 1
	},
	"$lt": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$gt": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$le": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$ge": {
		"type": "dict",
		"schema": LT_GT_SEARCH_SCHEMA,
		"maxlength": 1
	},
	"$in": {
		"type": "dict",
		"schema": {
			"id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["id"],
				"minlength": 1,
				"maxlength": 32
			},
			"creation_timestamp": {
				"type": "list",
				"schema": ATTR_SCHEMAS["creation_timestamp"],
				"minlength": 1,
				"maxlength": 32
			},
			"edit_timestamp": {
				"type": "list",
				"schema": {
					**ATTR_SCHEMAS["edit_timestamp"],
					"nullable": True
				},
				"minlength": 1,
				"maxlength": 32
			},
			"edit_count": {
				"type": "list",
				"schema": ATTR_SCHEMAS["edit_count"],
				"minlength": 1,
				"maxlength": 32
			},
			"receiver_id": {
				"type": "list",
				"schema": ATTR_SCHEMAS["receiver_id"],
				"minlength": 1,
				"maxlength": 32
			},
			"encrypted_session_key": {
				"type": "list",
				"schema": ATTR_SCHEMAS["encrypted_session_key"],
				"minlength": 1,
				"maxlength": 32
			},
			"tag": {
				"type": "list",
				"schema": ATTR_SCHEMAS["tag"],
				"minlength": 1,
				"maxlength": 32
			},
			"encrypted_content": {
				"type": "list",
				"schema": ATTR_SCHEMAS["encrypted_content"],
				"minlength": 1,
				"maxlength": 32
			}
		},
		"maxlength": 1
	}
})
