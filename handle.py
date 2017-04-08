from db import QueryObject, MemoryQueryObject, UnQLiteQueryObject
from utils import *
from error import Error404
import flask
from types import GeneratorType


class Resource(object):
    def __init__(self, app, name=None):
        if name is not None:
            self.__class__.__name__ = name

        self.app = app
        self.objects = UnQLiteQueryObject(self.get_name())

    def on_create(self):
        pass

    def register(self, endpoint, method, route=None):
        if route is None:
            route = endpoint.__name__

        route = self.app.route_factory.clean_relative_route(route)
        route = self.get_name() + '/' + route
        route = self.app.route_factory.create_route(route)

        def wrapper():
            response = endpoint(flask.request.get_json())

            if isinstance(response, GeneratorType):
                response = list(response)

            return self.app._response_middleware(response)

        self.app._add_route(route, wrapper, endpoint.__name__, method)

    def list(self):
        # GET <resource>/ - returns a list of resources.
        return self.objects.all()

    def post(self, body):
        # POST <resource>/ - create a new resource and returns it.
        return self.objects.create(body)

    def get(self, pk):
        # GET <resource>/:pk/ - returns a single resource.
        obj = self.objects.get(pk)
        if obj is None:
            raise Error404()
        return obj

    def delete(self, pk):
        # DELETE <resource>/:pk/ - delete a resource.
        return self.objects.delete(pk)

    def put(self, pk, body):
        # PUT <resource>/:pk/ - updates a resource.
        return self.objects.update(pk, body)

    def get_name(self):
        return to_url(self.__class__.__name__)
