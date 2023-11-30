import os
from flask import Blueprint, request, jsonify
from auth.authentication import authentication_middleware
from lists.models import db, List
import jwt
from datetime import datetime

list_bp = Blueprint("list", __name__)

@list_bp.route("/lists", methods=["POST"])
@authentication_middleware
def create_list():
    data = request.get_json()
    print(data)
    title = data.get('title')
    priority_value = data.get('priority')
    status_value = data.get('status')
    dueDate = data.get('dueDate')  

    valid_priority = ['high', 'medium', 'low']
    valid_statuses = ['to do', 'on progress', 'done']

    if priority_value not in valid_priority:
        return jsonify({"message": "Invalid priority value. Allowed values are high, medium, and low.", "success": False}), 400

    if status_value not in valid_statuses:
        return jsonify({"message": "Invalid status value. Allowed values are to do, on progress, and done.", "success": False}), 400

    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        print(decoded)
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_list = List(
            username=decoded['username'],
            title=title,
            priority=priority_value,
            status=status_value,
            dueDate=dueDate,
            date=current_date
        )

        db.session.add(new_list)
        db.session.commit()

        return jsonify({
            "message": "Successfully added List to do",
            "data": {
                "id": new_list.id,
                "title": new_list.title,  
                "priority": new_list.priority,
                "status": new_list.status,
                "createdAt": new_list.date.strftime('%Y-%m-%d'),  
                "dueDate": new_list.dueDate,  
            },
            "success": True
            }), 201
    except Exception as error:
        print(error)
        return jsonify({"message": str(error) or 'Internal Server Error', "success": False}), 500

@list_bp.route("/lists", methods=["GET"])
@authentication_middleware
def get_all_list():
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])

        if decoded['role'] == 'admin':
            user_lists = List.query.all()
        elif decoded['role'] == 'user':
            user_lists = List.query.filter_by(username=decoded['username']).all()
            print(decoded['role'])

        response_data = [{"id": lst.id, "title": lst.title, "priority": lst.priority, "status": lst.status, "dueDate": lst.dueDate, "date": lst.date} for lst in user_lists]
        
        return jsonify({
            "message": "Successfully retrieved user lists",
            "data": response_data,
            "success": True
        }), 200
    except Exception as error:
        print(error)
        return jsonify({"message": str(error) or 'Internal Server Error', "success": False}), 500

@list_bp.route("/lists/<id>", methods=["PUT"])
@authentication_middleware
def update_list(id):
    data = request.get_json()
    priority_value = data.get('priority')
    status_value = data.get('status')

    valid_properties = ['high', 'medium', 'low']
    valid_statuses = ['to do', 'on progress', 'done']

    if priority_value and priority_value not in valid_properties:
        return jsonify({"message": "Invalid priority value. Allowed values are high, medium, and low.", "success": False}), 400

    if status_value and status_value not in valid_statuses:
        return jsonify({"message": "Invalid status value. Allowed values are to do, on progress, and done.", "success": False}), 400

    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        list_item = List.query.filter_by(id=id, username=decoded['username']).first()

        if not list_item:
            return jsonify({"message": "List not found or you do not have permission to update it.", "success": False}), 404

        if priority_value:
            list_item.priority = priority_value

        if status_value:
            list_item.status = status_value

        list_item.date = current_date
        db.session.commit()

        return jsonify({
                "message": "Successfully updated list",
                "data": {
                    "id": list_item.id,
                    "title": list_item.title,
                    "priority": list_item.priority,
                    "status": list_item.status,
                    "dueDate": list_item.dueDate,
                    "date": list_item.date
                },
                "success": True
            }), 200
    except Exception as error:
        print(error)
        return jsonify({"message": str(error) or 'Internal Server Error', "success": False}), 500

@list_bp.route("/lists/<id>", methods=["DELETE"])
@authentication_middleware
def delete_list(id):
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])

        list_item = List.query.filter_by(id=id).first()

        if not list_item:
            return jsonify({"message": "List not found", "success": False}), 404

        if decoded['role'] == 'admin':
            return jsonify({"message": "Admins are not allowed to delete lists", "success": False}), 403
        elif decoded['role'] == 'user':
            if list_item.username != decoded['username']:
                return jsonify({"message": "You do not have permission to delete this list", "success": False}), 403

        db.session.delete(list_item)
        db.session.commit()

        return jsonify({
                "message": "Successfully deleted",
                "success": True
            }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired", "success": False}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token", "success": False}), 401
    except Exception as error:
        print(error)
        return jsonify({"message": str(error) or 'Internal Server Error', "success": False}), 500
