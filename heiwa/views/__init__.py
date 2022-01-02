"""Blueprints and utilities for different parts of the API."""

from . import utils
from .category import category_blueprint
from .forum import forum_blueprint
from .group import group_blueprint
from .guest import guest_blueprint
from .message import message_blueprint
from .meta import meta_blueprint
from .notification import notification_blueprint
from .openid import openid_blueprint
from .post import post_blueprint
from .thread import thread_blueprint
from .user import user_blueprint

__all__ = [
	"category_blueprint",
	"forum_blueprint",
	"group_blueprint",
	"guest_blueprint",
	"message_blueprint",
	"meta_blueprint",
	"notification_blueprint",
	"openid_blueprint",
	"post_blueprint",
	"thread_blueprint",
	"user_blueprint",
	"utils"
]
__version__ = "0.58.5"
