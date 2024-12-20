from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from importlib import import_module

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)

def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)

    # Initialize the scheduler after the app is fully configured
    from apps.home.scheduler import initialize_scheduler
    with app.app_context():
        initialize_scheduler(app)

    return app
