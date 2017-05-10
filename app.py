#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 4/5/17 9:16 PM
@author: Flowsnow
@file: app.py 
@function: 实现通用的web框架
"""
from webob import Request, Response
from webob.dec import wsgify
from webob import exc
import re


class _Vars:
    """Accessing to the dictionary is converted to access to attributes"""
    def __init__(self, data=None):
        if data is None:
            self._data = {}
        else:
            self._data = data

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError('no attribute {}'.format(item))

    def __setattr__(self, key, value):
        """Attributes are not allowed to be assigned, except for self._data = data in __init__"""
        if key != '_data':
            print('Attributes are not allowed to be assigned'.format(key))
            raise NotImplemented
        self.__dict__['_data'] = value


class Application:
    router = []

    @classmethod
    def route(cls, methods, pattern):
        def wrap(handler):
            cls.router.append((methods, re.compile(pattern), handler))
            return handler
        return wrap

    @classmethod
    def get(cls, pattern):
        return cls.route('GET', pattern)

    @classmethod
    def post(cls, pattern):
        return cls.route('POST', pattern)

    @classmethod
    def put(cls, pattern):
        return cls.route('PUT', pattern)

    @classmethod
    def delete(cls, pattern):
        return cls.route('DELETE', pattern)

    @classmethod
    def head(cls, pattern):
        return cls.route('HEAD', pattern)

    @classmethod
    def options(cls, pattern):
        return cls.route('OPTIONS', pattern)

    @wsgify
    def __call__(self, request: Request) -> Response:
        for methods, pattern, handler in self.router:
            if methods:
                if isinstance(methods, (list, tuple, set)) and request.method  not in methods:
                    continue
                if isinstance(methods, str) and request.method != methods:
                    continue
            m = pattern.match(request.path)
            if m:
                request.args = m.groups()  # tuple
                request.kwargs = _Vars(m.groupdict())  # dict
                return handler(request)
        raise exc.HTTPNotFound('not found')


# 192.168.110.13:9000/hello/suncle: The path has parameter {'name': 'suncle'}
@Application.get('^/hello/(?P<name>\w+)$')
def hello(request: Request) -> Response:
    name = request.kwargs.name
    response = Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


@Application.route(['GET', 'POST'], '^/$')
def root(request: Request) -> Response:
    return Response(body='hello world', status=200, content_type='text/plain')

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, Application())
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
