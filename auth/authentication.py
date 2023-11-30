import os
from flask import request, jsonify
import jwt
from functools import wraps

def authentication_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Unauthorized"}), 401

        _, token = auth_header.split(' ')

        try:
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.current_user = decoded_token  
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function
