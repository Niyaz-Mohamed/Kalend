from lib import app
from flask import render_template, request, url_for, redirect

@app.route('/')
def index():
  return render_template('index.html')