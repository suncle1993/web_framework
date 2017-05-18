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


# converted to re
PATTERNS = {
    'str': r'[^/]+',
    'word': r'\w+',
    'int': r'[+-]?\d+',
    'float': r'[+-]?\d+\.\d+',
    'any': r'.+'
}

TRANSLATORS = {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}


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


class Route:
    """A Route is a concrete match, containing pattern, translator, methods and handler"""
    __slots__ = ['methods', 'pattern', 'translator', 'handler']

    def __init__(self, pattern, translator, methods, handler):
        self.pattern = re.compile(pattern)
        if translator is None:
            translator = {}
        self.translator = translator
        self.methods = methods
        self.handler = handler

    def run(self, prefix: str, request: Request):
        if self.methods:
            if isinstance(self.methods, (list, tuple, set)) and request.method not in self.methods:
                return
            if isinstance(self.methods, str) and request.method != self.methods:
                return
        m = self.pattern.match(request.path.replace(prefix, '', 1))
        if m:
            vs = {}
            for k, v in m.groupdict().items():
                vs[k] = self.translator[k](v)
            request.vars = _Vars(vs)
            return self.handler(request)


class Router:
    """A Router contain multiple Route, storing in _routes. All Route in a Router has a specified prefix"""
    def __init__(self, prefix=''):
        self._prefix = prefix.rstrip('/')
        self._routes = []

    @property
    def prefix(self):
        return self._prefix

    def _rule_parse(self, rule: str, methods, handler) -> Route:
        pattern = ['^']
        spec = []
        translator = {}
        # /home/{name:str}/{id:int}
        is_spec = False
        for c in rule:
            if c == '{':
                is_spec = True
            elif c == '}':
                is_spec = False
                name, pat, t = self._spec_parse(''.join(spec))
                pattern.append(pat)
                translator[name] = t
                spec.clear()
            elif is_spec:
                spec.append(c)
            else:
                pattern.append(c)
        pattern.append('$')
        return Route(''.join(pattern), translator, methods, handler)

    @staticmethod
    def _spec_parse(spec: str):
        name, _, type_of_name = spec.partition(':')
        if not name.isidentifier():
            raise Exception('name {} is not identifier'.format(name))
        if type_of_name not in PATTERNS.keys():
            type_of_name = 'word'
        pattern = '(?P<{}>{})'.format(name, PATTERNS[type_of_name])
        return name, pattern, TRANSLATORS[type_of_name]

    def route(self, rule, methods=None):
        def wrap(handler):
            route = self._rule_parse(rule, methods, handler)
            self._routes.append(route)
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
        for route in self._routes:
            res = route.run(self.prefix, request)
            if res:
                return res


class Application:
    """A Application contain multiple Router. Each Router represents a prefix"""
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


@tv.get('/{id:int}')
def get_tv(request: Request) -> Response:
    return Response(body='tv {}'.format(request.vars.id), content_type='text/plain')

Application.register(router=tv)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 9000, Application())
    try:
        print('Serving on port 9000...')
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
