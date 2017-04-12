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


def hello(request: Request) -> Response:
    name = request.params.get("name", 'default_name')
    response = Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


def root(request: Request) -> Response:
    return Response(body='hello world', status=200, content_type='text/plain')


class Application:
    router = {}

    @classmethod
    def register(cls, path, handler):
        cls.router[path] = handler

    @wsgify
    def __call__(self, request: Request) -> Response:
        try:
            return self.router[request.path](request)
        except KeyError:
            return exc.HTTPNotFound('{} not found'.format(request.path))


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    Application.register('/hello', hello)
    Application.register('/', root)
    server = make_server('0.0.0.0', 9000, Application())
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
