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


class Router:
    def __init__(self, prefix=''):
        self._prefix = prefix.rstrip('/')
        self._routes = []

    @property
    def prefix(self):
        return self._prefix

    def route(self, pattern='.*', methods=None):
        def wrap(handler):
            self._routes.append((methods, re.compile(pattern), handler))
            return handler
        return wrap

    def get(self, pattern='.*'):
        return self.route(pattern, 'GET')

    def put(self, pattern='.*'):
        return self.route(pattern, 'PUT')

    def post(self, pattern='.*'):
        return self.route(pattern, 'POST')

    def delete(self, pattern='.*'):
        return self.route(pattern, 'DELETE')

    def patch(self, pattern='.*'):
        return self.route(pattern, 'PATCH')

    def head(self, pattern='.*'):
        return self.route(pattern, 'HEAD')

    def options(self, pattern='.*'):
        return self.route(pattern, 'OPTIONS')

    def run(self, request: Request):
        if not request.path.startswith(self.prefix):
            return
        for methods, pattern, handler in self._routes:
            if methods:
                if isinstance(methods, (list, tuple, set)) and request.method  not in methods:
                    continue
                if isinstance(methods, str) and request.method != methods:
                    continue
            m = pattern.match(request.path.replace(self._prefix, '', 1))
            if m:
                request.args = m.groups()  # tuple
                request.kwargs = _Vars(m.groupdict())  # dict
                return handler(request)

class Application:
    ROUTERS = []

    @classmethod
    def register(cls, router: Router):
        cls.ROUTERS.append(router)

    @wsgify
    def __call__(self, request: Request) -> Response:
        for router in self.ROUTERS:
            response = router.run(request)
            if response:
                return response
        raise exc.HTTPNotFound('not found')

tv = Router('/tv')


@tv.get(r'^/(?P<id>\d+)$')
def get_tv(request: Request) -> Response:
    return Response(body='tv {}'.format(request.kwargs.id), content_type='text/plain')

Application.register(router=tv)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, Application())
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
