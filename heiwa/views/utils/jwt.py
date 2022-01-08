import datetime
import uuid

import authlib.jose
import flask

__all__ = ["generate_jwt"]


def generate_jwt(
	user_id: uuid.UUID,
	name: str = None,
	expires_after: int = None
) -> str:
	"""Creates a JWT for the user with the given ``user_id``."""

	current_timestamp = round(
		datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
	)

	return authlib.jose.jwt.encode(
		{
			"alg": "HS256"
		},
		{
			"iss": (
				flask.current_app.config["META_NAME"]
				if name is None
				else name
			),
			"iat": current_timestamp,
			"exp": (
				current_timestamp
				+ (
					flask.current_app.config["JWT_EXPIRES_AFTER"]
					if expires_after is None
					else expires_after
				)
			),
			"sub": str(user_id)
		},
		flask.current_app.config["SECRET_KEY"]
	).decode("utf-8")
