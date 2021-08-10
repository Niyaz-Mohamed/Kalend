from os import error
from flask import render_template, request, session, url_for, redirect
from flask.helpers import flash, get_flashed_messages

from lib import app
from lib.forms import LoginForm, SignUpForm

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
      pass
    else:
      #Handle errors
      session.pop('_flashes', None)
      if form.errors:
        for error in form.errors:
          flash(form.errors[error][0])
 
  return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
  form = SignUpForm()

  if request.method == 'POST':
    if form.validate_on_submit():
      #Signup
      pass
    else:
      #Handle errors
      session.pop('_flashes', None)
      if form.errors:
        for error in form.errors:
          flash(form.errors[error][0])
  
  return render_template('signup.html',form=form)