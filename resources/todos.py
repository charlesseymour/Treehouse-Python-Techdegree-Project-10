from flask import jsonify, Blueprint, abort

from flask.ext.restful import (Resource, Api, reqparse, 
                               inputs, fields, marshal,
                               marshal_with, url_for)

#from auth import auth
import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime
}

class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                 for todo in models.Todo.select()]
        return {'todos': todos}

todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)
        
