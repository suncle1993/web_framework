#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 5/18/17 11:35 PM
@author: Flowsnow
@file: __init__.py.py 
@function: 
"""


import re

from webob import Request, Response
from webob import exc
from webob.dec import wsgify


# converted to re
_PATTERNS = {
    'str': r'[^/]+',
    'word': r'\w+',
    'int': r'[+-]?\d+',
    'float': r'[+-]?\d+\.\d+',
    'any': r'.+'
}

_TRANSLATORS = {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}



class _Context(dict):
    """Inherited from dict"""
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)


class _AppContext(_Context):
    """directly inherited from Context"""
    pass


class _RouterContext(_Context):
    app_ctx = None

    def with_app(self, app_ctx):
        self.app_ctx = app_ctx

    def __getattr__(self, item):
        """If the context at the Router level does not exist, the context of the APP level is returned"""
        if item in self.keys():
            return self[item]
        return getattr(self.app_ctx, item)

    def __setattr__(self, key, value):
        self[key] = value


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


class _Route:
    """A Route is a concrete match, containing pattern, translator, methods and handler"""
    __slots__ = ['methods', 'pattern', 'translator', 'handler']

    def __init__(self, pattern, translator, methods, handler):
        self.pattern = re.compile(pattern)
        if translator is None:
            translator = {}
        self.translator = translator
        self.methods = methods
        self.handler = handler

    def run(self, prefix: str, ctx: _Context, request: Request):
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
            return self.handler(ctx, request)


class _Router:
    """A Router contain multiple Route, storing in _routes. All Route in a Router has a specified prefix"""
    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix.rstrip('/')
        self._routes = []

        self._before_filters = []
        self._after_filters = []

        self._ctx = _RouterContext(kwargs)

    def context(self, ctx=None):
        if ctx:
            self._ctx.with_app(ctx)
        self._ctx.router = self
        return self._ctx

    @property
    def prefix(self):
        return self._prefix

    def _rule_parse(self, rule: str, methods, handler) -> _Route:
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
        return _Route(''.join(pattern), translator, methods, handler)

    @staticmethod
    def _spec_parse(spec: str):
        name, _, type_of_name = spec.partition(':')
        if not name.isidentifier():
            raise Exception('name {} is not identifier'.format(name))
        if type_of_name not in _PATTERNS.keys():
            type_of_name = 'word'
        pattern = '(?P<{}>{})'.format(name, _PATTERNS[type_of_name])
        return name, pattern, _TRANSLATORS[type_of_name]

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

    def before_request(self, fn):
        self._before_filters.append(fn)
        return fn

    def after_request(self, fn):
        self._after_filters.append(fn)
        return fn

    def run(self, request: Request):
        if not request.path.startswith(self.prefix):
            return
        for fn in self._before_filters:
            request = fn(self._ctx, request)
        for route in self._routes:
            res = route.run(self.prefix, self._ctx, request)
            if res:
                for fn in self._after_filters:
                    res = fn(self._ctx, request, res)
                return res


class M:
    """A Application contain multiple Router. Each Router represents a prefix"""
    Router = _Router
    Request = Request
    Response = Response

    _ROUTERS = []
    _before_filters = []
    _after_filters = []

    _ctx = _AppContext()

    def __init__(self, **kwargs):
        self._ctx.app = self
        for k, v in kwargs.items():
            self._ctx[k] = v

    @classmethod
    def add_extension(cls, name, extension):
        cls._ctx[name] = extension

    @classmethod
    def register(cls, router: Router):
        router.context(cls._ctx)
        cls._ROUTERS.append(router)

    @classmethod
    def before_request(cls, fn):
        cls._before_filters.append(fn)
        return fn

    @classmethod
    def after_request(cls, fn):
        cls._after_filters.append(fn)
        return fn

    @wsgify
    def __call__(self, request: Request) -> Response:
        for fn in self._before_filters:
            request = fn(self._ctx, request)  # self is an instance of current Application
        for router in self._ROUTERS:
            response = router.run(request)
            if response:
                for fn in self._after_filters:
                    response = fn(self._ctx, request, response)
                return response
        raise exc.HTTPNotFound('not found')
