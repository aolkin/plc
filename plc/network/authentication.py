
from plc.core.settings import conf
from plc.core.errors import *

import os
from passlib.hash import pbkdf2_sha256 as hasher

def hashpw(pw):
    return hasher.encrypt(pw, rounds=10000, salt_size=16)

def _get_users():
    if os.path.exists(conf["server"]["users"]):
        fd = open(conf["server"]["users"])
        users = fd.readlines()
        fd.close()
    else:
        users = []
    for i in range(len(users)):
        users[i] = users[i].strip().split(":")
    return users

def _write_users(users):
    for i in range(len(users)):
        users[i] = ":".join(users[i])
    fd = open(conf["server"]["users"], "w")
    fd.write("\n".join(users))
    fd.close()

class User:
    def __init__(self, username=False, pw=False):
        self.authenticated = False
        if username:
            self.username = username
            if pw != False:
                self.set_password(pw or "")

    def login(self, user, pw):
        users = _get_users()
        for i in users:
            if i[0] == user:
                if hasher.verify(pw, i[1]):
                    self.username = user
                    self.authenticated = True
                    return True
                return False
    
    def set_password(self, pw):
        if not self.username:
            raise SecurityError("Tried to change password of non-existent user.")
        users = _get_users()
        for i in users:
            if i[0] == self.username:
                i[1] = hashpw(pw)
                _write_users(users)
                return True
        users.append([self.username, hashpw(pw)])
        _write_users(users)
