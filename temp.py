from pymongo import MongoClient

db = MongoClient().armyProj.villages

result = db.find({})

houses = []
for r in result:
    houses += r['houses']

print('villages', len(houses))

db = MongoClient().armyProj.houses
data = db.find({}, {'_id': 1})

hids = list(map(lambda x: x['_id'], data))

print('houses', len(hids))

# find the difference in two list
diff = list(set(hids) - set(houses))

print(diff)