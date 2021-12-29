__all__ = [
	"PERMISSION_KEY_SCHEMA",
	"BASE_PERMISSION_SCHEMA"
]

PERMISSION_KEY_SCHEMA = {
	"type": "boolean",
	"nullable": True,
	"required": True
}
BASE_PERMISSION_SCHEMA = {
	"forum_create": PERMISSION_KEY_SCHEMA,
	"forum_delete": PERMISSION_KEY_SCHEMA,
	"forum_edit": PERMISSION_KEY_SCHEMA,
	"forum_merge": PERMISSION_KEY_SCHEMA,
	"forum_move": PERMISSION_KEY_SCHEMA,
	"forum_view": PERMISSION_KEY_SCHEMA,
	"group_create": PERMISSION_KEY_SCHEMA,
	"group_delete": PERMISSION_KEY_SCHEMA,
	"group_edit": PERMISSION_KEY_SCHEMA,
	"group_edit_permissions": PERMISSION_KEY_SCHEMA,
	"post_create": PERMISSION_KEY_SCHEMA,
	"post_delete_own": PERMISSION_KEY_SCHEMA,
	"post_delete_any": PERMISSION_KEY_SCHEMA,
	"post_edit_own": PERMISSION_KEY_SCHEMA,
	"post_edit_any": PERMISSION_KEY_SCHEMA,
	"post_edit_vote": PERMISSION_KEY_SCHEMA,
	"post_move_own": PERMISSION_KEY_SCHEMA,
	"post_move_any": PERMISSION_KEY_SCHEMA,
	"post_view": PERMISSION_KEY_SCHEMA,
	"thread_create": PERMISSION_KEY_SCHEMA,
	"thread_delete_own": PERMISSION_KEY_SCHEMA,
	"thread_delete_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_own": PERMISSION_KEY_SCHEMA,
	"thread_edit_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_lock_own": PERMISSION_KEY_SCHEMA,
	"thread_edit_lock_any": PERMISSION_KEY_SCHEMA,
	"thread_edit_pin": PERMISSION_KEY_SCHEMA,
	"thread_edit_vote": PERMISSION_KEY_SCHEMA,
	"thread_merge_own": PERMISSION_KEY_SCHEMA,
	"thread_merge_any": PERMISSION_KEY_SCHEMA,
	"thread_move_own": PERMISSION_KEY_SCHEMA,
	"thread_move_any": PERMISSION_KEY_SCHEMA,
	"thread_view": PERMISSION_KEY_SCHEMA,
	"user_delete": PERMISSION_KEY_SCHEMA,
	"user_edit": PERMISSION_KEY_SCHEMA,
	"user_edit_ban": PERMISSION_KEY_SCHEMA,
	"user_edit_groups": PERMISSION_KEY_SCHEMA,
	"user_edit_permissions": PERMISSION_KEY_SCHEMA
}
