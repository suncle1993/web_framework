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


class Application:
    router = []

    @classmethod
    def register(cls, pattern):
        def wrap(handler):
            cls.router.append((re.compile(pattern), handler))
            return handler
        return wrap

    @wsgify
    def __call__(self, request: Request) -> Response:
        for pattern, handler in self.router:
            if pattern.match(request.path):
                return handler(request)
        raise exc.HTTPNotFound('not found')


@Application.register('^/hello$')
def hello(request: Request) -> Response:
    name = request.params.get("name", 'default_name')
    response = Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


@Application.register('^/$')
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
