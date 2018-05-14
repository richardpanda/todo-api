import unittest

from app import create_app, db
from app.models import Todo, User
from config import TestingConfig


class UpdateTodoTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(username='johndoe', password='password')
        self.todo = Todo(text='Finish homework')
        self.user.todos.append(self.todo)
        db.session.add(self.user)
        db.session.commit()
        self.token = self.user.generate_jwt()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_update_todo(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        request_body = {'text': 'Exercise', 'is_completed': True}
        response = self.client.put(
            f'/api/todo/{self.todo.id}', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body['id'], self.todo.id)
        self.assertEqual(response_body['text'], 'Exercise')
        self.assertTrue(response_body['is_completed'])

        todo = Todo.query.filter_by(id=self.todo.id).first()
        self.assertEqual(todo.text, 'Exercise')
        self.assertTrue(todo.is_completed)

    def test_update_todo_without_token(self):
        request_body = {'text': 'Exercise', 'is_completed': True}
        response = self.client.put(
            f'/api/todo/{self.todo.id}', json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_body['message'], 'Authentication required.')

    def test_update_todo_without_text(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        request_body = {'is_completed': True}
        response = self.client.put(
            f'/api/todo/{self.todo.id}', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Text is missing.')

    def test_update_todo_without_is_completed(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        request_body = {'text': 'Exercise'}
        response = self.client.put(
            f'/api/todo/{self.todo.id}', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Completed is missing.')

    def test_update_todo_with_nonexistent_todo(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        request_body = {'text': 'Exercise', 'is_completed': True}
        invalid_todo_id = self.todo.id + 1
        response = self.client.put(
            f'/api/todo/{invalid_todo_id}', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_body['message'], 'Todo not found.')

    def test_update_todo_with_diff_user(self):
        diff_user = User(username='janedoe', password='password')
        db.session.add(diff_user)
        db.session.commit()

        headers = {'Authorization': f'Bearer {diff_user.generate_jwt()}'}
        request_body = {'text': 'Exercise', 'is_completed': True}
        response = self.client.put(
            f'/api/todo/{self.todo.id}', headers=headers, json=request_body)
        response_body = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_body['message'], 'Unauthorized.')
