from app import db
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import exists

from .middleware import token_auth
from .models import Todo, User

api = Blueprint('api', __name__)


@api.route('/signin', methods=['POST'])
def signin():
    request_body = request.get_json()
    username = request_body.get('username')
    password = request_body.get('password')

    if not username:
        return jsonify(message='Username is missing.'), 400

    if not password:
        return jsonify(message='Password is missing.'), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify(message='Username does not exist.'), 404

    if not user.check_password(password):
        return jsonify(message='Incorrect password.'), 401

    return jsonify(token=user.generate_jwt()), 200


@api.route('/signup', methods=['POST'])
def signup():
    request_body = request.get_json()
    username = request_body.get('username')
    password = request_body.get('password')
    password_confirm = request_body.get('password_confirm')

    if not username:
        return jsonify(message='Username is missing.'), 400

    if not password:
        return jsonify(message='Password is missing.'), 400

    if not password_confirm:
        return jsonify(message='Password confirm is missing.'), 400

    if password != password_confirm:
        return jsonify(message='Password and password confirm do not match.'), 400

    user_exists = db.session.query(
        exists().where(User.username == username)).scalar()

    if user_exists:
        return jsonify(message='Username is already taken.'), 400

    user = User(username=username,
                password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify(token=user.generate_jwt()), 201


@api.route('/todo/<int:todo_id>', methods=['DELETE'])
@token_auth.login_required
def delete_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify(message='Todo not found.'), 404

    if todo.user_id != g.user_id:
        return jsonify(message='Unauthorized.'), 401

    db.session.delete(todo)
    db.session.commit()

    return jsonify(), 200


@api.route('/todo/<int:todo_id>', methods=['PUT'])
@token_auth.login_required
def update_todo(todo_id):
    request_body = request.get_json()
    text = request_body.get('text')
    is_completed = request_body.get('is_completed')

    if is_completed is None:
        return jsonify(message='Completed is missing.'), 400

    if not text:
        return jsonify(message='Text is missing.'), 400

    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify(message='Todo not found.'), 404

    if todo.user_id != g.user_id:
        return jsonify(message='Unauthorized.'), 401

    todo.text = text
    todo.is_completed = is_completed
    db.session.commit()

    return jsonify(id=todo_id, text=text, is_completed=is_completed), 200


@api.route('/todos', methods=['GET'])
@token_auth.login_required
def get_todos():
    todos = [todo.as_dict()
             for todo in Todo.query.filter_by(user_id=g.user_id)]
    return jsonify(todos=todos), 200


@api.route('/todos', methods=['POST'])
@token_auth.login_required
def create_todo():
    request_body = request.get_json()
    text = request_body.get('text')

    if not text:
        return jsonify(message='Text is missing.'), 400

    todo = Todo(text=text, user_id=g.user_id)
    db.session.add(todo)
    db.session.commit()

    return jsonify(id=todo.id, text=todo.text), 201
