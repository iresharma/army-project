from os import error
from pymongo import MongoClient, errors
from app.constants import DATABASE_NAME, MONGO_URI
from datetime import datetime as dt
from hashlib import sha256
from bson.objectid import ObjectId
from certifi import where
from uuid import uuid4

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# iresharma, 123


def rowTodict(array) -> list:
    data = []
    for ind, i in array.iterrows():
        doc = {
            "Bn": i[0],
            "coy": i[1],
            "village": i[2],
            "mohalla": i[3],
            "Hnum": i[4],
            "name": i[5],
            "relation": i[6],
            "sex": i[7],
            "age": i[8],
            "occupation": i[9],
            "tel": i[10],
            "GR": i[11],
            "property": i[12],
            "floor": i[13],
            "colour": i[14],
            "nRooms": i[15],
            "perimeterfence": i[16],
            "cowshed": i[17],
            "entryPoints": i[18],
            "geo": {
                "lat": i[19].split("/")[0],
                "long": i[19].split("/")[1][:-1],
            },
        }
        data.append(doc)
    return data


def fileDataToClassifiedData(data: list) -> dict:
    houses = []
    villages = []
    mohallas = []

    houseDocs = []
    mohallaDocs = []
    villageDocs = []
    people = []

    for i in data:
        hid = str(uuid4()).replace('-', '')
        mid = str(uuid4()).replace('-', '')
        vid = str(uuid4()).replace('-', '')
        pid = str(uuid4()).replace('-', '')

        # create house doc
        if i['Hnum'] not in houses:
            houses.append(i['Hnum'])
            doc = {
                "_id": hid,
                "house": i["Hnum"],
                "btn": i["Bn"],
                "coy": i["coy"],
                "village": i["village"],
                "mohalla": i["mohalla"],
                "property": i['property'],
                "floor": i['floor'],
                "nRooms": i['nRooms'],
                "GR": i["GR"],
                "colour": i["colour"],
                "perimeterfence": True if i["perimeterfence"] == 'Y' or i["perimeterfence"] == 'y' else False,
                "cowshed": True if i["cowshed"] == 'Y' or i["cowshed"] == 'y' else False,
                "entryPoints": i['entryPoints'],
                "geo": {
                    "lat": i['geo']['lat'],
                    "long": i['geo']['long'],
                },
                "mother": None,
                "father": None,
                "daughter": None,
                "son": None,
                "husband": None,
                "wife": None
            }
            people.append({
                "_id": pid,
                "name": i['name'],
                "age": i['age'],
                "sex": i['sex'],
                "occupation": i['occupation'],
                "tel": i['tel'],
                "hid": hid,
            })
            doc[i['relation'].lower()] = pid
            houseDocs.append(doc)

            # create mohalla document
            if i['mohalla'] not in mohallas:
                mohallas.append(i['mohalla'])
                doc = {
                    "_id": mid,
                    "btn": i['Bn'],
                    "coy": i['coy'],
                    "village": i['village'],
                    "mohalla": i['mohalla'],
                    "houses": [hid]
                }
                mohallaDocs.append(doc)

                # create village document
                if i['village'] not in villages:
                    villages.append(i['village'])
                    doc = {
                        "_id": vid,
                        "btn": i['Bn'],
                        "coy": i['coy'],
                        "village": i['village'],
                        "houses": [hid],
                        "mohalla": [mid],
                    }
                    villageDocs.append(doc)
                else:
                    index = villages.index(i['village'])
                    villageDocs[index]['houses'].append(hid)
                    villageDocs[index]['mohalla'].append(mid)
            else:
                index = mohallas.index(i['mohalla'])
                mohallaDocs[index]['houses'].append(hid)
                if i['village'] not in villages:
                    villages.append(i['village'])
                    doc = {
                        "_id": vid,
                        "btn": i['Bn'],
                        "coy": i['coy'],
                        "village": i['village'],
                        "houses": [hid],
                        "mohalla": [mohallaDocs[index]['_id']],
                    }
                    villageDocs.append(doc)
                else:
                    index = villages.index(i['village'])
                    villageDocs[index]['houses'].append(hid)
                    if mohallaDocs[index]['village'] == villageDocs[index]['village']:
                        villageDocs[index]['mohalla'].append(
                            mohallaDocs[index]['_id'])
                        villageDocs[index]['mohalla'] = list(
                            set(villageDocs[index]['mohalla']))
        else:
            index = houses.index(i['Hnum'])
            person = {
                "_id": pid,
                "name": i['name'],
                "age": i['age'],
                "sex": i['sex'],
                "occupation": i['occupation'],
                "tel": i['tel'],
                "hid": houseDocs[index]["_id"]
            }
            people.append(person)
            houseDocs[index][i['relation'].lower()] = pid
    return {
        'houses': houseDocs,
        'villages': villageDocs,
        'mohallas': mohallaDocs,
        'people': people
    }


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


