# Sahib Chawla
# Flask application entry point

from flask import Flask
from backend.rest_entry import init_app


def create_app():
    app = Flask(__name__)
    init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)
