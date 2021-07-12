from pymongo import MongoClient
from app.constants import DATABASE_NAME
from datetime import datetime as dt
from hashlib import sha256

client = MongoClient()
db = client[DATABASE_NAME]
dbUsers = db.users

# iresharma, 123

# def addUser(username: str, password: str, btn: str) -> dict:
#     passW = sha256(password.encode()).hexdigest()
#     user = {
#         'username': username,
#         'password': passW,
#         'btn': btn,
#         'createdAt': dt.now().timestamp(),
#     }

#     userId = db['users'].insert_one(user)
#     print(userId)
#     return user

def loginUser(username: str, password: str) -> dict:
    user = dbUsers.find_one({"username": username})
    passW = sha256(password.encode()).hexdigest()
    if passW == user['password']:
        del user['password']
        user["_id"] = str(user["_id"])
        return user
    else:
        raise ValueError