def fillDB(data: list):
    objArray = rowTodict(data)
    classifiedData = fileDataToClassifiedData(objArray)
    result = db.people.insert_many(classifiedData['people'])
    print(len(result.inserted_ids))

    result = db.houses.insert_many(classifiedData['houses'])
    print(len(result.inserted_ids))

    result = db.mohallas.insert_many(classifiedData['mohallas'])
    print(len(result.inserted_ids))

    result = db.villages.insert_many(classifiedData['villages'])
    print(len(result.inserted_ids))
    return


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
        result = db.houses.aggregate([{"$match": filter}, {"$lookup": {"from": "people", "localField": "husband", "foreignField": "_id", "as": "husbandDocument"}}, {
                                     "$unwind": "$husbandDocument"}, {"$project": {"husband": 0}}])
    except Exception as e:
        print(e)
        return e

    return list(result)


def markPersonAsSuspect(id: str, suspectObject: object) -> dict:
    try:
        result = db.people.update_one({"_id": id},
                                      {"$set": {"suspect": {
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


def getPerson(request: dict) -> dict:
    filter = {}
    filter["name"] = {"$regex": request["name"],
                      "$options": "i"} if "name" in request.keys() else None
    filter["occupation"] = {"$regex": request["occupation"],
                            "$options": "i"} if "occupation" in request.keys() else None
    filter["tel"] = {"$regex": request["tel"],
                     "$options": "i"} if "tel" in request.keys() else None
    try:
        result = db.people.aggregate([{"$lookup": {"from": "houses", "localField": "hid", "foreignField": "_id", "as": "house"}}, {
                                     "$match": filter}, {"$unwind": "$house"}, {"$project": {"hid": 0}}])
        return list(result)
    except Exception as e:
        print(e)
        raise e


def insertPerson(request: dict) -> dict:
    newPerson = {}
    try:
        newPerson["name"] = request["name"]
        newPerson["age"] = request["age"]
        newPerson["sex"] = request["sex"]
        newPerson["occupation"] = request["occupation"]
        newPerson["tel"] = request["tel"]
        newPerson["hid"] = request["hid"] if "hid" in request.keys() else None
    except Exception as e:
        raise e
    try:
        result = db.people.insert_one(newPerson)
        return result
    except Exception as e:
        raise e


def insertHouse(request: dict) -> dict:
    newHouse = {}
    try:
        newHouse["house"] = request["house"]
        newHouse["btn"] = request["btn"]
        newHouse["coy"] = request["coy"]
        newHouse["village"] = request["village"]
        newHouse["mohalla"] = request["mohalla"]
        newHouse["property"] = request["property"]
        newHouse["floor"] = request["floor"]
        newHouse["nRooms"] = request["nRooms"]
        newHouse["GR"] = request["GR"]
        newHouse["colour"] = request["colour"]
        newHouse["perimeterfence"] = request["perimeterfence"]
        newHouse["cowshed"] = request["cowshed"]
        newHouse["entryPoints"] = request["entryPoints"]
        newHouse["geo"] = request["geo"]
    except Exception as e:
        raise e
    try:
        if request['relatives'] == None:
            raise TypeError('relatives not found')
        for relative, data in request['relatives'].items():
            if data != None:
                newPersonId = insertPerson(data)
                newHouse[relative] = str(newPersonId.inserted_id)
            else:
                newHouse[relative] = None
    except Exception as e:
        raise e
    try:
        result = db.houses.insert_one(newHouse)
    except Exception as e:
        raise e
    try:
        for relative, data in request['relatives'].items():
            if data != None:
                db.people.update_one({"_id": ObjectId(newHouse[relative])}, {
                                     "$set": {"hid": str(result.inserted_id)}})
    except Exception as e:
        raise e
    return str(result.inserted_id)
