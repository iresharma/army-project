from pymongo import MongoClient
from bson.dbref import DBRef
from uuid import uuid4
from json import dumps
data = []

with open('DATABASE.csv', 'r') as fileData:
    for line in fileData.readlines()[1::]:
        i = line.split(',')
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
        })
        doc[i['relation'].lower()] = DBRef('people', pid)
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
                "houses": [DBRef('houses', hid)]
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
                    "houses": [DBRef('houses', hid)],
                    "mohalla": [DBRef('mohalla', mid)],
                }
                villageDocs.append(doc)
            else:
                index = villages.index(i['village'])
                villageDocs[index]['houses'].append(DBRef('houses', hid))
                villageDocs[index]['mohalla'].append(DBRef('mohalla', mid))
        else:
            index = mohallas.index(i['mohalla'])
            mohallaDocs[index]['houses'].append(DBRef('houses', ''))
    else:
        index = houses.index(i['Hnum'])
        person = {
            "_id": pid,
            "name": i['name'],
            "age": i['age'],
            "sex": i['sex'],
            "occupation": i['occupation'],
            "tel": i['tel'],
        }
        people.append(person)
        houseDocs[index][i['relation'].lower()] = DBRef('people', pid)


print(f"houses - {len(houses)}")
print(f"mohallas - {len(mohallas)}")
print(f"villages - {len(villages)}")
print(f"people - {len(people)}")

print("printing first elements to check db struct")

# print(f"houses - {dumps(houseDocs[0], indent=4)}")
# print(f"mohallas - {dumps(mohallaDocs[0], indent=4)}")
# print(f"villages - {dumps(villageDocs[0], indent=4)}")

db = MongoClient().armyProj

result = db.people.insert_many(people)
print(len(result.inserted_ids))

result = db.houses.insert_many(houseDocs)
print(len(result.inserted_ids))

result = db.mohallas.insert_many(mohallaDocs)
print(len(result.inserted_ids))

result = db.villages.insert_many(villageDocs)
print(len(result.inserted_ids))
