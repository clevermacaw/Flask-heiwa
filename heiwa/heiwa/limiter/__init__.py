import flask
import flask_limiter

__all__ = ["limiter"]
__version__ = "1.0.0"


limiter = flask_limiter.Limiter(
	key_func=lambda: flask.g.identifier
)
