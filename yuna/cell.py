import os
import utils
import gdspy
import pathlib
import collections
import pyclipper
import copy as libCopy

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
            element = other.get()
            self.add(element)
        elif isinstance(other, Polygon):
            element = other.get()
            self.add(element)
        elif isinstance(other, MaskPolygon):
            element = other.get()
            print(element)
            self.add(element)
        elif isinstance(other, Label):
            element = other.get()
            self.add(element)

        # element = other.get()
        # self.add(element)

        # if isinstance(other, Label):
        #     self._labels += other
        # # elif issubclass(type(other), MetaLabel):
        # #     self._labels += other
        # else:
        #     self._elements += other

        return self

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

    def update_labels(self, oktypes=[]):

        self._labels = ElementList()
        labels = self.labels
        self.labels = []

        for label in labels:
            params = {}
            params['text'] = label.text
            params['layer'] = label.layer
            params['anchor'] = 'o'
            params['rotation'] = label.rotation
            params['magnification'] = label.magnification
            params['x_reflection'] = label.x_reflection
            params['texttype'] = label.texttype

            if label.text.startswith('ntron'):
                MLabel = type('Ntron', (Label,), params)
            elif label.text.startswith('via'):
                MLabel = type('Via', (Label,), params)
            else:
                MLabel = type('Megh', (Label,), params)

            lbl = MLabel(label.position, **params)

            if isinstance(lbl, Label.registry['Via']):
                self += lbl
            elif isinstance(lbl, Label.registry['Ntron']):
                self += lbl
            else:
                self += lbl

            # for key, lbl in utils.llabels.items():
            #     if key == label.text:
            #         # print(type(lbl))
            #         if isinstance(lbl, Label.registry['Ntron']):
            #             print(lbl)
            #             self += lbl

            # for lbl in Label.class_label:
            #     print(lbl.__dict__)

            # # lbl = LabelClass(label.position, **params)
            # # lbl = utils.llabels[params['text']]

            # if lbl is Label.registry['Ntron']:
            # # # if isinstance(lbl, Label.class_label[label.text]):
            #     print(lbl)
            # # #     self += lbl

            # for ok in oktypes:
            #     if isinstance(lbl, Label.registry[ok]):
            #         self += lbl

        # for label in self._labels:
        #     elem = label.get()
        #     self.add(elem)

