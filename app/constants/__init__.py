from os import environ

DATABASE_NAME = "armyProj"
JWT_SECRET_KEY = "army_pr0j"
CACHE_DEFAULT_TIMEOUT = 300
MONGO_URI = environ.get("MONGO_URI", None)