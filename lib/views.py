from datetime import datetime
from flask import render_template, request, url_for, redirect
from flask_login.utils import login_required, login_user, logout_user, current_user
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse
from bson import ObjectId
from werkzeug.utils import secure_filename

from lib import app, mongo, hasher
from lib.forms import EventForm, EventFilterForm, LoginForm, SignUpForm, eventFormFromEvent
from lib.models import User, bookingFromData, eventFromData

# Pretty Printing for debugging
from pprint import PrettyPrinter
pprint = PrettyPrinter(indent=4).pprint

# Error catching route
@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=e)

#Retreiving files from mongo
@app.route('/file/<filename>')
@login_required
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

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Event Searcher
def search(searchType, query, events):
    filteredEvents = list(events)
    removalIdentifier = 'marker'
    query = query.lower()

    for eventIndex in range(len(events)):
        event = events[eventIndex]

        # Search by event name
        if searchType == 'eName':
            if query not in event.name.lower():
                filteredEvents[eventIndex]=removalIdentifier
        # Search by event code
        elif searchType == 'eCode':
            if query == '':
                continue
            elif str(event.id).lower() != query:
                filteredEvents[eventIndex]=removalIdentifier
        # Search by creator name
        elif searchType == 'uName':
            creatorName = mongo.db.users.find_one(
                {'_id': ObjectId(event.creatorId)}).get('username').lower()
            if query == '':
                continue
            elif query not in creatorName:
                filteredEvents[eventIndex] = removalIdentifier

    filteredEvents = filter(lambda a: a != removalIdentifier, filteredEvents)
    return filteredEvents

#* Main app page routes
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = EventFilterForm()
    eventPointer = mongo.db.events.find(
        {'creatorId': ObjectId(current_user.id)})
    events = []
    for event in eventPointer:
        events.append(eventFromData(event))

    # Filter Events
    if request.method == 'POST':
        query = form.search.data
        searchType = form.searchType.data
        events = search(searchType, query, events)

    return render_template('dashboard.html', events=events, form=form)

@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    form = EventFilterForm()
    events = []
    for event in mongo.db.events.find():
        if event.get('creatorId') != ObjectId(current_user.id):
            events.append(eventFromData(event))

    # Filter Events
    if request.method == 'POST':
        query = form.search.data
        searchType = form.searchType.data
        events = search(searchType, query, events)

    return render_template('explore.html', events=events, form=form)

@app.route('/schedule')
@login_required
def schedule():
    return render_template('schedule.html')

# Event Creation Route
@app.route('/eventcreate', methods=['GET', 'POST'])
@login_required
def eventCreate():
    form = EventForm()
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
@app.route('/events/<id>')
@login_required
def eventRouter(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))
    
    # Check credentials
    isAdmin = False
    if current_user.id == str(event.creatorId):
        isAdmin = True

    isBooked = False
    if not isAdmin:
        existingBooking = mongo.db.bookings.find_one(
            {'eventId': ObjectId(id), 'attendeeId': ObjectId(current_user.id)})
        if existingBooking:
            isBooked = True

    return render_template('eventdisplay.html', event=event, isAdmin=isAdmin, isBooked=isBooked)

#* Admin Only Action Routes
# Event Bookings
@app.route('/events/<id>/bookings')
@login_required
def eventBookings(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check credentials
    if not current_user.id == str(event.creatorId):
        return redirect('/events/'+str(event.id))
    #Get Bookings
    bookings = []
    for booking in mongo.db.bookings.find():
        if booking.get('eventId') == ObjectId(id):
            bookings.append(bookingFromData(booking))

    return render_template('eventbookings.html', bookings=bookings, event=event)

# Event Editing
@app.route('/events/<id>/edit', methods=['GET', 'POST'])
@login_required
def eventEdit(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))
    form = eventFormFromEvent(event)

    # Check credentials
    if not current_user.id == str(event.creatorId):
        return redirect('/events/'+str(event.id))
    errors = {}

    #Validate form and perform actions
    if request.method == 'POST':
        if form.validate_on_submit():
            data={}
            for field in request.form:
                data.update({field: request.form.get(field)})

            # Process data
            data.pop('csrf_token')
            data['startTime'] = datetime.strptime(
                data.get('startTime'), '%Y-%m-%dT%H:%M')
            data['endTime'] = datetime.strptime(
                data.get('endTime'), '%Y-%m-%dT%H:%M')
            data['totalSlots'] = int(data.get('totalSlots'))
            # Push to mongo database
            mongo.db.events.update_one({'_id': ObjectId(id)}, {"$set": data})
            return redirect('/events/'+str(event.id))
        else:
            # Handle errors
            errors.update(form.errors)

    return render_template('eventedit.html', form=form, event=event, errors=errors)

# Event Deletion
@app.route('/events/<id>/delete')
@login_required
def eventDelete(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check credentials
    if not current_user.id == str(event.creatorId):
        return redirect('/events/'+str(event.id))
    else:
        mongo.db.events.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('dashboard'))

#* General User Routes
# Event Booking for Clients
@app.route('/events/<id>/bookevent')
@login_required
def eventBook(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check Credentials
    if current_user.id == str(event.creatorId):
        return redirect('events/'+str(event.id))
    # Book Event
    bookingData = {'eventId': ObjectId(event.id), 'attendeeId': ObjectId(
        current_user.id), 'timestamp': datetime.now()}
    existingBooking = mongo.db.bookings.find_one(
        {'eventId': bookingData['eventId'], 'attendeeId': bookingData['attendeeId']})
    if not existingBooking:
        mongo.db.bookings.insert_one(bookingData)

    return redirect('/events/'+str(event.id))

# Event Unbooking for Clients
@app.route('/events/<id>/unbookevent')
@login_required
def eventUnbook(id):
    event = eventFromData(mongo.db.events.find_one({'_id': ObjectId(id)}))

    # Check Credentials
    if current_user.id == str(event.creatorId):
        return redirect('events/'+str(event.id))
    # Find Booking
    existingBooking = mongo.db.bookings.find_one(
        {'eventId': ObjectId(event.id), 'attendeeId': ObjectId(current_user.id)})
    if existingBooking:
        mongo.db.bookings.delete_one(existingBooking)

    return redirect('/events/'+str(event.id))
