# Database config
# Replace in production!
DATABASE_URI = "postgresql://heiwa:heiwa@localhost/heiwa"

# Forum config
FORUM_MAX_CHILD_LEVEL = 20

# Group config
# Cannot be changed after the first (administrator) user has been created!
# Do not leave any permissions as `None` for the `*` `default_for` group!
GROUPS_FIRST_USER = ("Administrator",)
GROUP_DEFAULTS = {
	"Default": {
		"default_for": ["*"],
		"level": 0,
		"description": "The group all users are assigned to by default.",
		"permissions": {
			"forum_create": False,
			"forum_delete_own": False,
			"forum_delete_any": False,
			"forum_edit_own": False,
			"forum_edit_any": False,
			"forum_merge_own": False,
			"forum_merge_any": False,
			"forum_move_own": False,
			"forum_move_any": False,
			"forum_view": True,
			"group_create": False,
			"group_delete": False,
			"group_edit": False,
			"group_edit_permissions": False,
			"post_create": False,
			"post_delete_own": False,
			"post_delete_any": False,
			"post_edit_own": False,
			"post_edit_any": False,
			"post_edit_vote": False,
			"post_move_own": False,
			"post_move_any": False,
			"post_view": True,
			"thread_create": False,
			"thread_delete_own": False,
			"thread_delete_any": False,
			"thread_edit_own": False,
			"thread_edit_any": False,
			"thread_edit_vote": False,
			"thread_edit_lock_own": False,
			"thread_edit_lock_any": False,
			"thread_edit_pin": False,
			"thread_merge_own": False,
			"thread_merge_any": False,
			"thread_move_own": False,
			"thread_move_any": False,
			"thread_view": True,
			"user_delete": False,
			"user_edit": False,
			"user_edit_ban": False,
			"user_edit_groups": False,
			"user_edit_permissions": False
		}
	},
	"User": {
		"default_for": ["openid"],
		"level": 1,
		"description": "The group all registered users are assigned to.",
		"permissions": {
			"forum_create": None,
			"forum_delete_own": None,
			"forum_delete_any": None,
			"forum_edit_own": None,
			"forum_edit_any": None,
			"forum_merge_own": None,
			"forum_merge_any": None,
			"forum_move_own": None,
			"forum_move_any": None,
			"forum_view": None,
			"group_create": None,
			"group_delete": None,
			"group_edit": None,
			"group_edit_permissions": None,
			"post_create": True,
			"post_delete_own": True,
			"post_delete_any": None,
			"post_edit_own": True,
			"post_edit_any": None,
			"post_edit_vote": True,
			"post_move_own": None,
			"post_move_any": None,
			"post_view": None,
			"thread_create": True,
			"thread_delete_own": True,
			"thread_delete_any": None,
			"thread_edit_own": True,
			"thread_edit_any": None,
			"thread_edit_vote": True,
			"thread_edit_lock_own": True,
			"thread_edit_lock_any": None,
			"thread_edit_pin": None,
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
	},
	"Administrator": {
		"default_for": [],
		"level": 999,
		"description": "Board administrators.",
		"permissions": {
			"forum_create": True,
			"forum_delete_own": True,
			"forum_delete_any": True,
			"forum_edit_own": True,
			"forum_edit_any": True,
			"forum_merge_own": True,
			"forum_merge_any": True,
			"forum_move_own": True,
			"forum_move_any": True,
			"forum_view": True,
			"group_create": True,
			"group_delete": True,
			"group_edit": True,
			"group_edit_permissions": True,
			"post_create": True,
			"post_delete_own": True,
			"post_delete_any": True,
			"post_edit_own": True,
			"post_edit_any": True,
			"post_edit_vote": True,
			"post_move_own": True,
			"post_move_any": True,
			"post_view": True,
			"thread_create": True,
			"thread_delete_own": True,
			"thread_delete_any": True,
			"thread_edit_own": True,
			"thread_edit_any": True,
			"thread_edit_vote": True,
			"thread_edit_lock_own": True,
			"thread_edit_lock_any": True,
			"thread_edit_pin": True,
			"thread_merge_own": True,
			"thread_merge_any": True,
			"thread_move_own": True,
			"thread_move_any": True,
			"thread_view": True,
			"user_delete": True,
			"user_edit": True,
			"user_edit_ban": True,
			"user_edit_groups": True,
			"user_edit_permissions": True
		}
	}
}

# Guest config
GUEST_MAX_SESSIONS_PER_IP = 2
GUEST_SESSION_EXPIRES_AFTER = 604800

# Flask config
JSON_SORT_KEYS = False

# JWT config
JWT_EXPIRES_AFTER = 31557600

# Meta config
META_NAME = "Heiwa"

# OpenID config
OPENID_AUTHENTICATION_EXPIRES_AFTER = 30
OPENID_SERVICES = {
	"keycloak": {
		"client_id": "heiwa",
		"authorization_endpoint": "http://localhost:8080/auth/realms/master/"
		"protocol/openid-connect/auth",
		"token_endpoint": "http://localhost:8080/auth/realms/master/protocol/"
		"openid-connect/token",
		"userinfo_endpoint": "http://localhost:8080/auth/realms/master/protocol/"
		"openid-connect/userinfo",
		"jwks_uri": "http://localhost:8080/auth/realms/master/protocol/"
		"openid-connect/certs",
		"scope": "openid"
	}
}

# Which config values to expose through the API
PUBLIC_CONFIG_KEYS = (
	"FORUM_MAX_CHILD_LEVEL",
	"GUEST_SESSION_EXPIRES_AFTER",
	"JWT_EXPIRES_AFTER",
	"RATELIMIT_DEFAULT",
	"RATELIMIT_SPECIFIC",
	"USER_MAX_AVATAR_SIZE",
	"USER_AVATAR_TYPES"
)

# Rate limit config
RATELIMIT_DEFAULT = ("200/10second",)
RATELIMIT_SPECIFIC = {
	"openid.login": ("5/6hour",),
	"openid.authorize": ("5/6hour",)
}

# Flask config
SECRET_KEY = "incredibly_secretive_secret"   # Replace in production!

# User config
USER_MAX_AVATAR_SIZE = 5242880  # 5 Mebibytes
USER_AVATAR_TYPES = {
	"image/png": "png",
	"image/jpeg": "jpeg"
}
