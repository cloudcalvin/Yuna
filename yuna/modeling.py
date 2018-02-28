import gdsyuna
import pygmsh
import meshio
import numpy as np
from auron import tools

from pygmsh.opencascade.surface_base import SurfaceBase
from pygmsh.opencascade.volume_base import VolumeBase
from pygmsh.built_in.volume import Volume


nm_units = 10e-6


def build_layers(layer, gds, layer_polygons, geom):

    z = float(layer['start']) * nm_units
    h = float(layer['height']) * nm_units

    wires = tools.convert_node_to_3d(layer_polygons, z)

    for i, poly in enumerate(wires):
        polyname = layer['name'] + '_' + str(i)

        gp = geom.add_polygon(poly, lcar=0.01, make_surface=True)

        surface_base = SurfaceBase(id0=gp.surface.id, is_list=False)

        ex1 = geom.extrude(surface_base, [0, 0, h])

        # v1 = VolumeBase(id0='ex1[1]', is_list=False)
        # uu = geom.boolean_union([v1, v2])


def extrude_polygon():
    geom = pygmsh.opencascade.Geometry()

    p1 = [[0.0, 0.0, 0.0],
          [1.0, 0.0, 0.0],
          [2.0, 0.0, 0.0],
          [2.0, 2.0, 0.0],
          [1.0, 2.0, 0.0],
          [1.0, 1.0, 0.0],
          [0.0, 1.0, 0.0]]

    p2 = [[0,0,0],
         [1,0,0],
         [1,1,0],
         [0,1,0]]

    poly_1 = geom.add_polygon(
                p1,
                lcar=0.1,
                make_surface=True
             )

    poly_2 = geom.add_polygon(
                p2,
                lcar=0.1,
                make_surface=True
             )

    print(poly_1.surface.id)
    print(poly_2.surface.id)
    print(SurfaceBase(id0=poly_1.surface.id, is_list=True))

    flat1 = SurfaceBase(id0=poly_1.surface.id, is_list=False)
    flat2 = SurfaceBase(id0=poly_2.surface.id, is_list=False)

    ex1 = geom.extrude(flat1, [0, 0, 0.1])
    ex2 = geom.extrude(flat2, [0, 0, 0.1])

    # geom.add_raw_code('Extrude{0,0,0.1}{ Surface{s0,s1}; }')
    # geom.add_raw_code('

    v1 = VolumeBase(id0='ex1[1]', is_list=False)
    v2 = VolumeBase(id0='ex2[1]', is_list=False)

    uu = geom.boolean_union([v1, v2])

    return pygmsh.generate_mesh(geom, geo_filename='test.geo')


def setup_3d_geo(wirechain, configdata):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """

    geom = pygmsh.opencascade.Geometry(characteristic_length_min=0.05, characteristic_length_max=0.05)

    print(configdata)

    for gds, layer in configdata['Layers'].items():
        if layer['name'] not in ['J2', 'I0', 'I1BU']:
            if (int(gds), 0) in wirechain.get_polygons(True):
                tools.green_print('Constructing layer: ' + layer['name'])

                layer_polygons = wirechain.get_polygons(True)[(int(gds), 0)]
                build_layers(layer, int(gds), layer_polygons, geom)

    layer_mesh = pygmsh.generate_mesh(geom, verbose=True, geo_filename='awe.geo')

    meshio.write('wakka_final.vtk', *layer_mesh)
    # meshio.write('surotto.vtk', *generate_mesh())
    # meshio.write('box.vtk', *diff_boxes())
    # meshio.write('extrude.vtk', *extrude_polygon())

    tools.cyan_print('3D modeling setup finished\n')
