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

    def __init__(self, name, cell=None, elements=None, exclude_from_current=True, **kwargs):
        super().__init__(name, exclude_from_current=exclude_from_current)

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

        # for i in range(len(self.elements)):
            # e1 = self.elements[i]
        for e1 in self.elements:
            for e2 in other.elements:
                if e1.layers[0] == e2.layers[0]:
                    # self.elements[i].polygons = bool_operation(subj=e1.polygons, 
                    e1.polygons = bool_operation(subj=e1.polygons, 
                                            clip=e2.polygons, 
                                            method='difference')

                    # poly = gdspy.PolygonSet(points, 
                    #                         layer=e1.layers[0], 
                    #                         datatype=e1.datatypes[0])
                    # self.add(poly)
                # else:
                #     poly = gdspy.PolygonSet(e1.polygons, 
                #                             layer=e1.layers[0], 
                #                             datatype=e1.datatypes[0])
                #     self.add(poly)

        # for k1, v1 in self.get_polygons(True).items():
        #     for k2, v2 in other.get_polygons(True).items():
        #         if k1[0] == k2[0]:
        #             poly = bool_operation(subj=v1, 
        #                                   clip=v2, 
        #                                   method='difference')
        #             return poly
        # return self.get_polygons()

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

        # print(other)

        # element = other.get()
        # self.add(element)

        # if isinstance(other, Label):
        #     self._labels += other
        # # elif issubclass(type(other), MetaLabel):
        # #     self._labels += other
        # else:
        #     self._elements += other

        return self

    # def parse_to_gdspy(self):
    #     depend = set()
    #     for elem in self._elements:
    #         if isinstance(elem, SRef):
    #             depend.update(elem.ref_struct.parse_to_gdspy())
    #             depend.add(elem.ref_struct)
    #     return depend

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

        # print(labels)

        for label in labels:
            # LabelClass = Label.class_label[label.text]

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

            # print(lbl)
            # print(Label.registry['Ntron'])

            # if lbl is Label.registry['Ntron']:
            # # # if isinstance(lbl, Label.class_label[label.text]):
            #     print(lbl)
            # # #     self += lbl

            # print('')

            # for ok in oktypes:
            #     if isinstance(lbl, Label.registry[ok]):
            #         self += lbl

        # for label in self._labels:
        #     elem = label.get()
        #     self.add(elem)

