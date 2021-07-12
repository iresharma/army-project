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

print(data[0])

from pymongo import MongoClient

client = MongoClient()
db = client.armyPorj
dbData = db.data

dbData.insert_many(data)