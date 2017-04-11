#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 4/5/17 9:16 PM
@author: Flowsnow
@file: app.py 
@function: 实现通用的web框架
"""
import webob
from webob.dec import wsgify

@wsgify
def application(request: webob.Request) -> webob.Response:
    name = request.params.get('name', 'default_name')

    response = webob.Response()
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
