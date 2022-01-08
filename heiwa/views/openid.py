import datetime
import io
import typing

import authlib.common.security
import authlib.integrations.requests_client
import authlib.jose
import authlib.oidc.core
import flask
import PIL
import requests
import sqlalchemy

from .. import database, encoders, exceptions, statuses, validators
from .utils import generate_jwt, generate_scrypt_hash

__all__ = ["openid_blueprint"]

openid_blueprint = flask.Blueprint(
	"openid",
	__name__,
	url_prefix="/openid"
)
openid_blueprint.json_encoder = encoders.JSONEncoder

REGISTERED_BY = "openid"


def get_config(client_name: str) -> typing.Dict[
		str,
		typing.Dict[
			str,
			str
		]
	]:
	"""Returns the current app's config for the OpenID service with the given
	``client_name``. If the ``'scope'`` parameter is missing or lacks
	``'openid'``, it's added at the start.
	"""

	config = flask.current_app.config["OPENID_SERVICES"][client_name].copy()

	if "scope" not in config:
		config["scope"] = "openid"
	elif "openid" not in config["scope"]:
		config["scope"] = f"openid {config['scope']}"

	return config


@openid_blueprint.route("", methods=["GET"])
def list_() -> typing.Tuple[flask.Response, int]:
	"""Returns all OpenID services registered in the config."""

	return flask.jsonify(
		list(flask.current_app.config["OPENID_SERVICES"])
	), statuses.OK


@openid_blueprint.route("/<string:client_name>/authorize", methods=["POST"])
@validators.validate_json({
	"code": {
		"type": "string",
		"required": True
	},
	"state": {
		"type": "string",
		"required": True
	},
	"redirect_uri": {
		"type": "string",
		"minlength": 8,
		"maxlength": 2048,
		"check_with": "is_public_url",
		"required": True
	}
})
def authorize(client_name: str) -> typing.Tuple[flask.Response, int]:
	"""Gets the ``client_name`` OpenID service's ``userinfo`` by logging in through
	an OAuth session, and creates a token for the associated user. The ``'sub'``
	key has to be defined, ``'preferred_username'`` and ``'picture'`` are optional
	but highly recommended. If there is no user associated, the user is
	automatically created. The ``registered_by`` column will be  ``'openid'``.
	"""

	if client_name not in flask.current_app.config["OPENID_SERVICES"]:
		raise exceptions.APIOpenIDServiceNotFound

	# Delete all expired entries
	flask.g.sa_session.execute(
		sqlalchemy.delete(database.OpenIDAuthentication).
		where(
			database.OpenIDAuthentication.creation_timestamp
			> (
				datetime.datetime.now(tz=datetime.timezone.utc)
				+ datetime.timedelta(seconds=flask.current_app.config[
					"OPENID_AUTHENTICATION_EXPIRES_AFTER"
				])
			)
		)
	)

	authentication = flask.g.sa_session.execute(
		sqlalchemy.select(database.OpenIDAuthentication).
		where(
			sqlalchemy.and_(
				database.OpenIDAuthentication.identifier == generate_scrypt_hash(
					flask.g.identifier.encode("utf-8")
				),
				database.OpenIDAuthentication.state == flask.g.json["state"]
			)
		)
	).scalars().one_or_none()

	if authentication is None:
		raise exceptions.APIOpenIDStateInvalid

	with authlib.integrations.requests_client.OAuth2Session(
		**get_config(client_name)
	) as oa2_session:
		try:
			token = oa2_session.fetch_token(
				oa2_session.metadata["token_endpoint"],
				**flask.g.json
			)
		except authlib.integrations.requests_client.OAuthError as exc:
			raise exceptions.APIOpenIDAuthenticationFailed(exc.error)

		jwks = oa2_session.get(oa2_session.metadata["jwks_uri"]).json()

		claims = authlib.jose.jwt.decode(
			token["id_token"],
			jwks,
			claims_cls=authlib.oidc.core.CodeIDToken
		)
		claims.validate()

		if claims["nonce"] != authentication.nonce:
			raise exceptions.APIOpenIDNonceInvalid

		authentication.delete()

		userinfo = oa2_session.get(oa2_session.metadata["userinfo_endpoint"]).json()

		user = flask.g.sa_session.execute(
			sqlalchemy.select(database.User).
			where(
				sqlalchemy.and_(
					database.User.registered_by == REGISTERED_BY,
					database.User.external_id == userinfo["sub"]
				)
			)
		).scalars().one_or_none()

		avatar_url = userinfo.get("picture")

		avatar = None
		avatar_type = None

		if avatar_url is not None:
			try:
				avatar = requests.get(avatar_url).content

				image = PIL.Image.open(io.BytesIO(avatar))
				image.verify()
			except OSError:
				avatar = None
			else:
				avatar_type = PIL.Image.MIME[image.format]

		if user is None:
			user = database.User.create(
				flask.g.sa_session,
				registered_by=REGISTERED_BY,
				external_id=userinfo["sub"],
				avatar_type=avatar_type,
				name=userinfo.get("preferred_username"),
			)

			# Be absolutely sure ``avatar_type`` is already set.
			# Is this necessary?
			user.avatar = avatar

			status = statuses.CREATED
		else:
			status = statuses.OK

		flask.g.sa_session.commit()

		oa2_session.revoke_token(
			oa2_session.metadata["token_endpoint"],
			token=token["access_token"]
		)

		return flask.jsonify({
			"token": generate_jwt(user.id)
		}), status


@openid_blueprint.route("/<string:client_name>/login", methods=["GET"])
@validators.validate_json({
	"redirect_uri": {
		"type": "string",
		"minlength": 8,
		"maxlength": 2048,
		"check_with": "is_public_url",
		"required": True
	}
})
def login(client_name: str) -> typing.Tuple[flask.Response, int]:
	"""Creates a URI for a user to log in through. The login attempt is recorded
	using ``database.OpenIDAuthentication``, to secure against replay and other
	similar attacks.
	"""

	if client_name not in flask.current_app.config["OPENID_SERVICES"]:
		raise exceptions.APIOpenIDServiceNotFound

	with authlib.integrations.requests_client.OAuth2Session(
		**get_config(client_name)
	) as oa2_session:
		nonce = authlib.common.security.generate_token()

		uri, state = oa2_session.create_authorization_url(
			oa2_session.metadata["authorization_endpoint"],
			redirect_uri=flask.g.json["redirect_uri"],
			nonce=nonce
		)

		hashed_identifier = generate_scrypt_hash(
			flask.g.identifier.encode("utf-8")
		)

		existing_authentication = flask.g.sa_session.get(
			database.OpenIDAuthentication,
			hashed_identifier
		)

		if existing_authentication is not None:
			existing_authentication.delete()

		database.OpenIDAuthentication.create(
			flask.g.sa_session,
			identifier=hashed_identifier,
			nonce=nonce,
			state=state
		)

		flask.g.sa_session.commit()

		return flask.jsonify({
			"uri": uri,
			"state": state,
			"nonce": nonce
		}), statuses.OK
