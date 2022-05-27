from flask import (
    Flask,
    request,
    render_template,
    abort
)
from marshmallow import ValidationError
from app.service.main import PrologDService
from app.schema import (
    DebugSchema,
    TestsSchema,
    BadRequestSchema
)
from app.service.exceptions import ServiceException


def create_app():

    app = Flask(__name__)

    @app.errorhandler(400)
    def bad_request_handler(ex: Exception):
        return BadRequestSchema().dump(ex), 400

    @app.route('/', methods=['get'])
    def index():
        return render_template("index.html")

    @app.route('/debug/', methods=['post'])
    def debug():
        schema = DebugSchema()
        try:
            data = PrologDService.debug(
                schema.load(request.get_json())
            )
        except (ServiceException, ValidationError) as ex:
            abort(400, ex)
        else:
            return schema.dump(data)

    @app.route('/testing/', methods=['post'])
    def testing():
        schema = TestsSchema()
        try:
            data = PrologDService.testing(
                schema.load(request.get_json())
            )
        except (ServiceException, ValidationError) as ex:
            abort(400, ex)
        else:
            return schema.dump(data)
    return app


app = create_app()
