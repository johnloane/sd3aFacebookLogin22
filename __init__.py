from flask import Flask, render_template, session, redirect, url_for, flash
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

import json
import os

import time, threading

from . import my_db

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Mysql1234!@localhost/sd3a_login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

alive = 0
data = {}

facebook_id = '262680999236983'#os.getenv('sd3aFacebookApp')
print(facebook_id)
facebook_secret = 'd3fca92625388651a041d86af8e575fb'#os.getenv('sd3aFacebookSecret')

facebook_blueprint = make_facebook_blueprint(client_id = facebook_id, client_secret = facebook_secret, redirect_url= '/facebook_login')
app.register_blueprint(facebook_blueprint, url_prefix = '/facebook_login')


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            if session['logged_in']:
                return f(*args, **kwargs)
        flash("Please login first")
        return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    return render_template("login.html")


@app.route('/facebook_login')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    account_info = facebook.get('/me')
    if account_info.ok:
        print("Access token", facebook.access_token)
        me = account_info.json()
        session['logged_in'] = True
        session['facebook_token'] = facebook.access_token
        session['user'] = me['name']
        session['user_id'] = me['id']
        return redirect(url_for('main'))

@app.route('/main')
@login_required
def main():
    flash(session['user'])
    my_db.add_user_and_login(session['user'], int(session['user_id']))
    return render_template('index.html')

def clear_user_session():
    session['logged_in'] = None
    session['facebook_token'] = None
    session['user'] = None
    session['user_id'] = None

@app.route('/logout')
@login_required
def logout():
    clear_user_session()
    flash("You just logged out")
    return redirect(url_for('login'))

@app.route('/login')
def login():
    clear_user_session()
    return render_template('login.html')



@app.route('/keep_alive')
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data['keep_alive'] = keep_alive_count
    parsed_json = json.dumps(data)
    return str(parsed_json)

@app.route("/status=<name>-<action>", methods=["POST"])
def event(name, action):
    global data
    print("Got " + name + ", action: " + action)
    if name == "buzzer":
        if action == "ON":
            data["alarm"] = True
        elif action == "OFF":
            data["alarm"] = False
    return str("OK")


if __name__ == '__main__':
    app.run()





