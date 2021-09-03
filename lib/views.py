from datetime import datetime, timedelta
from flask import render_template, request, url_for, redirect, session
from flask_login.utils import login_required, login_user, logout_user, current_user
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse
from bson import ObjectId
from werkzeug.utils import secure_filename

from lib import app, mongo, hasher, gridfs
from lib.forms import EventCreateForm, EventFilterForm, LoginForm, SignUpForm
from lib.models import User, eventFromData

# Pretty Printing for debugging
from pprint import PrettyPrinter
pprint = PrettyPrinter(indent=4).pprint

# Error catching route
@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=e)

#Retreiving files from mongo
@login_required
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

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

#! Main app page routes
@login_required
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = EventFilterForm()
    eventPointer = mongo.db.events.find(
        {'creatorId': ObjectId(current_user.id)})
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
        if event.get('creatorId') != ObjectId(current_user.id):
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

    if request.method == 'POST':
        if form.validate_on_submit():
            data = {}
            data['creatorId'] = ObjectId(current_user.id)
            for field in request.form:
                data.update({field: request.form.get(field)})

            # Process data
            data.pop('csrf_token')
            data['startTime'] = datetime.strptime(
                data.get('startTime'), '%Y-%m-%dT%H:%M')
            data['endTime'] = datetime.strptime(
                data.get('endTime'), '%Y-%m-%dT%H:%M')
            data['totalSlots'] = int(data.get('totalSlots'))
            createdEventId = mongo.db.events.insert_one(data).inserted_id
            # Upload Image
            file = request.files.get('img')
            file.filename = 'event{}.'.format(
                createdEventId) + file.filename.split('.')[-1]
            if secure_filename(file.filename):
                mongo.save_file(file.filename, file)
                mongo.db.events.update({'_id': ObjectId(createdEventId)},
                                       {'$set': {'displayImgName': file.filename}})
            return redirect(url_for('dashboard'))
        else:
            # Handle errors
            errors.update(form.errors)

    return render_template('eventcreate.html', form=form, errors=errors)

# Event Display Page
@login_required
@app.route('/events/<id>')
def eventRouter(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))
    
    # Check credentials
    isAdmin = False
    if current_user.id == str(event.creatorId):
        isAdmin = True
    return render_template('eventdisplay.html', event=event, isAdmin=isAdmin)

#! Admin Only Routes
# Event Bookings
@login_required
@app.route('/events/<id>/bookings')
def eventBookings(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check credentials
    if not current_user.id == str(event.creatorId):
        return redirect('events/'+str(event.id))
    return render_template('eventbookings.html', event=event)

# Event Editing
@login_required
@app.route('/events/<id>/edit', methods=['GET', 'POST'])
def eventEdit(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check credentials
    if not current_user.id == str(event.creatorId):
        return redirect('events/'+str(event.id))
    return render_template('eventedit.html', event=event)

#! General User Routes
# Event Booking for Clients
@login_required
@app.route('/events/<id>/bookevent')
def eventBook(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))
    # Book Event
    
    return redirect('/events/'+str(event.id))