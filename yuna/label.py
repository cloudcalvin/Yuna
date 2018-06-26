import gdspy
import collections
import pyclipper

from yuna import utils


# class MetaBase(type):
#     @classmethod
#     def __prepare__(cls, name, bases, **kwds):
#         return collections.OrderedDict()

#     def __new__(cls, name, bases, attrs):
#         cls = super().__new__(cls, name, bases, dict(attrs))

#         if not hasattr(cls, 'class_label'):
#             cls.class_label = {}
#         if 'text' in attrs:
#             cls.class_label[attrs['text']] = cls

#         return cls


class MetaLabel(type):

    _ID = 0

    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, dict(attrs))

        if 'id' in attrs:
            cls.id = '{}_{}'.format('surface', attrs['id'])
        else:
            cls.id = '{}_{}'.format(name, MetaLabel._ID)
            MetaLabel._ID += 1

        # if 'text' in attrs:
        #     utils.llabels[attrs['text']] = cls

        # if not hasattr(cls, 'class_label'):
        #     cls.class_label = {}
        # if 'text' in attrs:
        #     cls.class_label[attrs['text']] = cls

        # if not hasattr(cls, 'class_label'):
        #     cls.class_label = list()
        # if 'text' in attrs:
        #     cls.class_label.append(cls)

        if not hasattr(cls, 'registry'):
            cls.registry = {}

        if 'text' in attrs.keys():
            cls.registry[attrs['text']] = cls
            # cls.registry[name] = cls

        return cls

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, dict(attrs))

    def __call__(cls, *args, **kwargs):
        cls = super().__call__(*args, **kwargs)

        utils.llabels[kwargs['text']] = cls

        return cls


class Label(gdspy.Label, metaclass=MetaLabel):
    """

    """

    def __init__(self, position, **kwargs):

        if 'text' in kwargs:
            text = kwargs['text']
        else:
            text = 'noname'

        if 'anchor' in kwargs:
            anchor = kwargs['anchor']
        else:
            anchor = 'o'

        if 'rotation' in kwargs:
            rotation = kwargs['rotation']
        else:
            rotation = None

        if 'magnification' in kwargs:
            magnification = kwargs['magnification']
        else:
            magnification = None

        if 'x_reflection' in kwargs:
            x_reflection = kwargs['x_reflection']
        else:
            x_reflection = False

        if 'layer' in kwargs:
            layer = kwargs['layer']
        else:
            layer = 0

        if 'texttype' in kwargs:
            texttype = kwargs['texttype']
        else:
            texttype = 0

        super().__init__(text, position,
                        anchor=anchor,
                        rotation=rotation,
                        magnification=magnification,
                        x_reflection=x_reflection,
                        layer=layer,
                        texttype=texttype)

    def __str__(self):
        return ("Yuna -> Label (\"{0}\", at ({1[0]}, {1[1]}), rotation {2}, "
            "magnification {3}, reflection {4}, layer {5}, texttype {6})")\
            .format(self.text, self.position, self.rotation,
                self.magnification, self.x_reflection, self.layer,
                self.texttype)

    def get(self):
        return gdspy.Label(self.text,
                           self.position,
                           self.anchor,
                           self.rotation,
                           self.magnification,
                           self.x_reflection,
                           self.layer,
                           self.texttype)

    def point_inside(self, polygon):
        if pyclipper.PointInPolygon(self.position, polygon) != 0:
            return True
        return False

    def flat_copy(self, level=-1):
        return self
        # return self.__copy__()


class MyLabel(Label):
    pass
