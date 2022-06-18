from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os


db = SQLAlchemy()
DB_NAME = "my_models.db"
UPLOAD_FOLDER = os.path.join(os.getcwd(),'website/static/images')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "asdsadas"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
   
    db.init_app(app)

    from . import models
    create_database(app)

    from .models import User

    
    with app.app_context():
        admin = User.query.filter_by(first_name = "admin").first()
        #print(admin.first_name)
        if not admin:
            create_admin(User,db)

    ##Blueprint registration
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/" )
    app.register_blueprint(auth, url_prefix = "/" )

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists("website/"+DB_NAME):
        db.create_all(app=app)
        print("CREATED DATABASE")

def create_admin(User,db):
    #Making a admin 
    admin_pass = ""
    new_user = User(email="admin123@gmail.com", first_name= "admin", address="",password = generate_password_hash(admin_pass,method="sha256"))
    db.session.add(new_user)
    db.session.commit()