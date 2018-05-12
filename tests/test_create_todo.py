import unittest

from app import create_app, db
from app.models import Todo, User
from config import TestingConfig


class CreateTodoTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username='johndoe', password='password')
        db.session.add(self.user)
        db.session.commit()
        self.token = self.user.generate_jwt()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_todo(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        text = 'Make bed'
        request_body = {'text': text}
        response = self.client.post(
            '/api/todos', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 201)

        todo = Todo.query.filter_by(user_id=self.user.id, text=text).first()
        self.assertEqual(response_body['id'], todo.id)
        self.assertEqual(response_body['text'], todo.text)

    def test_create_todo_without_token(self):
        text = 'Make bed'
        request_body = {'text': text}
        response = self.client.post('/api/todos', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_body['message'], 'Authentication required.')

    def test_create_todo_without_text(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        request_body = {}
        response = self.client.post(
            '/api/todos', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Text is missing.')
