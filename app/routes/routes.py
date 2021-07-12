from app import app, cache
import app.database as db
from flask import request, Response
import app.helpers.jwt as jwt
from json import dumps


@app.route('/', methods=['GET'])
@cache.cached()
def index():
    data = db.addUser('iresharma', '123', '78 BTN')
    return f"hio{data}"


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

        # GET data according to BTN from userObj
        retData = {'user': userObject}
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
        # GET data according to Btn
        retData = {'user': userObject}
        retData['token'] = jwt.createToken(userObject)
        try:
            del retData['user']['exp']
        except KeyError:
            pass
        return Response(dumps(retData), status=200)
