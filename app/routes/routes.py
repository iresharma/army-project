from app import app, cache
import app.database as db
from flask import request, Response
import app.helpers.jwt as jwt
from json import dumps
import app.helpers.decorators as decorators
from app.helpers.caching import cache_key

@app.after_request
def apply_caching(response):
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/")
def index():
    return Response(dumps({"message": "Hello, World!"}), mimetype="application/json", status=200)

@app.route("/createUser")
def create_user():
    x = db.addUser("test", "test", "78 BN")
    return Response(dumps({"user": x}), mimetype="application/json", status=200)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        if 'Auth' not in request.headers:
            return Response('Auth header missing', status=400)

        token = request.headers.get('Auth')
        try:
            userObject = jwt.verifyToken(token)
        except KeyError:
            return Response('Invalid Signature', status=403)
        except PermissionError:
            return Response('Token Expired Please log in again', status=401)
        except Exception as e:
            print(e)
            return Response('Internal server error', status=500)

        retData = {'user': userObject}
        retData['data'] = db.sendCount(userObject["btn"])
        retData['token'] = jwt.createToken(userObject)
        try:
            del retData['user']['exp']
        except KeyError:
            pass

        return Response(dumps(retData), status=200)

    elif request.method == 'POST':
        json = request.json
        try:
            userObject = db.loginUser(json['username'], json['password'])
        except ValueError:
            return Response('Invalid credentials', status=400)
        retData = {'user': userObject}
        retData['data'] = db.sendCount(userObject["btn"])
        retData['token'] = jwt.createToken(userObject)
        try:
            del retData['user']['exp']
        except KeyError:
            pass
        return Response(dumps(retData), status=200)

# Route to get all lat longs

@app.route('/geo')
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def geo(userObject: dict):
    try:
        result = db.getGeoLocation(userObject["btn"], queryType=request.args.get('type'), value=request.args.get('value'))
        if result == []:
                return Response(dumps({'error': "No collection found"}), status=400)
        return Response(dumps({"data":result}), status=200)
    except:
        return Response(dumps({"error": "Something went wrong"}), status=500)

# TODO : add count of everything in the json

# Route to get data about specific company(coy)
@app.route('/coy', methods=['GET'])
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def coy(userObject: dict):
    try:
        if request.args.get("type") != None and request.args.get("coyName") != None:
            result = db.getCoyByName(userObject["btn"], request.args.get("type"), request.args.get("coyName"))
            coyList = db.getCoyList(userObject["btn"], request.args.get("type"))
            if len(result) == 0:
                return Response(dumps({"error": "No collection found"}), status=400)
            return Response(dumps({"data":{"coy":coyList, "documents": result}}), status=200)
        else:
            coyList = db.getCoyList(userObject["btn"])
            return Response(dumps({"data":{"coy":coyList}}), status=200)
    except Exception as e:
        print(e)
        return Response(dumps({"error": "Something went wrong"}), status=500)



# Route for village
@app.route('/village', methods=['GET'])
@decorators.jwtChecker
# @cache.cached(key_prefix=cache_key)
def village(userObject: dict):
    try:
        result = db.getVillageList(userObject["btn"], request.args.get("coyName"))
        if len(result) == 0:
            return Response(dumps({"error": "Village not found"}), status=400)
        return Response(dumps({"data":result}), status=200)
    except Exception as e:
        print(e)
        return Response(dumps({"error": "Something went wrong"}), status=500)


# Route for mohalla
@app.route('/mohalla', methods=['GET'])
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def mohalla(userObject: dict):
    try:
        result = db.getMohallaList(userObject["btn"], request.args.get("villageName"))
        if len(result) == 0:
            return Response(dumps({"error": "Mohalla not found"}), status=400)
        return Response(dumps({"data":result}), status=200)
    except Exception as e:
        print(e)
        return Response(dumps({"error": "Something went wrong"}), status=500)


# Route for house
@app.route('/house', methods=['GET'])
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def house(userObject: dict):
    try:
        result = db.getHouseList(userObject["btn"], request.args.get("mohallaName"))
        if len(result) == 0:
            return Response(dumps({"error": "House not found"}), status=400)
        return Response(dumps({"data":result}), status=200)
    except Exception as e:
        print(e)
        return Response(dumps({"error": "Something went wrong"}), status=500)

# Route to get data about specific company(coy)
@app.route('/house/<id>', methods=["PUT"])
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def updateHouse(userObject: dict, id: str):
    if request.method == "POST":
        try:
            result = db.updateHouse(id, request.json)
            return Response(dumps({"data":result}), status=200)
        except:
            return Response(dumps({"error": "Something went wrong"}), status=500)


@app.route('/csv', methods=['GET'])
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def csv(userObject: dict):
    try:
        result = db.exportDataAsCSV(userObject["btn"])
        return Response(dumps({"data":result}), status=200)
    except Exception as e:
        print(e)
        return Response(dumps({"error": "Something went wrong"}), status=500)
    return Response(dumps({"data": "File exported"}), status=200)
        
