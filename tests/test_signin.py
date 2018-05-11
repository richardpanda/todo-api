import unittest

from app import create_app, db
from app.models import User
from config import TestingConfig


class SignInTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username='johndoe', password='password')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signin(self):
        request_body = {'username': self.user.username,
                        'password': self.user.password}
        response = self.client.post('/api/signin', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response_body['token'])

    def test_signin_without_username(self):
        request_body = {'password': self.user.password}
        response = self.client.post('/api/signin', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Username is missing.')

    def test_signin_without_password(self):
        request_body = {'username': self.user.username}
        response = self.client.post('/api/signin', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Password is missing.')

    def test_signin_with_unregistered_username(self):
        request_body = {'username': 'janedoe', 'password': self.user.password}
        response = self.client.post('/api/signin', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_body['message'], 'Username does not exist.')

    def test_signin_with_incorrect_password(self):
        request_body = {'username': self.user.username,
                        'password': 'incorrect password'}
        response = self.client.post('/api/signin', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_body['message'], 'Incorrect password.')
