from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User,Posts
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import Posts
import os
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy.sql.expression import func
from sqlalchemy import asc, desc


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('auth.profile'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name,last_name=last_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.profile'))

    return render_template("sign_up.html", user=current_user)



@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile.html",user=current_user)

@auth.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    id = current_user.id
    userloggedin = User.query.get_or_404(id)
    if request.method == "POST":
        userloggedin.website = request.form.get('website')
        userloggedin.instagram = request.form.get('instagram')
        userloggedin.bio = request.form.get('bio')
        file = request.files['file']
        userloggedin.image = file.filename
        if not userloggedin.bio:
            flash('Bio cannot be empty', category='error')
        else:
            db.session.commit()
            flash('bio updated!', category='success')
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash('Profile picture updated succesfully')
            return redirect(url_for('auth.profile'))
    return render_template("X/editprofile.html",user=current_user)



@auth.route('/create-article', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get('title')
        preview = request.form.get('preview')
        # content = request.form.get('content')
        content = request.form.get('ckeditor')
        file = request.files['file']
        img_name = file.filename
        author = current_user.id
        category = request.form.get('category')
        if not content:
            flash('Post cannot be empty', category='error')
        else:
            post = Posts(title=title,preview=preview, content=content, image=img_name, author=author,category=category)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            return render_template('X/createarticle.html',user=current_user)
    return render_template("X/createarticle.html",user=current_user)



@auth.route('/update-article/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    article = Posts.query.get_or_404(id)
    if not article:
        flash("Post does not exist.", category='error')
    else:
        if request.method == "POST":
            article.title = request.form.get('title')
            article.preview = request.form.get('preview')
            article.content = request.form.get('ckeditor')
            file = request.files['file']
            article.image = file.filename
            article.author = current_user.id
            article.category = request.form.get('category')
            if not article.content:
                flash('Post cannot be empty', category='error')
            else:
                db.session.commit()
                flash('Post updated successfully!', category='success')
                if not file:
                    return redirect(url_for('auth.deletev2'))
                else:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    flash('Image successfully updated ')
                    return redirect(url_for('auth.deletev2'))
    return render_template("X/editarticle.html",user=current_user, article=article)



@auth.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Posts.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist.", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')
    return redirect(url_for('auth.deletev2'))


displayed_posts = 9

@auth.route('/delete', methods=['GET', 'POST'])
@login_required
def deletev2():
    if current_user.is_authenticated == False:
        return redirect(url_for('views.home'))
    else:
        sort = "new"
        posts = Posts.query.all()
        page = request.args.get('page', 1, type=int)
        posts = Posts.query.order_by(Posts.pub_date.desc()).paginate(page=page, per_page=displayed_posts)
        return render_template("X/delete.html",user=current_user, posts=posts, sort=sort)




@auth.route('/delete/sorted_by_oldest', methods=['GET', 'POST'])
def oldest():
    sort = "oldest"
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.paginate(page=page, per_page=displayed_posts)
    return render_template("X/delete.html",user=current_user, posts=posts, sort=sort)