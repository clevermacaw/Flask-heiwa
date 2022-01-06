"""SQLAlchemy ORM models, tables and utilities."""

import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()

from . import utils
from .category import Category
from .forum import (
	Forum,
	ForumParsedPermissions,
	ForumPermissionsGroup,
	ForumPermissionsUser,
	forum_subscribers
)
from .group import Group, GroupPermissions
from .message import Message
from .notification import Notification
from .openid import OpenIDAuthentication
from .post import Post, PostVote
from .thread import Thread, ThreadVote, thread_subscribers
from .user import (
	User,
	UserBan,
	UserPermissions,
	user_blocks,
	user_follows,
	user_groups
)

__all__ = [
	"Base",
	"Category",
	"Forum",
	"ForumParsedPermissions",
	"ForumPermissionsGroup",
	"ForumPermissionsUser",
	"Group",
	"GroupPermissions",
	"Message",
	"Notification",
	"OpenIDAuthentication",
	"Post",
	"PostVote",
	"Thread",
	"ThreadVote",
	"User",
	"UserBan",
	"UserPermissions",
	"forum_subscribers",
	"thread_subscribers",
	"user_blocks",
	"user_follows",
	"user_groups",
	"utils"
]
__version__ = "0.35.14"
