from flask import Flask, Blueprint, request, render_template, redirect, flash
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_models import db, User


auth = Blueprint('auth', __name__)


# ------------------Sign_up------------------

@auth.route('/signup_form', strict_slashes=False)
def signup_form():
    return render_template('sign_up.html')


@auth.route('/signup', methods=['POST'], strict_slashes=False)
def signup():
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    password = request.form.get('password')

    user_email = db.session.query(User).filter_by(email=email).first()
    user_nickname = db.session.query(User).filter_by(nickname=nickname).first()

    if user_email:
        flash('Email address already exists')
        return redirect('/signup_form')

    if user_nickname:
        flash('Nickname already exists')
        return redirect('/signup_form')
    
    user = User(nickname=nickname, email=email, password=generate_password_hash(password, method='sha256'))
    db.session.add(user)
    db.session.commit()

    return redirect('/')


# ------------------Login------------------

@auth.route('/')
def login_form():
    return render_template('login.html')


@auth.route('/login', methods=['POST'], strict_slashes=False)
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = db.session.query(User).filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect('/')
    
    login_user(user, remember=remember)
    return redirect('/index')


# ------------------Logout------------------

@auth.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    return redirect('/')