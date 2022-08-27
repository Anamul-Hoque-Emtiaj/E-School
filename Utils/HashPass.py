
from passlib.hash import pbkdf2_sha256

def passlib_encryption(raw_password):
	if raw_password:
		encrypted = pbkdf2_sha256.hash(raw_password)
	else:
		encrypted = None
	
	return encrypted

def passlib_encryption_verify(raw_password, enc_password):
	if raw_password and enc_password:
		response = pbkdf2_sha256.verify(raw_password, enc_password)
	else:
		response = None;
	
	return response

