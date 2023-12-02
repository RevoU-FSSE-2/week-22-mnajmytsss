from flask import Blueprint, request
from common.bcrypt import bcrypt
from auth.models import User
from db import db
import jwt, os
from datetime import datetime, timedelta
from marshmallow import Schema, fields, ValidationError

auth_blp = Blueprint("auth", __name__)

class UserRegistrationSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    role = fields.String(required=True, validate=lambda x: x in ['admin', 'user'])

@auth_blp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    existing_user = User.query.filter_by(username=data['username']).first()

    if existing_user:
        return {"error": "username sudah digunakan"}, 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()

    return {
        'id': new_user.id,
        'username': new_user.username,
        'role': new_user.role
    }

@auth_blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": "username atau password tidak tepat"}, 400

    valid_password = bcrypt.check_password_hash(user.password, password)
    if not valid_password:
        return {"error": "username atau password tidak tepat"}, 400

    payload = {
        'username': user.username,
        'id': user.id,
        'role': user.role
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")

    return {
        'data': {
            'token': token,
            'user': {
                'username': user.username,
                'role': user.role
            }
        }
    }

