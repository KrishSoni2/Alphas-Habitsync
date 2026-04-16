# Sahib Chawla
# REST API entry point - registers all blueprints

from flask import Flask
import logging

logger = logging.getLogger(__name__)


def init_app(app: Flask):
    app.logger.setLevel(logging.DEBUG)

    # Import and register blueprints
    from backend.habits.habits_routes import habits_blueprint
    from backend.groups.groups_routes import groups_blueprint
    from backend.admin.admin_routes import admin_blueprint
    from backend.analytics.analytics_routes import analytics_blueprint

    app.register_blueprint(habits_blueprint, url_prefix='/habits')
    app.register_blueprint(groups_blueprint, url_prefix='/groups')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(analytics_blueprint, url_prefix='/analytics')

    @app.route('/')
    def index():
        return '<h1>Welcome to the HabitSync REST API</h1>'

    return app
