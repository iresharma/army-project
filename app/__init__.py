from os import environ
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from app.constants import CACHE_DEFAULT_TIMEOUT


config = {
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    # !================================================================
    # ! Uncomment the below line to minimize caching to 5secs
    # !================================================================
    # "CACHE_DEFAULT_TIMEOUT": 5,
    # "CACHE_REDIS_HOST": "127.0.0.1", # Redis host running on local
    "CACHE_REDIS_URL": environ.get("REDIS_URL", "redis://localhost:6379/0")
}

try:
    if environ["PY_ENV"] == "development":
        config["DEBUG"] = True
        config["CACHE_DEFAULT_TIMEOUT"] = 0
except:
    pass

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
CORS(app)

from app.routes import routes