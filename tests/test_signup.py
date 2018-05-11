import unittest

from app import create_app, db
from app.models import User
from config import TestingConfig


class SignUpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup(self):
        password = 'password'
        request_body = {'username': 'johndoe',
                        'password': password, 'password_confirm': password}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response_body['token'])

        user = db.session.query(User).first()
        self.assertNotEqual(user.hash, password)

    def test_signup_without_username(self):
        password = 'password'
        request_body = {'password': password, 'password_confirm': password}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Username is missing.')

    def test_signup_without_password(self):
        request_body = {'username': 'johndoe', 'password_confirm': 'password'}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Password is missing.')

    def test_signup_without_password_confirm(self):
        request_body = {'username': 'johndoe', 'password': 'password'}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'],
                         'Password confirm is missing.')

    def test_signup_with_mismatch_password_and_password_confirm(self):
        request_body = {'username': 'johndoe',
                        'password': 'password', 'password_confirm': 'mismatch password'}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_body['message'], 'Password and password confirm do not match.')

    def test_signup_with_username_already_registered(self):
        username = 'johndoe'
        password = 'password'

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        request_body = {'username': username,
                        'password': password, 'password_confirm': password}
        response = self.client.post('/api/signup', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'],
                         'Username is already taken.')
