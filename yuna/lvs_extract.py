import gdspy

from yuna import grid
from yuna.mask_ops import *
from yuna.cell import Cell
from yuna.label import Label


from yuna.utils import *
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


from yuna.sref import SRef
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


from yuna.read_pdk import *
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


from types import SimpleNamespace
def dynamic_cells(json_devices):
    devices = {}

    path = SimpleNamespace(single_datatype=0, cell=Cell('Path'))
    devices['Path'] = path
    
    for key, single_datatype in json_devices.items():
        name = key[0].upper() + key[1:]

        device = SimpleNamespace(single_datatype=single_datatype, cell=Cell(name))
        devices[name] = device
    
    return devices


from yuna.mask_polygon import MaskPolygon
def mask_levels(key, device, value, Layers):

    for layer in Layers:
        if layer['layer'] == key[0] and key[1] == device.single_datatype:
            params = layer
            params['datatype'] = device.single_datatype

            polygons = create_mask(value)

            MaskClass = type(params['name'], (MaskPolygon,), params)
            mask = MaskClass(polygons, **params)

            device.cell += mask



