#!/usr/bin/env python  
# encoding: utf-8  

"""
Created on 5/18/17 10:43 PM
@author: Flowsnow
@file: context.py 
@function: 
"""


class Context(dict):
    """Inherited from dict"""
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)


class AppContext(Context):
    """directly inherited from Context"""
    pass


class RouterContext(Context):
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

if __name__ == '__main__':
    pass
