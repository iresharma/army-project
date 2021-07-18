from app import app, cache
import app.database as db
from flask import request, Response
import app.helpers.jwt as jwt
from json import dumps
import app.helpers.decorators as decorators
from app.helpers.caching import cache_key


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
@app.route('/coy')
@decorators.jwtChecker
@cache.cached(key_prefix=cache_key)
def coy(userObject: dict):
    try:
        if request.args.get("type") != None and request.args.get("coyName") != None:
            result = db.getCoyByName(userObject["btn"], request.args.get("type"), request.args.get("coyName"))
        else:
            result = db.getCoyList(userObject["btn"])

        if len(result) == 0:
            return Response(dumps({"error": "No collection found"}), status=400)
        return Response(dumps({"data":result}), status=200)
    except:
        return Response(dumps({"error": "Something went wrong"}), status=500)