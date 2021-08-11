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

  if request.method == 'POST':
    if form.validate_on_submit():
      print('validated')
      #Login
      return redirect(url_for('dashboard'))
    else:
      #Handle errors
      session.pop('_flashes', None)
      if 'username' not in form.errors:
        form.errors['username']=['']
      if 'password' not in form.errors:
        form.errors['password']=['']
      flash(form.errors)
  
  #Placeholder for first GET request
  try:
    get_flashed_messages[0]
  except:
    flash({'username':'','password':''})
 
  return render_template('login.html', form=form, errors=get_flashed_messages()[0])

@app.route('/signup', methods=['GET','POST'])
def signup():
  form = SignUpForm()

  if request.method == 'POST':
    if form.validate_on_submit():
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
      if 'username' not in form.errors:
        form.errors['username']=['']
      if 'email' not in form.errors:
        form.errors['email']=['']
      if 'password' not in form.errors:
        form.errors['password']=['']
      flash(form.errors)
  
  #Placeholder for first GET request
  try:
    get_flashed_messages[0]
  except:
    flash({'username':'','email':'','password':''})

  return render_template('signup.html', form=form, errors=get_flashed_messages()[0])

@app.route('/dashboard')
def dashboard():
  return 'Signed in'