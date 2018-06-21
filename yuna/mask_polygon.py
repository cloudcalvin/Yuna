import gdspy
import collections


class MetaMask(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, dict(attrs))

        if not hasattr(cls, 'registry'):
            cls.registry = {}

        cls.registry[name] = cls

        return cls

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, dict(attrs))

    def __call__(cls, *args, **kwargs):
        cls = super().__call__(*args, **kwargs)
        return cls


class MaskPolygon(gdspy.PolygonSet, metaclass=MetaMask):

    def __init__(self, polygons, **kwargs):

        if kwargs:
            self.layer = kwargs['layer']
            self.datatype = kwargs['datatype']
        else:
            self.layer = 0
            self.datatype = 0

        verbose = False

        super().__init__(polygons, layer=self.layer, 
                         datatype=self.datatype, verbose=verbose)

    def get(self):
        return gdspy.PolygonSet(self.polygons, self.layer, self.datatype)