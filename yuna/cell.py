import os
import gdspy
import pathlib
import collections
import pyclipper
import copy as libCopy

from yuna import utils
from yuna.polygon import Polygon
from yuna.sref import SRef
from yuna.label import Label
from yuna.label import MetaLabel
from yuna.label import MyLabel
from yuna.elements import ElementList
from yuna.mask_polygon import MaskPolygon

from yuna.poly_ops import *


class MetaCell(type):
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


class Cell(gdspy.Cell, metaclass=MetaCell):
    """

    """

    def __init__(self, name, cell=None, elements=None, **kwargs):
        super().__init__(name, exclude_from_current=True)

        if cell is not None:
            self.import_cell(name, cell)

        self._labels = ElementList()

        if elements is not None:
            assert isinstance(elements, list)
            self._elements = ElementList(items=elements)
        else:
            self._elements = ElementList()

    def __str__(self):
        return "Yuna -> Cell (\"{}\", {} elements, {} labels)".format(
                self.name, len(self._elements), len(self.labels))

    def __sub__(self, other):
        for e1 in self.elements:
            for e2 in other.elements:
                if e1.layers[0] == e2.layers[0]:
                    e1.polygons = bool_operation(subj=e1.polygons,
                                                 clip=e2.polygons,
                                                 method='difference')

    def __add__(self, other):
        if isinstance(other, SRef):
            for label in other.ref_struct._labels:
                label = label.translate(*other.origin)
                self._labels += label
            element = other.get()
            self.add(element)
        elif isinstance(other, Polygon):
            element = other.get()
            self.add(element)
        elif isinstance(other, MaskPolygon):
            element = other.get()
            self.add(element)

        if type(other) in Label.registry.values():
            self._labels += other
            element = other.get()
            self.add(element)
        else:
            self._elements += other

        return self

    # def flat_labels(self, level=-1):
    #     if level == 0:
    #         return self._labels
    #     el = self._labels.flat_copy(level-1)
    #     return el

    # import copy as libCopy
    # def flat_labels(self, depth=None):
    #     """
    #     Returns a list with a copy of the labels in this cell.
    #     Parameters
    #     ----------
    #     depth : integer or ``None``
    #         If not ``None``, defines from how many reference levels to retrieve
    #         labels from.
    #     Returns
    #     -------
    #     out : list of ``Label``
    #         List containing the labels in this cell and its references.
    #     """
    #     labels = libCopy.deepcopy(self._labels)
    #     if depth is None or depth >= 0:
    #         for element in self._elements:
    #             if isinstance(element, SRef):
    #                 labels.extend(element.flat_labels(None if depth is None else depth - 1))
    #     return labels

    def flat_copy(self, duplicate_layer={}):
        self.flatten()

        # Convert doublicate layers to the same type.
        for l1, l2 in duplicate_layer.items():
            for element in self.elements:
                if isinstance(element, gdspy.PolygonSet):
                    for i in range(len(element.layers)):
                        if element.layers[i] == l1:
                            element.layers[i] = l2

    def view(self, library):
        debug_dir = os.getcwd() + '/debug/'
        pathlib.Path(debug_dir).mkdir(parents=True, exist_ok=True)

        name = debug_dir + self.name + '.gds'

        gdspy.write_gds(name,
                        name='yuna_library',
                        unit=1.0e-12)

        gdspy.LayoutViewer(library=library)

    def import_cell(self, name, cell):
        self.elements = libCopy.deepcopy(cell.elements)
        self.labels = libCopy.deepcopy(cell.labels)

        for ref in self.get_dependencies(True):
            if ref._bb_valid:
                ref._bb_valid = False

    def get_cell(self):
        cell = gdspy.Cell(self.name, exclude_from_current=True)
        cell.elements = self.elements
        cell.labels = self.get_labels()
        return cell
