import gdspy
import collections
import pyclipper


def bool_operation(subj, clip=None, method=None, closed=True):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    setattr(pc, 'StrictlySimple', True)

    if clip is not None:
        pc.AddPaths(clip, pyclipper.PT_CLIP, True)

    pc.AddPaths(subj, pyclipper.PT_SUBJECT, closed)

    subj = None
    if method == 'difference':
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif method == 'union':
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'intersection':
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'exclusive':
        subj = pc.Execute(pyclipper.CT_XOR,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    else:
        raise ValueError('please specify a clipping method')

    return subj


def offset_operation(layer, size):
    """
    Apply polygon offsetting using Angusj.
    Either blow up polygons or blow it down.
    """

    pco = pyclipper.PyclipperOffset()
    pco.AddPath(layer, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

    if size == 'down':
        return pco.Execute(-10000)[0]
    elif size == 'up':
        return pco.Execute(10.0)
    else:
        raise ValueError('please select the Offset function to use')


class MetaPolygon(type):
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


class Polygon(gdspy.Polygon, metaclass=MetaPolygon):
    """

    """

    def __init__(self, points=[], mask=False, **kwargs):

        if kwargs:
            layer = kwargs['layer']
            datatype = kwargs['datatype']
        else:
            layer = 0
            datatype = 0

        verbose = False

        super().__init__(points, layer=layer, datatype=datatype, verbose=verbose)

    def __str__(self):
        return "Yuna -> Polygon ({} vertices, layer {}, datatype {})".format(
                len(self.points), self.layer, self.datatype)

    def __add__(self, other):
        pass

    def __or__(self, other):
        poly = bool_operation(subj=other.points, clip=self.points, method='intersection')
        return Polygon(poly)

    def __sub__(self, other):
        poly = bool_operation(subj=other.points, clip=self.points, method='difference')
        return Polygon(poly)

    def __and__(self, other):
        poly = bool_operation(subj=other.points, clip=self.points, method='union')
        return Polygon(poly)

    def __xor__(self, other):
        pass

    def get(self):
        return gdspy.Polygon(self.points, self.layer, self.datatype)