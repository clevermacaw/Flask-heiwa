"""Utilities for the API views."""

from .find_and_validate import (
	find_category_by_id,
	find_forum_by_id,
	find_group_by_id,
	find_thread_by_id,
	find_user_by_id,
	validate_category_exists,
	validate_forum_exists,
	validate_thread_exists,
	validate_user_exists
)
from .jwt import create_jwt
from .permissions import requires_permission, validate_permission
from .query import generate_parsed_forum_permissions_exist_query
from .schema import generate_search_schema, generate_search_schema_registry
from .search import parse_search
from .static import BASE_PERMISSION_SCHEMA, PERMISSION_KEY_SCHEMA

__all__ = [
	"BASE_PERMISSION_SCHEMA",
	"PERMISSION_KEY_SCHEMA",
	"create_jwt",
	"find_category_by_id",
	"find_forum_by_id",
	"find_group_by_id",
	"find_thread_by_id",
	"find_user_by_id",
	"generate_parsed_forum_permissions_exist_query",
	"generate_search_schema",
	"generate_search_schema_registry",
	"parse_search",
	"requires_permission",
	"validate_permission",
	"validate_category_exists",
	"validate_forum_exists",
	"validate_thread_exists",
	"validate_user_exists"
]
__version__ = "1.29.0"
