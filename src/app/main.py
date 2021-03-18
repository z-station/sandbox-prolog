from flask import Flask, request
from flask_cors import CORS

from app.entities.request import (
    RequestDebugDict,
    RequestTestingDict
)
from app.entities.response import (
    ResponseDebugDict,
    ResponseTestingDict
)
from app import config
from app.service import PrologService


app = Flask(__name__)
# CORS(app, origins=config.CORS_DOMAINS)
CORS(app)
service = PrologService()


@app.route('/debug/', methods=['post'])
def debug() -> ResponseDebugDict:

    data: RequestDebugDict = request.json
    result = service.debug(data)
    return result


@app.route('/testing/', methods=['post'])
def testing() -> ResponseTestingDict:

    data: RequestTestingDict = request.json
    result = service.testing(data)
    return result
