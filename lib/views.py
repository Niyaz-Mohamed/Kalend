from datetime import datetime, timedelta
from flask import render_template, request, url_for, redirect, session
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse
from bson import ObjectId

from lib import app, mongo, hasher
from lib.forms import EventCreateForm, EventFilterForm, LoginForm, SignUpForm
from lib.models import User, eventFromData

# Pretty Printing for debugging
from pprint import PrettyPrinter
pprint = PrettyPrinter(indent=4).pprint

# Error catching route
@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=e)

# Static homepage route
@app.route('/')
@app.route('/home')
def home():
    return render_template('static.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = {}

    if request.method == 'POST':
        if form.validate_on_submit():
            # Login user
            userId = mongo.db.users.find_one(
                {'username': form.username.data})['_id']
            login_user(User(userId), remember=True)

            # Authenticate next parameter
            nextPage = request.args.get('next')
            if not nextPage or url_parse(nextPage).netloc != '':
                nextPage = url_for('dashboard')
            return redirect(nextPage)
        else:
            # Handle errors
            errors.update(form.errors)

    return render_template('login.html', form=form, errors=errors)

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
                    'timestamp': datetime.now()}
            # Push to MongoDB
            insertedUser = mongo.db.users.insert_one(user)
            # Login new user
            authUser = User(insertedUser.inserted_id)
            print(authUser)
            print(authUser.email)
            login_user(authUser, remember=True)

            # Authenticate next parameter
            nextPage = request.args.get('next')
            if not nextPage or url_parse(nextPage).netloc != '':
                nextPage = url_for('dashboard')
            return redirect(nextPage)
        else:
            # Handle errors
            errors.update(form.errors)

    return render_template('signup.html', form=form, errors=errors)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Main app page routes
@login_required
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = EventFilterForm()
    eventPointer = mongo.db.events.find(
        {'creatorId': ObjectId(session['_user_id'])})
    events = []
    for event in eventPointer:
        events.append(eventFromData(event))
    return render_template('dashboard.html', events=events, form=form)

@login_required
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    form = EventFilterForm()
    events = []
    for event in mongo.db.events.find():
        if event.get('creatorId') != ObjectId(session['_user_id']):
            events.append(eventFromData(event))
    return render_template('explore.html', events=events, form=form)

@login_required
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@login_required
@app.route('/eventcreate', methods=['GET', 'POST'])
def eventCreate():
    form = EventCreateForm()
    errors = {}
    pprint(request.form)
    pprint(request.files)

    if request.method == 'POST':
        if form.validate_on_submit():
            print('yay')
        else:
            # Handle errors
            errors.update(form.errors)

    return render_template('eventcreate.html', form=form, errors=errors)

@login_required
@app.route('/events/<id>')
def eventRouter(id):
    return str(mongo.db.events.find_one({'_id': ObjectId(id)}))
