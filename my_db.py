from flask_sqlalchemy import SQLAlchemy

from .__init__ import db

class user_table(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(4096))
    user_id = db.Column(db.Integer)
    authkey = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)
    write_access = db.Column(db.Integer)

    def __init__(self, name, user_id, authkey, login, read_acccess, write_access):
        self.name = name
        self.user_id = user_id
        self.authkey = authkey
        self.login = login
        self.read_access = read_acccess
        self.write_access = write_access

def delete_all():
    try:
        db.session.query(user_table).delete()
        db.session.commit()
        print("Delete all done")
    except Exception as e:
        print("Failed " + str(e))
        db.session.rollback()

def get_user_row_if_exists(user_id):
    get_user_row = user_table.query.filter_by(user_id=user_id).first()
    if(get_user_row != None):
        return get_user_row
    else:
        print("User does not exist")
        return False

def add_user_and_login(name, user_id):
    row = get_user_row_if_exists(user_id)
    if(row != False):
        row.login = 1
        db.session.commit()
    else:
        print("Adding user " + name)
        new_user = user_table(name, user_id, None, 1, 0, 0)
        db.session.add(new_user)
        db.session.commit()
    print('user ' + name + " login added")

def user_logout(user_id):
    row = get_user_row_if_exists(user_id)
    if(row != False):
        row.login = 0
        db.session.commit()
        print("user " + row.name + " logout updated")


def get_all_logged_in_users():
    row = user_table.query.filter_by(login=1).all()
    online_user_record = {"user_record" : []}
    for n in range(0 ,len(row)):
        if(row[n].read_access):
            read = "checked"
        else:
            read = "unchecked"
        if row[n].write_access:
            write = "checked"
        else:
            write = "unchecked"
        online_user_record["user_record"].append([row[n].name, row[n].user_id, read, write])
        print(str(row[n].id) + " | " + row[n].name + " | " + str(row[n].user_id) + " | " + str(row[n].authkey) + " | " + str(row[n].read_access) + " | " + str(row[n].write_access))
    return online_user_record

def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError

def add_user_permission(user_id, read, write):
    row = get_user_row_if_exists(user_id)
    if row != False:
        row.read_access = bool_to_int(read)
        row.write_access = bool_to_int(write)
        db.session.commit()

def add_authkey(user_id, auth):
    row = get_user_row_if_exists(user_id)
    if row != False:
        row.authkey = auth
        db.session.commit()


def get_authkey(user_id):
    row = get_user_row_if_exists(user_id)
    if row != False:
        return row.authkey
    else:
        print("User with id: " + user_id + " does not exist")


def get_user_access(user_id):
    row = get_user_row_if_exists(user_id)
    if row != False:
        get_user_row = user_table.query.filter_by(user_id=user_id).first()
        read = get_user_row.read_access
        if read == 1:
            read = True
        else:
            read = False
        write = get_user_row.write_access
        if write == 1:
            write = True
        else:
            write = False
    return read, write




