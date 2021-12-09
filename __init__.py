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

test = os.getenv("TEST")
print(test)

facebook_id = os.getenv('FACEBOOK_APP')
print(facebook_id)
facebook_secret = os.getenv('FACEBOOK_SECRET')

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
    return render_template('index.html', user_id=session['user_id'], online_users = my_db.get_all_logged_in_users())

def clear_user_session():
    session['logged_in'] = None
    session['facebook_token'] = None
    session['user'] = None
    session['user_id'] = None

@app.route('/logout')
@login_required
def logout():
    my_db.user_logout(session['user_id'])
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


@app.route('/grant-<who>-<key_or_id>-<read>-<write>', methods=['GET', 'POST'])
def grant_access(who, key_or_id, read, write):
    if int(session['user_id']) == 327150209222373:
        print("Granting " + key_or_id + " read " + read + ", write " + write + " permision")
        my_db.add_user_permission(key_or_id, read, write)
        authkey = my_db.get_auth_key(key_or_id)
        PB.grant_access(key_or_id, str_to_bool(read), str_to_bool(write))
    else:
        print("WHO ARE YOU?")
        return json.dumps({"access" : "denied"})
    return json.dumps({"access" : "granted"})



if __name__ == '__main__':
    app.run()





