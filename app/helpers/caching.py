from flask import request

def cache_key():
    """
    Generate a cache key for the current request.
    """
    return request.url