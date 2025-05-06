from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Create instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.main import main
    
    app.register_blueprint(auth)
    app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(id):
        from app.models import User
        return User.query.get(int(id))

    return app