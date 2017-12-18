from coverage import coverage
cov = coverage(omit=['env/*', 'test.py'])
cov.start()

import unittest, os, app, datetime

from base64 import b64encode
from playhouse.test_utils import test_database
from peewee import *

import app
from models import Todo, User



TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Todo], safe=True)

USER_DATA = {
    'username': 'test_user',
    'email': 'test_user@example.com',
    'password': 'password'
}

headers = {
    'Authorization': 'Basic ' + b64encode('test_user:password'.encode()).decode()
}
class UserModelTestCase(unittest.TestCase):
    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            User.create_user('test_user', 'test_user@example.com', 'password')
            self.assertEqual(User.select().count(), 1)
            user = User.select().get()
            self.assertEqual(user.username, 'test_user')
            self.assertEqual(user.email, 'test_user@example.com')
            self.assertNotEqual(user.password, 'password')

    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            User.create_user('test_user', 'test_user@example.com', 'password')
            with self.assertRaises(Exception):
                User.create_user('test_user', 'hello@example.com', 'asfsdf')

class TodoModelTestCase(unittest.TestCase):
    def test_create_todo(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name='Go bowling')
            todo = Todo.select().get()
            self.assertEqual(todo.name, 'Go bowling')
            now = datetime.datetime.now()
            self.assertLess(todo.created_at, now)

class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()

    def test_todolist_get(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name="Cook dinner")
            Todo.create(name="Wash dishes")
            rv = self.app.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b"Cook dinner", rv.data)
            self.assertIn(b"Wash dishes", rv.data)

    def test_todolist_post(self):
        with test_database(TEST_DB, (Todo, User)):
            User.create_user('test_user', 'test_user@example.com', 'password')
            rv = self.app.post('/api/v1/todos',
                               headers=headers,
                               data = {'name': 'Go bowling'}
                               )
            self.assertEqual(rv.status_code, 201)                   
            self.assertEqual(Todo.select().count(), 1)
            todo = Todo.select().get()
            self.assertEqual(todo.name, 'Go bowling')
            self.assertIn(b"Go bowling", rv.data)
            
    def test_todo_put(self):
        with test_database(TEST_DB, (Todo, User)):
            User.create_user('test_user', 'test_user@example.com', 'password')
            Todo.create(name='Cook dinner')
            rv = self.app.put('/api/v1/todos/1',
                               headers=headers,
                               data = {'name': 'Wash dishes'}
                               )
            self.assertEqual(rv.status_code, 200)
            todo = Todo.select().where(Todo.id == 1)
            self.assertEqual(todo[0].name, 'Wash dishes')
            self.assertIn(b"Wash dishes", rv.data)
            
    def test_todo_delete(self):
        with test_database(TEST_DB, (Todo, User)):
            User.create_user('test_user', 'test_user@example.com', 'password')
            Todo.create(name='Cook dinner')
            rv = self.app.delete('/api/v1/todos/1',
                               headers=headers)
            self.assertEqual(rv.status_code, 204)
            self.assertEqual(Todo.select().count(), 0)
            self.assertEqual(b"", rv.data)
            
class TodoViewTestCase(unittest.TestCase):            
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()
    
    def test_empty_db(self):
        with test_database(TEST_DB, (Todo,)):
            rv = self.app.get('/')
            self.assertIn(b"Add a New Task", rv.data)
        


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report(show_missing=True)
    cov.erase()



    
