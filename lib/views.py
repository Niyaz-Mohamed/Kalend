from lib import app
from flask import render_template, request, url_for, redirect

@app.route('/')
def index():
  return render_template('static.html')

@app.route('/login')
def login():
  return render_template('login.html')