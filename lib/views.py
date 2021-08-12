from datetime import datetime
from os import error
from flask import render_template, request, session, url_for, redirect
from flask_login import login_user
from flask_login.utils import login_required, login_user
from werkzeug.exceptions import HTTPException
from flask.helpers import flash, get_flashed_messages

from lib import app, mongo, hasher
from lib.forms import LoginForm, SignUpForm
from lib.models import User

# Error catching route
@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=e)

# Static homepage route
@app.route('/')
def index():
    return render_template('static.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = {}

    if request.method == 'POST':
        if form.validate_on_submit():
            # Login user
            userId= mongo.db.users.find_one({'username':form.username.data})['_id']
            login_user(User(userId), remember=True)
            return redirect(url_for('dashboard'))
        else:
            # Handle errors
            errors.update(form.errors)

    print(errors)
    return render_template('login.html', form=form, errors=errors)

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    errors = {}

    if request.method == 'POST':
        if form.validate_on_submit():
            # Create user
            username = form.username.data
            email = form.email.data
            password = hasher.hash_value(
                form.password.data, salt=app.secret_key)
            user = {'username': username, 'password': password, 'email': email,
                    'timestamp': datetime.now().strftime("%m/%d/%Y,%H:%M:%S")}
            # Push to MongoDB
            insertedUser = mongo.db.users.insert_one(user)
            # Login new user
            login_user(User(insertedUser.inserted_id), remember=True)
            return redirect(url_for('dashboard'))
        else:
            # Handle errors
            errors.update(form.errors)

    print(errors)
    return render_template('signup.html', form=form, errors=errors)

@login_required
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')