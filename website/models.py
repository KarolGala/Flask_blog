from email.mime import image
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func 
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    join_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    image = db.Column(db.String(9999), nullable=True)
    bio = db.Column(db.String(9999), nullable=True)
    instagram = db.Column(db.String(999), nullable=True)
    website = db.Column(db.String(999), nullable=True)
    
class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400))
    preview = db.Column(db.String(400))
    content = db.Column(db.String(9999))
    comments = db.Column(db.String(9999))
    image = db.Column(db.String(9999))
    pub_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    author = db.Column(db.String(400))
    category = db.Column(db.String(400))

class Rating(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.String(40))
    articleId = db.Column(db.String(999))
    pub_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    
