from pymongo import MongoClient

db = MongoClient().armyProj

result = db.villages.find_one({
    "village": "Devgarh"
})

noneCount, actualCount = 0, 0

for i in result['mohalla']:
    res = db.mohallas.find_one({"_id": i})
    if res == None:
        noneCount += 1
    else:
        print(res['mohalla'])
        actualCount += 1

# print counts
print("None: " + str(noneCount) + " Actual: " + str(actualCount))