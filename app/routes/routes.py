from app import app
from app.database.SQL import db

@app.route('/', methods=['GET'])
def index():
    print(db.dbFunc())
    return "hio"