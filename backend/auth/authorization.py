from functools import wraps
from flask import request, jsonify
import jwt

def authorization_middleware(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"error": "Unauthorized"}), 401

            _, token = auth_header.split(' ')

            try:
                decoded_token = jwt.decode(token, 'your_secret_key_here', algorithms=["HS256"])

                if decoded_token.get('role') in allowed_roles:
                    request.current_user = decoded_token  # You can customize this to store user information
                    return f(*args, **kwargs)
                else:
                    return jsonify({"error": "Unauthorized"}), 401

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError as e:
                return jsonify({"error": str(e)}), 401

        return decorated_function

    return decorator
