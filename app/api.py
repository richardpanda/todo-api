import jwt

from app import db
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import exists

from .models import User

api = Blueprint('api', __name__)


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

    token = jwt.encode(
        {'id': user.id}, current_app.config['JWT_SECRET'], algorithm='HS256').decode()

    return jsonify(token=token), 201
