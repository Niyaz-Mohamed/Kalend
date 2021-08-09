from os import error
from flask import render_template, request, url_for, redirect
from flask.helpers import flash

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
      #login
      pass
    else:
      #Handle errors
      flash('Failure to submit form {}'.format(form.errors))
 
  return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
  form = SignUpForm()

  if request.method == 'POST':
    if form.validate_on_submit():
      #signup
      pass
    else:
      #Handle errors
      flash('Failure to submit form {}'.format(form.errors))
  
  return render_template('signup.html',form=form)