#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 4/5/17 9:16 PM
@author: Flowsnow
@file: app.py 
@function: 实现通用的web框架
"""
import os


def application(environ: dict, start_response):
    qs = environ['QUERY_STRING']
    print(qs)  # name=suncle&age=18
    params = {}
    for kv in qs.split('&'):
        k, v = kv.split('=')
        params[k] = v
    print(params)
    status = '200 OK'  # HTTP Status
    response_headers = [('Content-type', 'text/plain')]  # HTTP Headers
    response_body = [b'hello world\n', b'I love you\n']
    start_response(status, response_headers)
    return response_body

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, application)
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()