from datetime import date
from operator import pos
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Rating, User,Posts
import random
import os
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy.sql.expression import func
from sqlalchemy import asc, desc



views = Blueprint('views', __name__)
displayed_posts = 9

@views.route("/")
@views.route('/home', methods=['GET', 'POST'])
def home():
    slides_article = Posts.query.order_by(func.random()).limit(3).all()
    sort = "new"
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.order_by(Posts.pub_date.desc()).paginate(page=page, per_page=displayed_posts)
    return render_template("index.html",user=current_user,posts=posts, sort=sort,slides_article=slides_article)

@views.route('/home/sorted_by_oldest', methods=['GET', 'POST'])
def oldest():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.paginate(page=page, per_page=displayed_posts)
    return render_template("index.html",user=current_user,posts=posts)



@views.route("/search", methods=['POST', 'GET'])
def search():
    search = request.args.get('search')
    if search:
        posts= Posts.query.filter(Posts.title.contains(search) | 
        Posts.content.contains(search))
        return render_template("search.html", search=search, posts=posts, user=current_user)
    else:
        posts = Posts.query.all()
        return render_template("search.html", search=search, posts=posts, user=current_user)
        



@views.route('/article/<id>', methods=['GET', 'POST'])
def article(id):
    Post = Posts.query.filter_by(id=id).first()
    Author = User.query.filter_by(id=Post.author).first()
   
    if request.method == "POST":
        selectedValue = request.form['rating']
        rating = Rating(rating=selectedValue, articleId=id)
        db.session.add(rating)
        db.session.commit()
    return render_template("article.html",user=current_user, post=Post , Author=Author)



@views.route('/author/<id>', methods=['GET', 'POST'])
def author(id):
    posts= Posts.query.filter(Posts.author.contains(id)).order_by(Posts.pub_date.desc()).limit(9).all()
    Author = User.query.filter_by(id=id).first()
    return render_template("author.html",user=current_user, posts=posts , Author=Author)






