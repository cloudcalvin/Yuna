import gdspy
import collections


# class MetaStructure(type):
#     @classmethod
#     def __prepare__(metacls, name, bases, **kwds):
#         return collections.OrderedDict()

#     def __new__(cls, name, bases, attrs):
#         params = dict()

#         for key, value in attrs.items():
#             cls = super().__new__(meta, name, bases, attrs)
#             registry[cls.__name__] = cls
#             # if isinstance(value, Polygon):
#             #     params.update(value.__dict__)
#             # elif isinstance(value, Properties):
#             #     params.update(value.__dict__)

#         cls = super().__new__(cls, name, bases, dict(params))
#         return cls


class MetaLayer(type):

    @classmethod
    def __prepare__(mcls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        print('MetaLayer.__new__')

        # for key, attr in attrs.items():
        #     print(key, attr)
        # print('')

        if 'ltype' in attrs:
            ltype = attrs['ltype']
            attrs[ltype] = {}

            # for base in bases:
            #     try:
            #         attrs[ltype].update(base.fields)
            #     except AttributeError:
            #         pass

            attrs[ltype].update({k: v for k, v in attrs.items() if k.startswith('params')})

        if 'params' in attrs:
            new_name = attrs['params']['name']
        else:
            new_name = name

        cls = super().__new__(cls, new_name, bases, dict(attrs))

        if not hasattr(cls, 'registry'):
            cls.registry = {}

        if cls.__name__ not in ['Polygon', 'Layer']:
            cid = new_name.lower()
            cls.registry[cid] = cls

        return cls

    def __init__(cls, name, bases, attrs):
        # print('MetaLayer.__init__')

        super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        print('MetaLayer.__call__')

        # print(cls.__dict__)

        cls = super().__call__(*args, **kwargs)

        if 'params' in kwargs:
            cid = kwargs['params']['name'].lower()
            cls.registry[cid] = cls

        return cls

    def __add__(cls, other):
        print(cls.__dict__['params'])
        print(other.__dict__['params'])


class Polygon(gdspy.Polygon, metaclass=MetaLayer):
    """ 
    Process layer represents a specific process step which requires a 
    defined mask pattern. Typically this is a lithography step in.
    """

    def __init__(self, points, ltype='', params=None, **kwargs):
        print('\nProcessLayer.__init__')

        if params is None:
            layer = self.params['layer']
            datatype = self.params['datatype']
        else:
            if 'layer' not in params:
                raise ValueError('`layer` has to be defined')

            if 'datatype' not in params:
                raise ValueError('`datatype` has to be defined')

            layer = params['layer']
            datatype = params['datatype']

        super().__init__(points, layer=layer, datatype=datatype)

        if hasattr(self, 'params'):
            print(self.params)

    def __repr__(self):
        return '<Polygon ({}, {})>'.format(self.layer, self.datatype)

    # def __add__(self, other):
    #     print(self.__class__.__name__)
    #     print(other.__class__.__name__)
    #     psum = [self.params, other.params]
    #     print(psum)
        
    # def __eq__(self, other):
    #     if not isinstance(other, ProcessLayer): 
    #         return False
    #     return self.extension == other.extension
            
    # def __ne__(self, other):
    #     return (not self.__eq__(other))    


class Layer(Polygon):
    pass

