import jwt

from flask import current_app, g, jsonify
from flask_httpauth import HTTPTokenAuth

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
