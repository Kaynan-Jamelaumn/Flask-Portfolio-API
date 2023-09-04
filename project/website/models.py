from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    text = db.Column(db.String(10000),  nullable=True)
    password = db.Column(db.String(150))
    image = db.Column(db.String(150),  nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    projects = db.relationship('Project')
    links = db.relationship('Link')


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    link = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    # user_id is the name of the table and the field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    resume = db.Column(db.String(400),  nullable=True)
    text = db.Column(db.String(10000),  nullable=True)
    image = db.Column(db.String(150),  nullable=True)
    public = db.Column(db.Boolean, default=False)
    source_code = db.Column(db.String(500),  nullable=True)
    live_code = db.Column(db.String(500),  nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    # user_id is the name of the table and the field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
