import os
from flask import Flask
from db import db, db_init
from common.bcrypt import bcrypt
from auth.apis import auth_blp
from lists.apis import list_bp
from flask_cors import CORS
from flask_talisman import Talisman

app = Flask(__name__)

CORS(app)
Talisman(app)

database_url = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(auth_blp, url_prefix="/auth")
app.register_blueprint(list_bp, url_prefix="/api/v1")


# with app.app_context():
#     db_init() 
