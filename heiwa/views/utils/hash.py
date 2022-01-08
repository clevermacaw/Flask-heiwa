import hashlib

import flask


def generate_scrypt_hash(
	origin: bytes,
	dklen: int = 32
) -> str:
	"""Generates an SCrypt hash for the given origin, with the current app's
	secret key as the salt.

	:param origin: The original bytes to hash.
	:param dklen: The length of the resulting hash.

	:returns: The hash.

	.. note::
		The app's secret key isn't the greatest salt ever, but the best we can
		afford to use here, since this function is also used for finding values
		where the salt is already known beforehand. Unfortunately, this means
		using a random string is out of the question.
	"""

	return hashlib.scrypt(
		origin,
		salt=flask.current_app.config["SECRET_KEY"].encode("utf-8"),
		n=flask.current_app.config["SCRYPT_N"],
		r=flask.current_app.config["SCRYPT_R"],
		p=flask.current_app.config["SCRYPT_P"],
		maxmem=flask.current_app.config["SCRYPT_MAXMEM"],
		dklen=dklen
	).hex()
