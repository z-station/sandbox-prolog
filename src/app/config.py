from os import environ, getuid


TIMEOUT = 10  # seconds
SANDBOX_USER_UID = int(environ.get('SANDBOX_USER_UID', getuid()))
