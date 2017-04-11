#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 4/11/17 10:52 AM
@author: Flowsnow
@file: wsgify_dec.py 
@function: 
"""
from webob import Request, Response
from functools import wraps


def wsgify(fn):
    @wraps(fn)
    def wrap(environ, start_response):
        request = Request(environ)
        response = fn(request)
        return response(environ, start_response)
    return wrap


@wsgify
def application(request: Request) -> Response:
    name = request.params.get('name', 'default_name')

    response = Response()
    response.text = 'hello {}'.format(name)
    response.status_code = 200
    response.content_type = 'text/plain'
    return response


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, application)
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
