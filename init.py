import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__))
                                                                    + '\\database.sqlite')

db = SQLAlchemy(app, session_options={'autocommit': False})

f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/config/", "config.json"), "r")
config = json.loads(f.read())

from main_routes import *

if __name__ == '__main__':
    app.secret_key = utils.generate_salt()
    db.create_all()
    app.run(port=config["port"], host=config["ip"])

