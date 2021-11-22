import datetime
import typing

import authlib.common.security
import authlib.integrations.requests_client
import authlib.jose
import authlib.oidc.core
import flask
import magic
import requests
import sqlalchemy

from .. import encoders, exceptions, helpers, limiter, models, validators
from .helpers import create_jwt, get_endpoint_limit

__all__ = ["openid_blueprint"]

openid_blueprint = flask.Blueprint(
	"openid",
	__name__,
	url_prefix="/openid"
)
openid_blueprint.json_encoder = encoders.JSONEncoder


def get_config(client_name: str) -> typing.Dict[
		str,
		typing.Dict[
			str,
			str
		]
	]:
	"""Returns the current app's config for the given OpenID service.
	If the `scope` parameter is missing or lacks `'openid'`, it's added.
	"""

	config = flask.current_app.config["OPENID_SERVICES"][client_name].copy()

	if "scope" not in config:
		config["scope"] = "openid"
	elif "openid" not in config["scope"]:
		config["scope"] = f"openid {config['scope']}"

	return config


@openid_blueprint.route("", methods=["GET"])
@limiter.limiter.limit(get_endpoint_limit)
def list_() -> typing.Tuple[flask.Response, int]:
	"""Returns all available OpenID services.

	Idempotent.
	"""

	return flask.jsonify(
		[
			service
			for service in flask.current_app.config["OPENID_SERVICES"].keys()
		]
	), helpers.STATUS_OK


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
@limiter.limiter.limit(get_endpoint_limit)
def authorize(client_name: str) -> typing.Tuple[flask.Response, int]:
	"""Gets OpenID's `userinfo` by logging in through an OAuth session,
	and creates a JWT for the associated user. If there is none, the user
	is automatically created. The `registered_by` column will be
	`openid.$the_name_of_the_current_service`.

	Not idempotent.
	"""

	if client_name not in flask.current_app.config["OPENID_SERVICES"]:
		raise exceptions.APIOpenIDServiceNotFound(client_name)

	# Delete all expired entries
	flask.g.sa_session.execute(
		sqlalchemy.delete(models.OpenIDAuthentication).
		where(
			models.OpenIDAuthentication.creation_timestamp
			> (
				datetime.datetime.now(tz=datetime.timezone.utc) +
				datetime.timedelta(seconds=flask.current_app.config[
					"OPENID_AUTHENTICATION_EXPIRES_AFTER"
				])
			)
		)
	)

	authentication = flask.g.sa_session.execute(
		sqlalchemy.select(models.OpenIDAuthentication).
		where(
			sqlalchemy.and_(
				models.OpenIDAuthentication.identifier == flask.g.identifier,
				models.OpenIDAuthentication.state == flask.g.json["state"]
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

		registered_by = f"openid.{client_name}"

		user = flask.g.sa_session.execute(
			sqlalchemy.select(models.User).
			where(
				sqlalchemy.and_(
					models.User.registered_by == registered_by,
					models.User.external_id == userinfo["sub"]
				)
			)
		).scalars().one_or_none()

		avatar_url = userinfo.get("picture")

		avatar = None
		avatar_type = None

		if avatar_url is not None:
			avatar = requests.get(avatar_url)

			m = magic.Magic(mime=True)
			avatar_type = m.from_buffer(avatar)

		if user is None:
			user = models.User.create(
				flask.g.sa_session,
				registered_by=registered_by,
				external_id=userinfo["sub"],
				avatar_type=avatar_type,
				name=userinfo.get("preferred_username"),
			)

			# Be absolutely sure `avatar_type` is already set.
			# Is this necessary?
			user.avatar = avatar

			status = helpers.STATUS_CREATED
		else:
			status = helpers.STATUS_OK

		flask.g.sa_session.commit()

		oa2_session.revoke_token(
			oa2_session.metadata["token_endpoint"],
			token=token["access_token"]
		)

		return flask.jsonify(
			{
				"token": create_jwt(user.id)
			}
		), status


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
@limiter.limiter.limit(get_endpoint_limit)
def login(client_name: str) -> typing.Tuple[flask.Response, int]:
	"""Creates a URL for a user with access to a browser to log in through.

	Not idempotent.
	"""

	if client_name not in flask.current_app.config["OPENID_SERVICES"]:
		raise exceptions.APIOpenIDServiceNotFound(client_name)

	with authlib.integrations.requests_client.OAuth2Session(
		**get_config(client_name)
	) as oa2_session:
		nonce = authlib.common.security.generate_token()

		uri, state = oa2_session.create_authorization_url(
			oa2_session.metadata["authorization_endpoint"],
			redirect_uri=flask.g.json["redirect_uri"],
			nonce=nonce
		)

		existing_authentication = flask.g.sa_session.get(
			models.OpenIDAuthentication,
			flask.g.identifier
		)

		if existing_authentication is not None:
			existing_authentication.delete()

		models.OpenIDAuthentication.create(
			flask.g.sa_session,
			identifier=flask.g.identifier,
			nonce=nonce,
			state=state
		)

		flask.g.sa_session.commit()

		return flask.jsonify(
			{
				"uri": uri,
				"state": state,
				"nonce": nonce
			}
		), helpers.STATUS_OK
