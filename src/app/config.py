from os import environ as env
from tempfile import gettempdir

TMP_DIR = gettempdir()
TIMEOUT = 5  # seconds

CORS_DOMAINS = env.get('CORS_DOMAINS')
CORS_DOMAINS = CORS_DOMAINS.split(',') if CORS_DOMAINS else []
CORS_DOMAINS += [r'http[s]?:\/\/localhost[:]?[0-9]*']
