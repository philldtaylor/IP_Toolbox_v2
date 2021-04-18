from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_manager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uhiluhyfhjffmhgc'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # f string allows us to dynamically specify the project name 
    db.init_app(app) # initiates our db and tells it what our app is????

    from .views import views # import our different end points
    from .auth import auth

    app.register_blueprint(views, url_prefix='/') # register our blueprints
    app.register_blueprint(auth, url_prefix='/') # this defines the first part of url, if we had '/auth/' here to go to a route for hello from here we would ahve to got to /auth/hello/

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # where should users go who aren't logged in - name of our template and name of our function
    login_manager.init_app(app) # tell login manager what our app is

    @login_manager.user_loader # this is how we load the user who has logged in
    def load_user(id):
        return User.query.get(int(id)) #by default the User.query.get works off primary key, hnec we dont need id = id

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME): # only create db if it doesn't exist so we avoid overwriting data
        db.create_all(app=app)
        print('Created Database!')