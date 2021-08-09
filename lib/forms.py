from typing import Pattern
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, ValidationError

import re
import requests

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})

    def validate_username(form,field):
        username=field.data

        if not username.isalnum:
            modifiedUsername=username.replace('_','a')
            if not modifiedUsername.isalnum:
                raise ValidationError("Username can only contain letters, numbers, or underscores")

        if len(username) < 8:
            raise ValidationError("Username must have >8 characters")
        elif len(username) > 20:
            raise ValidationError("Username must have <20 characters")

    def validate_password(form,field):
        password=field.data
        if len(password) < 8:
            raise ValidationError("Password must have >8 characters")

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    email= EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Password"})

    def validate_username(form,field):
        username=field.data

        if not username.data.isalnum:
            modifiedUsername=username.replace('_','a')
            if not modifiedUsername.isalnum:
                raise ValidationError("Username can only contain letters, numbers, or underscores")

        if len(username) < 8:
            raise ValidationError("Username must have >8 characters")
        elif len(username) > 20:
            raise ValidationError("Username must have <20 characters")

    def validate_password(form,field):
        password=field.data
        if len(password) < 8:
            raise ValidationError("Password must have >8 characters")

    def validate_email(form,field):
        email=field.data
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

        response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params = {'email': email})
        status = response.json()['status']

        if email_regex.match(email):
            pass
        else:
            raise ValidationError('Invalid Email')
        
        if status == "valid":
            pass
        elif status == "invalid":
            ValidationError('Email does not exist')
        else:
            ValidationError('Email unknown')
