import pygmsh

from yuna.library import Library
from yuna.cell import Cell

from .utils import logging


from types import SimpleNamespace
def dynamic_cells():
    devices = {}

    path = SimpleNamespace(single_datatype=0, cell=Cell('Path'))
    devices['Path'] = path

    return devices


from yuna.mask_ops import create_mask
from yuna.mask_polygon import MaskPolygon
from yuna.sref import SRef
def mask_levels(key, device, value, Layers):

    for layer in Layers:
        if layer['layer'] == key[0] and key[1] == device.single_datatype:

            print('adding properties to layer polygon:')
            print(layer)

            params = layer
            params['datatype'] = device.single_datatype

            polygons = create_mask(value)

            MaskClass = type(params['name'], (MaskPolygon,), params)
            mask = MaskClass(polygons, **params)

            device.cell += mask


import os
import meshio
from yuna import settings
from yuna.read_pdk import *
def generate_3d_model(topcell, log=None):
    """
    Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh.

    Parameters
    ----------
    basedir : string
        Current working directory string.
    args : docopt library object
        Contains the args received from ExVerify

    Arguments
    ---------
    cell : string
        Name of the cell inside the top-level gds layout
        that has to be executed.
    config_name : string
        Name of the process configuration file.
    model : bool
        If True then a 3D model of the cell must be created.
    """

    print('----- Rikku -----\n')

    geom = pygmsh.opencascade.Geometry(
        characteristic_length_min=0.005,
        characteristic_length_max=0.005,
    )

    geom.add_raw_code('Mesh.Algorithm = 6;')
    geom.add_raw_code('Coherence Mesh;')

    library = Library(name='3D Geometry Library')

    cell = Cell('3D Structure')

    settings.init()

    pdk, material_stack = get_pdk()

    print('-------------------- ** POLYGONS ** --------------------\n')

    pdk_layers = [*pdk['Layers']['Ix'], *pdk['Layers']['via']]

    devices = dynamic_cells()

    for key, value in topcell.get_polygons(True).items():
        for device in devices.values():
            mask_levels(key, device, value, pdk_layers) 

    extruded = []
    for element in devices['Path'].cell._elements:
        surface_list = []

        element.geom_surfaces(geom, surface_list, material_stack)
        element.geom_extrude(geom, surface_list)

        extruded.extend(element.extrude)

    geom.boolean_union(extruded)

    cell += SRef(devices['Path'].cell, (0, 0))

    library += cell

    cell.view(library)

    mesh = pygmsh.generate_mesh(geom,
                                verbose=True,
                                geo_filename='rikku_test' + '.geo')

    directory = os.getcwd() + '/debug/gmsh/'
    mesh_file = '{}{}.msh'.format(directory, 'test')

    if not os.path.exists(directory):
        os.makedirs(directory)

    meshio.write(mesh_file, *mesh)
    meshio.write('test.vtu', *mesh)

    return geom

