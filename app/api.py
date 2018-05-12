import jwt

from app import db
from flask import Blueprint, current_app, g, jsonify, request
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import exists

from .models import Todo, User

api = Blueprint('api', __name__)

token_auth = HTTPTokenAuth('Bearer')


@token_auth.verify_token
def verify_token(token):
    jwt_secret = current_app.config['JWT_SECRET']
    g.jwt_claims = {}
    try:
        g.jwt_claims = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        g.user_id = g.jwt_claims['id']
    except:
        return False
    return True


@token_auth.error_handler
def token_error():
    return jsonify(message='Authentication required.'), 401


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
