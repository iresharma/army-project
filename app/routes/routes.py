from app import app, cache
import app.database as db
from flask import request, Response
import app.helpers.jwt as jwt
from json import dumps
import app.helpers.decorators as decorators


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
@cache.cached()
def geo(userObject: dict):
    result = db.getGeoLocation(userObject["btn"])
    return Response(dumps(result), status=200)


# TODO : add count of everything in the json

# Route to get data about specific company(coy)
@app.route('/coy')
@decorators.jwtChecker
@cache.cached()
def coy(userObject: dict):
    if type == 'village':
        result = db.listVillages(coy.replace('+', ' '), userObject['btn'])
        return Response(dumps(result), status=200)
    elif type == 'mohalla':
        result = db.listMohalla(coy.replace('+', ' '), userObject['btn'])
        return Response(dumps(result), status=200)
    elif type == 'house':
        result = db.listHouse(coy.replace('+', ' '), userObject['btn'])
        return Response(dumps(result), status=200)