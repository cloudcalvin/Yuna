import gdspy
import collections


class MetaLabel(type):

    _ID = 0

    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        # print('MetaLabel.__new__')
        cls = super().__new__(cls, name, bases, dict(attrs))

        if not hasattr(cls, 'registry'):
            cls.registry = {}

        cls.registry[name] = cls

        # if 'text' in attrs:
        #     cid = attrs['text'].lower()
        #     cls.registry[cid] = cls

        return cls

    def __init__(cls, name, bases, attrs):
        # print('MetaLabel.__init__')
        super().__init__(name, bases, dict(attrs))

        # cls.registry[name] = cls

    def __call__(cls, *args, **kwargs):
        # print('MetaLayer.__call__')
        cls = super().__call__(*args, **kwargs)

        # if 'text' in kwargs:
        #     cid = kwargs['text'].lower()
        #     cls.registry[cid] = cls

        return cls


class MasterNode(gdspy.Label, metaclass=MetaLabel):
    """
    Creates a new class with a unique device name.
    """

    _ID = 0

    __slots__ = 'id'

    def __init__(self, text, position, id0=None, **kwargs):
        print('MasterNode.__init__')
        super().__init__(text, position, anchor='o',
                         rotation=None, magnification=None,
                         x_reflection=False, layer=0, texttype=0)

        if id0 is None:
            self.id = 'via_{}'.format(MasterNode._ID)
            MasterNode._ID += 1
        else:
            self.id = 'poly {}'.format(id0)

    def __str__(self):
        return '<MasterNode ({})>'.format(self.params['metals'])

    def __repr__(self):
        return '<MasterNode ({}, {})>'.format(self.text, self.position)

    def get_label(self):
        return gdspy.Label(self.text, self.position, rotation=0, layer=64)


class Label(MasterNode):
    pass

