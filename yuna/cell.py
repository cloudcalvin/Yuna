import os
import gdspy
import pathlib
import collections
import copy as libCopy

from yuna.polygon import Polygon
from yuna.sref import SRef
from yuna.label import Label
from yuna.elements import ElementList


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

        if elements is not None:
            assert isinstance(elements, list)
            self._elements = ElementList(items=elements)
        else:
            self._elements = ElementList()

    def __str__(self):
        return "Yuna -> Cell (\"{}\", {} elements, {} labels)".format(
                self.name, len(self._elements), len(self.labels))

    def __add__(self, other):
        # if isinstance(other, SRef):
        #     print('\nAdding cell {} to cell {}'.format(other.ref_cell.name, self.name))
        #     element = other.get_cellref()
        # elif isinstance(other, Polygon):
        #     print('\nAdding polygon to cell {}'.format(self.name))
        #     element = other.get_polygon()
        # elif isinstance(other, Label):
        #     print('\nAdding label to cell {}'.format(self.name))
        #     element = other.get_label()
        # else:
        #     raise ValueError('Implement element support')

        element = other.get()
        self.add(element)

        self._elements += other

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
        cell.labels = self.labels
        return cell

    # def update(self):
    #     depend = self.parse_to_gdspy()

    #     for cell in depend:
    #         # print(cell)
    #         for element in cell._elements:
    #             # print(' - ' + str(element))
    #             elem = element.get()
    #             cell.add(elem)
    #         # print('')

    #     # print(self)
    #     for element in self._elements:
    #         # print(' - ' + str(element))
    #         elem = element.get()
    #         self.add(elem)
    #     # print('')

    # def flat_copy(self):
    #     # self.update()

    #     # g_cell = self.get_cell()

    #     self.flatten()

    #     for element in self.elements:
    #         print(element)
    #     print('')

    #     return self



