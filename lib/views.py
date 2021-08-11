from datetime import datetime
from os import error
from flask import render_template, request, session, url_for, redirect
from werkzeug.exceptions import HTTPException
from flask.helpers import flash, get_flashed_messages

from lib import app,mongo,hasher
from lib.forms import LoginForm, SignUpForm

@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=e)

@app.route('/')
def index():
  return render_template('static.html')

@app.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm()
  errors={'username':'', 'password':''}

  if request.method == 'POST':
    if form.validate_on_submit():
      session.pop('_flashes', None)
      #Login
      return redirect(url_for('dashboard'))
    else:
      #Handle errors
      try:
        errors['username']=form.errors['username']
      except:
        pass
      try:
        errors['password']=form.errors['password']
      except:
        pass
 
  print(errors)
  return render_template('login.html', form=form, errors=errors)

@app.route('/signup', methods=['GET','POST'])
def signup():
  form = SignUpForm()
  errors={'username':'', 'email':'', 'password':''}

  if request.method == 'POST':
    if form.validate_on_submit():
      session.pop('_flashes', None)
      #Create user
      username=form.username.data
      email=form.email.data
      password=hasher.hash_value(form.password.data,salt=app.secret_key)
      user={'username':username,'password':password,'email':email,'timestamp':datetime.now().strftime("%m/%d/%Y,%H:%M:%S")}
      #Push to MongoDB
      mongo.db.users.insert_one(user)
      return redirect(url_for('dashboard'))
    else:
      #Handle errors
      session.pop('_flashes', None)
      try:
        errors['username']=form.errors['username']
      except:
        pass
      try:
        errors['email']=form.errors['email']
      except:
        pass
      try:
        errors['password']=form.errors['password']
      except:
        pass

  return render_template('signup.html', form=form, errors=errors)

@app.route('/dashboard')
def dashboard():
  return 'Signed in'