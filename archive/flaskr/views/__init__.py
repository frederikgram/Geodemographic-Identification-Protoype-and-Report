import flask
from flask import Flask, render_template, url_for, request, current_app
from flaskr import app

@app.route('/')
def index():
    return render_template("index.html")