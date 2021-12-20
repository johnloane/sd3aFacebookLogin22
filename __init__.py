from flask import Flask, render_template, session, redirect, url_for, flash
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

import json
import os
import hashlib, random, string

import time, threading

from . import my_db, PB

app = Flask(__name__)

mysql_password = os.getenv("MYSQL_PASSWORD")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:'+mysql_password+'@localhost/sd3a_login'
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
# Give the raspberry pi an auth key (johns-raspberry-pi) and give it read and write access to the channel
PB.grant_access("johns-raspberry-pi", True, True)


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

def str_to_bool(s):
    if 'true' in str(s):
        return True
    elif 'false' in str(s):
        return False
    else:
        raise ValueError


@app.route('/grant-<who>-<key_or_id>-<read>-<write>', methods=['GET', 'POST'])
def grant_access(who, key_or_id, read, write):
    if int(session['user_id']) == 327150209222373:
        print("Granting " + key_or_id + " read " + read + ", write " + write + " permision")
        my_db.add_user_permission(key_or_id, read, write)
        authkey = my_db.get_authkey(key_or_id)
        PB.grant_access(key_or_id, str_to_bool(read), str_to_bool(write))
    else:
        print("WHO ARE YOU?")
        return json.dumps({"access" : "denied"})
    return json.dumps({"access" : "granted"})

def salt(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_auth_key():
    s = salt(10)
    hash_string = str(session['facebook_token']) + s
    hashing = hashlib.sha256(hash_string.encode('utf-8'))
    return hashing.hexdigest()

@app.route('/get_authkey', methods=['POST', 'GET'])
def get_authkey():
    print("Creating authkey for " + session['user'])
    auth_key = create_auth_key()
    my_db.add_authkey(int(session['user_id']), auth_key)
    (read, write) = my_db.get_user_access(int(session['user_id']))
    PB.grant_access(auth_key, read, write)
    auth_response = {'auth_key':auth_key, 'cipher_key': PB.cipher_key}
    json_response = json.dumps(auth_response)
    return str(json_response)


if __name__ == '__main__':
    app.run()





