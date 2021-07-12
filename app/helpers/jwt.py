import jwt
from app.constants import JWT_SECRET_KEY
import datetime as dt

def createToken(userObj: dict) -> str:
    exp = dt.datetime.utcnow() + dt.timedelta(days=14)
    userObj['exp'] = exp
    return jwt.encode(userObj, JWT_SECRET_KEY, algorithm="HS256")

def verifyToken(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        print("Invalid signature")
        raise KeyError
    except jwt.ExpiredSignatureError:
        print("Expired signature")
        raise PermissionError
    except Exception as e:
        print(e)
        raise e