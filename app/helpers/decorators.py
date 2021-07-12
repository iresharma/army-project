from functools import wraps
from app.helpers.jwt import verifyToken
from flask import request, Response


def jwtChecker(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Auth' not in request.headers:
            return Response('Auth header missing', status=400)

        token = request.headers.get('Auth')
        try:
            userObject = verifyToken(token)
        except KeyError:
            return Response('Invalid Signature', status=403)
        except PermissionError:
            return Response('Token Expired Please log in again', status=401)
        except Exception as e:
            print(e)
            return Response('Internal server error', status=500)

        return f(*args, **kwargs, userObject=userObject)
    return wrapper