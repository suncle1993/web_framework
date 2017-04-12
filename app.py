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


def hello(request: Request) -> Response:
    name = request.params.get("name", 'default_name')
    response = Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


def root(request: Request) -> Response:
    return Response(body='hello world', status=200, content_type='text/plain')

router = {
    '/hello': hello,
    '/': root
}

@wsgify
def application(request: Request) -> Response:
    return router.get(request.path, root)(request)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, application)
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
