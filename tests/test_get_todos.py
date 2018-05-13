import unittest

from app import create_app, db
from app.models import Todo, User
from config import TestingConfig


class GetTodosTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user1 = User(username='johndoe', password='password')
        self.user2 = User(username='janedoe', password='password')
        self.todo1 = Todo(text='Finish homework')
        self.todo2 = Todo(text='Exercise')
        self.user1.todos.extend([self.todo1, self.todo2])
        self.user2.todos.append((Todo(text='Mow lawn')))
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        self.token = self.user1.generate_jwt()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_todos(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/todos', headers=headers)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body['todos']), 2)

        todo = response_body['todos'][0]
        self.assertEqual(todo['id'], self.todo1.id)
        self.assertEqual(todo['text'], self.todo1.text)

    def test_get_todos_without_token(self):
        response = self.client.get('/api/todos')
        response_body = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_body['message'], 'Authentication required.')
