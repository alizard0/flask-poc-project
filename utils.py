import uuid, OpenSSL,bcrypt

def generate_token():
    return uuid.UUID(bytes = OpenSSL.rand.bytes(16))


def generate_salt():
	return bcrypt.gensalt(rounds=24)
