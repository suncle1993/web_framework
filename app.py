#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 4/5/17 9:16 PM
@author: Flowsnow
@file: app.py 
@function: 实现通用的web框架
"""
from m import M
import json


def jsonify(**kwargs):
    """Support json in M"""
    body = json.dumps(kwargs)
    return M.Response(body, charset='utf-8', content_type='application/json')

tv = M.Router('/tv')


@tv.get('/{id:int}')
def get_tv(ctx, request):
    return jsonify(id=request.vars.id)


if __name__ == '__main__':
    app = M()
    app.register(tv)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 9000, app)
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()