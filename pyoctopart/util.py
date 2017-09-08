'''
Utility features
'''


APIOBJECTS = {}

# pylint: disable=star-args, too-few-public-methods
class Curry(object):
    ''' A curried function '''
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw_copy = self.kwargs.copy()
            kw_copy.update(kwargs)
        else:
            kw_copy = kwargs or self.kwargs

        return self.fun(*(self.pending + args), **kw_copy)

def dict_to_class(obj, cls=None):
    ''' Check if obj is an instance of cls, instantiate it otherwise '''
    global APIOBJECTS
    if cls is None:
        cls = APIOBJECTS[obj['__class__']]
    if not isinstance(obj, cls):
        return cls.new_from_dict(obj)
    return obj

def list_to_class(objects, cls=None):
    ''' Given a list of dicts, instantiate them each as cls '''
    global APIOBJECTS
    if cls is None:
        cls = APIOBJECTS[objects[0]['__class__']]
    ret = []
    for obj in objects:
        obj = dict_to_class(obj, cls)
        ret.append(obj)
    return ret

def select(param, obj):
    ''' Select all keys containing param in obj '''
    return {key: val for key, val in obj.items() if param in key}

def api_object(cls):
    ''' Decorator for API objects that can be converted from dicts '''
    global APIOBJECTS
    APIOBJECTS[cls.__name__] = cls
    return cls

