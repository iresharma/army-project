from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_REDIS_HOST": "127.0.0.1", # Redis host running on local
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
CORS(app)

from app.routes import routes