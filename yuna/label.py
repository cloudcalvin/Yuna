import gdspy
import collections


class MetaLabel(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, dict(attrs))

        if not hasattr(cls, 'class_label'):
            cls.class_label = {}
        if 'text' in attrs:
            cls.class_label[attrs['text']] = cls

        if not hasattr(cls, 'registry'):
            cls.registry = {}
        cls.registry[name] = cls
           
        return cls

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, dict(attrs))

    def __call__(cls, *args, **kwargs):
        cls = super().__call__(*args, **kwargs)
        return cls


class Label(gdspy.Label, metaclass=MetaLabel):
    """

    """

    def __init__(self, position, **kwargs):

        if kwargs:
            text = kwargs['text']
            anchor = kwargs['anchor']
            rotation = kwargs['rotation']
            magnification = kwargs['magnification']
            x_reflection = kwargs['x_reflection']
            layer = kwargs['layer']
            texttype = kwargs['texttype']
        else:
            text = 'noname'
            anchor = 'o'
            rotation = None
            magnification = None
            x_reflection = False
            layer = 0
            texttype = 0

        super().__init__(text, position,
                        anchor=anchor,
                        rotation=rotation,
                        magnification=magnification,
                        x_reflection=x_reflection,
                        layer=layer,
                        texttype=texttype)

    def __str__(self):
        return ("Label (\"{0}\", at ({1[0]}, {1[1]}), rotation {2}, "
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
