from datetime import datetime
from sys import excepthook
from flask.app import Flask
from flask_wtf import FlaskForm
from werkzeug.datastructures import Range
from wtforms.fields import StringField, PasswordField
from wtforms.fields.core import SelectField
from wtforms.fields.html5 import DateTimeField, EmailField, IntegerField, SearchField
from wtforms.fields.simple import HiddenField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError

from lib import app, mongo, hasher
import requests

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired()], render_kw={
                           "placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={
                             "placeholder": "Password"})

    def validate_username(form, field):
        username = field.data

        # If user doesn't exist
        if not mongo.db.users.find_one({'username': username}):
            raise ValidationError("User doesn't exist")

    def validate_password(form, field):
        username = form.username.data
        password = field.data
        hashedUser = mongo.db.users.find_one({'username': username})

        # If password is wrong
        if hashedUser == None:
            pass
        elif not hasher.check_value(hashedUser['password'], password, salt=app.secret_key):
            raise ValidationError('Incorrect Password')

class SignUpForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(), Length(min=8,max=20)], render_kw={
                           "placeholder": "Username"})
    email = EmailField('Email', validators=[InputRequired()], render_kw={
                       "placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)], render_kw={
                             "placeholder": "Password"})

    def validate_username(form, field):
        username = field.data

        # If user already exists
        if mongo.db.users.find_one({'username': username}):
            raise ValidationError("Username taken")

        # If username isn't in correct format
        if not username.isalnum:
            modifiedUsername = username.replace('_', 'a')
            if not modifiedUsername.isalnum:
                raise ValidationError(
                    "Username can only contain letters, numbers, or underscores")

    def validate_email(form, field):
        email = field.data

        # If email already exists in db
        if mongo.db.users.find_one({'email': email}):
            raise ValidationError("Email taken")

        # Check whether email exists
        response = requests.get(
            "https://isitarealemail.com/api/email/validate",
            params={'email': email})
        status = response.json()['status']

        if not status == "valid":
            raise ValidationError('Email does not exist')

class EventFilterForm(FlaskForm):

    search = SearchField('Search Events', validators=[InputRequired()], render_kw={
        "placeholder": "Search Events"})
    searchType = SelectField('Search Type', validators=[InputRequired()], choices=[(
        'eventName', 'Search by Name'), ('eventCode', 'Search by Code')])

class EventCreateForm(FlaskForm):

    name = StringField('Event Name', validators=[InputRequired()], render_kw={
        "placeholder": "Name"})
    desc = TextAreaField('Description', validators=[InputRequired()], render_kw={
        "placeholder": "Description"})
    startTime = DateTimeField('Start Time', validators=[InputRequired()], render_kw={
        "placeholder": "Start Time"})
    endTime = DateTimeField('End Time', validators=[InputRequired()], render_kw={
        "placeholder": "End Time"})
    location = StringField('Location', validators=[InputRequired()], render_kw={
        "placeholder": "Location"})
    totalSlots = IntegerField('Slots Avaliable', validators=[InputRequired()], render_kw={
        "placeholder": "Slots Avaliable"})

    def validate_startTime(form, field):
        startTime = field.data
        if not startTime > datetime.now():
            raise ValidationError('Invalid Start Time')

    def validate_endTime(form, field):
        endTime = field.data
        startTime = form.desc.data
        if not endTime > startTime:
            raise ValidationError('End Time must be after Start Time')
