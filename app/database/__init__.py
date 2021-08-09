from os import error
from pymongo import MongoClient,errors
from app.constants import DATABASE_NAME, MONGO_URI
from datetime import datetime as dt
from hashlib import sha256
from bson.objectid import ObjectId

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# iresharma, 123


def addUser(username: str, password: str, btn: str) -> dict:
    passW = sha256(password.encode()).hexdigest()
    user = {
        'username': username,
        'password': passW,
        'btn': btn,
        'createdAt': dt.now().timestamp(),
    }

    userId = db['users'].insert_one(user)
    user["_id"] = str(userId.inserted_id)
    user.pop("password")
    return user


def loginUser(username: str, password: str) -> dict:
    user = db.users.find_one({"username": username})
    print(user)
    if user == None:
        raise ValueError
    passW = sha256(password.encode()).hexdigest()
    print(passW)
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


def getGeoLocation(btn: str, queryType=None, value=None) -> list:
    fields = {
        "houseNumber": 1,
        "village": 1,
        "mohalla": 1,
        "geo": 1,
        "colour": 1,
        "entryPoints": 1,
        "husband": 1,
    }
    if queryType is None and value is None:
        result = db.houses.find({"btn": btn}, fields)
    else:
        result = db.houses.find({"btn": btn, queryType: value}, fields)
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


# COY database functions
def getCoyList(btn: str, coyName: str = None) -> list:
    filter = {"btn": btn}
    if coyName != None:
        filter["coy"] = coyName
    try:
        result = db.villages.aggregate([
            {
                "$match": filter
            },
            {
                "$group": {"_id": "$coy",
                           "villagesCount": {"$sum": 1},
                           "mohallasCount": {"$sum": {"$size": "$mohalla"}},
                           "housesCount": {"$sum": {"$size": "$houses"}}
                           }
            },
        ])
        return list(result)
    except Exception as e:
        print(e)
        raise e


def getCoyByName(btn: str, queryType: str, coyName: str) -> list:
    try:
        result = db[queryType].find({"coy": coyName, "btn": btn})
        return list(result)
    except Exception as e:
        print(e)
        raise e

# Houses database functions


def updateHouse(id: str, updateQuery: object) -> dict:
    try:
        result = db.houses.update_one({"_id": ObjectId(id)},
                                      {"$set": updateQuery})
        return result
    except Exception as e:
        print(e)
        raise e


def getVillageList(btn: str, coy: str = None) -> list:
    filter = {"btn": btn}
    if coy != None:
        filter["coy"] = coy
    try:
        result = db.villages.aggregate([{"$match": filter}, {"$group": {"_id": "$village", "coy": {"$addToSet": "$coy"}, "houseCount": {
                                       "$sum": {"$size": "$houses"}}, "mohallaCount": {"$sum": {"$size": "$mohalla"}}}}, {"$unwind": "$coy"}])
    except Exception as e:
        print(e)
        return e

    return list(result)


def getMohallaList(btn: str, village: str = None) -> list:
    filter = {"btn": btn}
    if village != None:
        filter["village"] = village
    try:
        result = db.mohallas.aggregate([{"$match": filter}, {"$group": {"_id": "$mohalla", "village": {
                                       "$addToSet": "$village"}, "houseCount": {"$sum": {"$size": "$houses"}}}}, {"$unwind": "$village"}])
    except Exception as e:
        print(e)
        return e

    return list(result)


def getHouseList(btn: str, mohalla: str = None) -> list:
    filter = {"btn": btn}
    if mohalla != None:
        filter["mohalla"] = mohalla
    try:
        result = db.houses.aggregate([{"$lookup": {"from": "people", "localField": "husband", "foreignField": "_id", "as": "husbandDocument"}}, {
                                     "$unwind": "$husbandDocument"}, {"$project": {"husband": 0}}])
    except Exception as e:
        print(e)
        return e

    return list(result)



