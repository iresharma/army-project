from app import app as application
from os import environ
from flask import request

@application.before_request
def before_request():
    print(request.headers)
if __name__ == '__main__':
    application.run(debug=environ.get("DEBUG", True), port=environ.get("PORT", 5000))