from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()


def create_app():

	app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
	app.config.from_object('config.Config')
	
	db.init_app(app)
	migrate.init_app(app, db)

	from .routes.auth_routes import auth
	app.register_blueprint(auth)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login_form'
	login_manager.init_app(app)

	from .db_models import User

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	with app.app_context():
		from .routes import routes_fintech, routes_currency, auth_routes
		from . import db_models
		db.create_all()

	return app