def markPersonAsSuspect(id: str, suspectObject: object) -> dict:
    try:
        result = db.people.update_one({"_id": id},
            {"$set": {"suspect":{
                    "status": suspectObject['status'],
                    "data": suspectObject['data'] if suspectObject['status'] else None
                 }}})
        return result
    except Exception as e:
        print(e)
        raise e

        
def exportDataAsCSV(btn: str) -> dict:
    try:
        result = db.houses.find({"btn": btn})
        houses = list(result)
        data = ["".join(['Bn', 'COY', 'Village', 'Mohalla', 'House No', 'Name', 'Relation', 'Sex', 'Age', 'Occupation', 'Mob No',
                'GR', 'Property', 'Floor', 'Colour', 'No of Rooms', 'Perimeter Fence', 'Cowshed', 'Entry points', 'LAT/LONG'])]
        for i in houses:
            if i['father']:
                father = db.people.find_one({"_id": i['father']})
                data.append(f"{i['btn']},{i['coy']},{i['village']},{i['mohalla']},{i['house']},{father['name']},father,{father['sex']},{father['age']},{father['occupation']},{father['tel']},{i['GR']},{i['property']},{i['floor']},{i['colour']},{i['nRooms']},{i['perimeterfence']},{i['cowshed']},{i['entryPoints']},{i['geo']['lat']}/{i['geo']['long']}")
            elif i['husband']:
                husband = db.people.find_one({"_id": i['husband']})
                data.append(f"{i['btn']},{i['coy']},{i['village']},{i['mohalla']},{i['house']},{husband['name']},husband,{husband['sex']},{husband['age']},{husband['occupation']},{husband['tel']},{i['GR']},{i['property']},{i['floor']},{i['colour']},{i['nRooms']},{i['perimeterfence']},{i['cowshed']},{i['entryPoints']},{i['geo']['lat']}/{i['geo']['long']}")
            elif i['wife']:
                wife = db.people.find_one({"_id": i['wife']})
                data.append(f"{i['btn']},{i['coy']},{i['village']},{i['mohalla']},{i['house']},{wife['name']},wife,{wife['sex']},{wife['age']},{wife['occupation']},{wife['tel']},{i['GR']},{i['property']},{i['floor']},{i['colour']},{i['nRooms']},{i['perimeterfence']},{i['cowshed']},{i['entryPoints']},{i['geo']['lat']}/{i['geo']['long']}")
            elif i['son']:
                son = db.people.find_one({"_id": i['son']})
                data.append(f"{i['btn']},{i['coy']},{i['village']},{i['mohalla']},{i['house']},{son['name']},son,{son['sex']},{son['age']},{son['occupation']},{son['tel']},{i['GR']},{i['property']},{i['floor']},{i['colour']},{i['nRooms']},{i['perimeterfence']},{i['cowshed']},{i['entryPoints']},{i['geo']['lat']}/{i['geo']['long']}")
            elif i['daughter']:
                daughter = db.people.find_one({"_id": i['daughter']})
                data.append(f"{i['btn']},{i['coy']},{i['village']},{i['mohalla']},{i['house']},{daughter['name']},daughter,{daughter['sex']},{daughter['age']},{daughter['occupation']},{daughter['tel']},{i['GR']},{i['property']},{i['floor']},{i['colour']},{i['nRooms']},{i['perimeterfence']},{i['cowshed']},{i['entryPoints']},{i['geo']['lat']}/{i['geo']['long']}")
        with open('export.csv', 'w') as csvFile:
            csvFile.write('\n'.join(data))
        return 'hi'
    except Exception as e:
        print(e)
        raise e

       

def getPerson(request: object) -> dict:
    filter = {}
    filter["name"] = {"$regex": request["name"], "$options": "i"} if request["name"] != None else None
    try:
        result = db.people.find(filter)
        return list(result)
    except Exception as e:
        print(e)
        raise e