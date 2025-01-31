from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_migrate import Migrate



# # Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

app = Flask(__name__)
app.config.from_object('config.Config') 

db.init_app(app)
migrate.init_app(app, db)
login.init_app(app)
login.login_view = 'admin_login'  # Set the login view for Flask-Login


@login.user_loader
def load_user(user_id):
    from app.models.admin import Admin
    return Admin.query.get(int(user_id))


from app.routes.root import *
from app.routes.admin import *
from app.models import *


if __name__ == '__main__':
    app.run()


# def create_app():
#     app = Flask(__name__)
    
#     # Configuration
#     app.config.from_object('config.Config')  # Assuming your Config class is in config.py
    
    # Initialize extensions with app
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login.init_app(app)
    
#     # Login manager configuration
#     login.login_view = 'admin.login'  # Use Blueprint notation if using Blueprints
    
#     # Import models and routes after initializing extensions to avoid circular imports
#     from app.models.admin import Admin
#     from app.routes import root, admin
    
#     # Register Blueprints if using them
#     app.register_blueprint(root.bp)
#     app.register_blueprint(admin.bp)
    
#     return app

# app = create_app()

# @login.user_loader
# def load_user(user_id):
#     from app.models.admin import Admin
#     return Admin.query.get(int(user_id))

# if __name__ == '__main__':
#     app.run()
