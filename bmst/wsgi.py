
import werkzeug
from werkzeug import Request, Response
from werkzeug.exceptions import MethodNotAllowed
import json


class StoreApp(object):
    def __init__(self, store):
        self.store = store

    @Request.application
    def __call__(self, request):

        if request.path == '/':
            return Response(json.dumps(list(self.store)))
        elif request.method=='PUT':
            key = request.path[1:]
            self.store[key] = request.data
            return Response() #XXX: correct code
        else:
            key = request.path[1:]
            return Response(self.store[key])
        return Response('a')