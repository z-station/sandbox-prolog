from os import environ, getuid


TIMEOUT = 5  # seconds
SANDBOX_USER_UID = int(environ.get('SANDBOX_USER_UID', getuid()))
