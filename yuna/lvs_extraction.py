import pyclipper
import os
import json
import gdspy

from yuna import grid
from yuna.utils import *

from yuna.polygon import Polygon
from yuna.cell import Cell
from yuna.label import Label
from yuna.sref import SRef

from shapely.geometry import Polygon as ShapelyPolygon


def user_label(class_name, prefix, cell, params):

    pdk = get_pdk()

    label_list = []

    for lbl in cell.labels:
        if lbl.text[0] == prefix:

            port_labels = lbl.text.split(' ')
            params['ports'] = calculate_ports(port_labels, pdk)

            params['text'] = lbl.text
            params['layer'] = lbl.layer
            params['anchor'] = lbl.anchor
            params['rotation'] = lbl.rotation
            params['magnification'] = lbl.magnification
            params['x_reflection'] = lbl.x_reflection
            params['texttype'] = lbl.texttype

            MasterLabel = type(class_name, (Label,), params)
            label = MasterLabel(lbl.position, **params)

            label_list.append(label)

    return label_list


def convert_to_yuna_cells(library, topcell, cell_list):
    """
    Convert the gdspy cells to yuna cells, which contains 
    metaclass operations and extra functions.
    """

    sref_list = []

    def _define_cell(library, cell_list, cell):
        cap = Cell(cell.name)

        for element in cell.elements:
            if isinstance(element, gdspy.CellReference):
                name = element.ref_cell.name

                params = {}
                params['rotation'] = element.rotation
                params['magnification'] = element.magnification
                params['x_reflection'] = element.x_reflection

                cap += SRef(cell_list[name], element.origin, **params)
            elif isinstance(element, gdspy.Polygon):
                params = {}
                params['layer'] = element.layer
                params['datatype'] = element.datatype

                cap += Polygon(element.points, **params)
            elif isinstance(element, gdspy.PolygonSet):
                raise ValueError('Implement PolygonSet support')

        return cap

    for element in topcell.elements:
        if isinstance(element, gdspy.CellReference):
            ccell = _define_cell(library, cell_list, element.ref_cell)

            library += ccell

            sref_list.append(SRef(ccell, element.origin))

    return sref_list


def create_device_cells(topcell, devices):
    """
    Reads all the cells from the TopLevel Cell and flattens them
    with a unique datatype value for each different device type.
    """

    def _define_cell(name, cell, single_datatype, device):
        pdk = get_pdk()

        DeviceCell = type(device, (Cell,), {})
        ccell = DeviceCell(name, cell=cell)
        ccell.flatten(single_datatype=single_datatype)

        for key, layer in pdk['Cells'][device].items():
            if key != 'color' and key == name:
                params = {}
                params = layer

                params['text'] = name
                params['layer'] = 64
                params['anchor'] = 'o'
                params['rotation'] = None
                params['magnification'] = None
                params['x_reflection'] = False
                params['texttype'] = 0

                position = element_center(ccell)

                DeviceLabel = type(device, (Label,), params)
                cap_label = DeviceLabel(position, **params)

                ccell += cap_label
        return ccell

    cell_list = {}
    for cell in topcell.get_dependencies(True):
        name = cell.name

        MyNode = type('Normal', (Cell,), {})
        ccell = MyNode(name, cell=cell)

        for key, single_datatype in devices.items():
            pdk_name = key[0].upper() + key[1:]

            if name.startswith(key):
                ccell = _define_cell(name, cell, single_datatype, pdk_name)

        cell_list[name] = ccell
    return cell_list



def element_center(element):
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    return (cx, cy)


def get_pdk():
    pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(pdk) as data_file:
        data = json.load(data_file)
    return data
    

def simplify(pp):
    if len(pp) > 10:
        factor = (len(pp)/100) * 1e5
        sp = ShapelyPolygon(pp).simplify(factor)
        plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]

        return plist[:-1]
    else:
        return pp
    # points = list()
    # for pp in self._union():
    #     if len(pp) > MaskBase._PP:
    #         factor = (len(pp)/self.smoothness) * MaskBase._FACTOR
    #         sp = Polygon(pp).simplify(factor)
    #         plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
    #         points.append(plist[:-1])
    #     else:
    #         points.append(list(pp))
    # return grid.snap_points(points)


def create_mask(polygons):

    poly_list = []
    for poly in polygons:
        if pyclipper.Orientation(poly) is False:
            reverse_poly = pyclipper.ReversePath(poly)
            solution = pyclipper.SimplifyPolygon(reverse_poly)
        else:
            solution = pyclipper.SimplifyPolygon(poly)

        pp = Polygon(points=solution)
        poly_list.append(pp)

    p1 = poly_list[0]
    for i in range(1, len(poly_list)):
        p1 = p1 & poly_list[i]

    mask = []
    for points in p1.points:
        simple_points = simplify(points)
        mask.append(simple_points)

    return mask
