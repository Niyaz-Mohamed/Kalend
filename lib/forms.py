from sys import excepthook
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, ValidationError

from lib import app, mongo, hasher
import requests

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})

    def validate_username(form,field):
        username=field.data

        #If user doesn't exist
        if not mongo.db.users.find_one({'username':username}):
            raise ValidationError("User doesn't exist")

    def validate_password(form,field):
        username=form.username.data
        password=field.data
        hashedPassword=mongo.db.users.find_one({'username':username})['password']

        #If password is wrong
        if hashedPassword == None:
            pass
        elif not hasher.check_value(hashedPassword,password,salt=app.secret_key):
            raise ValidationError('Incorrect Password')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    email= EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})

    def validate_username(form,field):
        username=field.data
        
        #If user already exists
        if mongo.db.users.find_one({'username':username}):
            raise ValidationError("Username taken")

        #If username isn't in correct format
        if not username.isalnum:
            modifiedUsername=username.replace('_','a')
            if not modifiedUsername.isalnum:
                raise ValidationError("Username can only contain letters, numbers, or underscores")

        if len(username) < 8:
            raise ValidationError("Username must have 8 or more characters")
        elif len(username) > 20:
            raise ValidationError("Username must have 20 or less characters")

    def validate_password(form,field):
        password=field.data

        if len(password) < 8:
            raise ValidationError("Password must have 8 or more characters")

    def validate_email(form,field):
        email=field.data

        #If email already exists in db
        if mongo.db.users.find_one({'email':email}):
            raise ValidationError("Email taken")

        #Check whether email exists
        response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params = {'email': email})
        status = response.json()['status']

        if not status == "valid":
            raise ValidationError('Email does not exist')