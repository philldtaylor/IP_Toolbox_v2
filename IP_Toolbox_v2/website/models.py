# this is where we create our database models

from datetime import timezone
from . import db
from flask_login import UserMixin # user mixin allows us to access values associated with the logged in user
from sqlalchemy.sql import func

class Resultfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# each table is a class/model
class User(db.Model, UserMixin): # the only reason we inherit from UserMixin is because we are using it as a short cut, usually we would only inherit from db.Model
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    resultfiles = db.relationship('Resultfile')