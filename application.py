from app import app as application
from os import environ
if __name__ == '__main__':
    application.run(debug=environ.get("DEBUG", False), port=environ.get("PORT", 5000))