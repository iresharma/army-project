from pymongo import MongoClient
from app.constants import DATABASE_NAME
from datetime import datetime as dt
from hashlib import sha256

client = MongoClient()
db = client[DATABASE_NAME]

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
#     return user


def loginUser(username: str, password: str) -> dict:
    user = db.users.find_one({"username": username})
    passW = sha256(password.encode()).hexdigest()
    if passW == user['password']:
        del user['password']
        user["_id"] = str(user["_id"])
        return user
    else:
        raise ValueError


def sendCount(btn: str) -> dict:
    filter = {"btn": btn}
    return {
        "villages": db.villages.count_documents(filter),
        "mohallas": db.mohallas.count_documents(filter),
        "houses": db.houses.count_documents(filter),
        # 
    }


def getGeoLocation(btn: str, type=None, id=None) -> list:
    fields = {
            "houseNumber": 1,
            "village": 1,
            "mohalla": 1,
            "geo": 1,
            "colour": 1,
            "entryPoints": 1,
            "husband": 1,
        }
    if type is None and id is None:
        result = db.houses.find({"btn": btn, '_id': 'f802ab303ad048c9a4aa3616162fcab9'}, fields)
    else:
        result = db.houses.find({"btn": btn, type: id}, fields)
    return list(result)


def listVillages(coy: str, btn: str) -> list:
    result = db.villages.find({"btn": btn, "coy": coy})
    return list(result)


def listMohalla(coy: str, btn: str) -> list:
    result = db.mohallas.find({"btn": btn, "coy": coy})
    return list(result)


def listHouse(coy: str, btn: str) -> list:
    result = db.houses.find({"btn": btn, "coy": coy})
    return list(result)

# addUser('iresharma', '123', '78 BN')
