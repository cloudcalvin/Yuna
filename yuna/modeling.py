import gdsyuna
import pygmsh
import meshio
import numpy as np

from yuna import tools

from pygmsh.opencascade.surface_base import SurfaceBase
from pygmsh.opencascade.volume_base import VolumeBase
from pygmsh.built_in.volume import Volume


nm_units = 10e-6


# def extrude_polygon():
#     geom = pygmsh.opencascade.Geometry()
#
#     p1 = [[0.0, 0.0, 0.0],
#           [1.0, 0.0, 0.0],
#           [2.0, 0.0, 0.0],
#           [2.0, 2.0, 0.0],
#           [1.0, 2.0, 0.0],
#           [1.0, 1.0, 0.0],
#           [0.0, 1.0, 0.0]]
#
#     p2 = [[0,0,0],
#          [1,0,0],
#          [1,1,0],
#          [0,1,0]]
#
#     poly_1 = geom.add_polygon(
#                 p1,
#                 lcar=0.1,
#                 make_surface=True
#              )
#
#     poly_2 = geom.add_polygon(
#                 p2,
#                 lcar=0.1,
#                 make_surface=True
#              )
#
#     print(poly_1.surface.id)
#     print(poly_2.surface.id)
#     print(SurfaceBase(id0=poly_1.surface.id, is_list=True))
#
#     flat1 = SurfaceBase(id0=poly_1.surface.id, is_list=False)
#     flat2 = SurfaceBase(id0=poly_2.surface.id, is_list=False)
#
#     ex1 = geom.extrude(flat1, [0, 0, 0.1])
#     ex2 = geom.extrude(flat2, [0, 0, 0.1])
#
#     # geom.add_raw_code('Extrude{0,0,0.1}{ Surface{s0,s1}; }')
#     # geom.add_raw_code('
#
#     v1 = VolumeBase(id0='ex1[1]', is_list=False)
#     v2 = VolumeBase(id0='ex2[1]', is_list=False)
#
#     uu = geom.boolean_union([v1, v2])
#
#     return pygmsh.generate_mesh(geom, geo_filename='test.geo')


# def square_loop(geo_object):
#     """Construct square using built in geometry."""
#
#     p_arrays = [np.array([-0.5, -0.5, 0]), np.array([-0.5, 0.5, 0]),
#                 np.array([0.5, 0.5, 0]), np.array([0.5, -0.5, 0])]
#     points = []
#     for point in p_arrays:
#         new_point = geo_object.add_point(point, 0.05)
#         points.append(new_point)
#     points = points + [points[0]]
#     lines = []
#     for point1, point2 in zip(points[:-1], points[1:]):
#         line = geo_object.add_line(point1, point2)
#         lines.append(line)
#     line_loop = geo_object.add_line_loop(lines)
#     return geo_object, line_loop
#
#
# def circle_loop(geo_object):
#     """construct circle using built_in geometry module."""
#     points = [geo_object.add_point(point, 0.05) for point in
#               [np.array([0., 0.1, 0.]),
#                np.array([-0.1, 0, 0]),
#                np.array([0, -0.1, 0]),
#                np.array([0.1, 0, 0])]]
#     points = points + [points[0]]
#     quarter_circles = [geo_object.add_circle_arc(point1,
#                                                  geo_object.add_point(
#                                                      [0, 0, 0],
#                                                      0.05),
#                                                  point2) for
#                        point1, point2 in zip(points[:-1], points[1:])]
#     line_loop = geo_object.add_line_loop(quarter_circles)
#     return geo_object, line_loop
#
#
# def built_in_opencascade_geos():
#     """Construct surface using builtin and boolean methods."""
#     # construct surface with hole using standard built in
#     geo_object = pygmsh.opencascade.Geometry(0.05, 0.05)
#     geo_object, square = square_loop(geo_object)
#     geo_object, circle = circle_loop(geo_object)
#     geo_object.add_plane_surface(square, [circle])
#
#     # construct surface using boolean
#     geo_object2 = pygmsh.opencascade.Geometry(0.05, 0.05)
#     geo_object2, square2 = square_loop(geo_object2)
#     geo_object2, line_loop2 = circle_loop(geo_object2)
#     surf1 = geo_object2.add_plane_surface(square2)
#     surf2 = geo_object2.add_plane_surface(line_loop2)
#     geo_object2.boolean_difference([surf1], [surf2])
#
#     return geo_object, geo_object2
#
#
# def built_in_opencascade_geos_fragments():
#     """Cconstruct surface using boolean fragments."""
#
#     geo_object = pygmsh.opencascade.Geometry(0.04, 0.04)
#     geo_object, square = square_loop(geo_object)
#     geo_object, line_loop = circle_loop(geo_object)
#     surf1 = geo_object.add_plane_surface(square)
#     surf2 = geo_object.add_plane_surface(line_loop)
#
#     geo_object.boolean_fragments([surf1], [surf2])
#     return geo_object
#
#
# def test_fragments_diff_union():
#     """
#     Test planar surface with holes.
#     Construct it with boolean operations and verify that it is the same.
#     """
#     geo_object = pygmsh.opencascade.Geometry(0.04, 0.04)
#     geo_object, square = square_loop(geo_object)
#     geo_object, line_loop = circle_loop(geo_object)
#     surf1 = geo_object.add_plane_surface(square)
#     surf2 = geo_object.add_plane_surface(line_loop)
#
#     geo_object.add_physical_surface([surf1], label=1)
#     geo_object.add_physical_surface([surf2], label=2)
#
#     s1 = SurfaceBase(id0=surf1.id, is_list=False)
#     ex1 = geo_object.extrude(s1, [0,0,-0.1])
#
#     # geo_object.add_physical_volume(ex1[1])
#
#     # geo_object.add_raw_code('s() = Unique(Abs(Boundary{ Volume{1}; }));')
#     # geo_object.add_raw_code('Printf("returned entities (top, body, laterals, etc.) = ", s());')
#
#     # surf3 = geo_object.add_plane_surface(ex1[0])
#
#     # geo_object.boolean_fragments([surf1], [surf2])
#     diff = geo_object.boolean_difference([ex1[0]], [surf2], delete_other=False)
#     # geo_object.add_physical_volume(diff[1])
#     # geo_object.boolean_union([surf_diff, surf2])
#
#     layer_mesh = pygmsh.generate_mesh(geo_object, geo_filename='gmsh_test.geo')


class Sideconnect(gdsyuna.Polygon):
    """
    Inherits from the Polygon class in the gdspy library
    and extends on it by adding the edge of the polygon.

    Parameters
    ----------
    edge : coordinate numpy array
        This is the two edge nodes of the polygon
        that contains a terminal.
    """

    def __init__(self, edge, points, layer=0, datatype=0, verbose=True):
        super().__init__(points, layer=layer, datatype=datatype, verbose=True)
        self.edge = edge
        self.name = ''

    def set_terminal_name(self, name):
        pass


def geom_extrude_wirechain(layer, gds, layer_polygons, geom):
    """
    Extrude each polygon for the specific layer.

    Returns
    -------
    extruded : list()
        List of extrudes object from the pygmsh library.
    """

    z = float(layer['start']) * nm_units
    h = float(layer['height']) * nm_units

    wires = tools.convert_node_to_3d(layer_polygons, z)

    extruded = list()

    for i, poly in enumerate(wires):
        polyname = layer['name'] + '_' + str(i)

        gp = geom.add_polygon(poly, lcar=0.01, make_surface=True)

        surface_base = SurfaceBase(id0=gp.surface.id, is_list=False)

        ex = geom.extrude(surface_base, [0, 0, h])
        extruded.append(ex)

    return extruded


def wirechain(geom, cellname, cell_wirechain, jsondata):
    """
    Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh.

    Parameters
    ----------
    geom : opencascade object
        openCASCADE object from the pygmsh library
    cellname : string
        Name of the cell that has to be extracted
    cell_wirechain : Cell
        GDSpy library cell object after polygon manipulations
    jsondata : dict()
        Process configuration data from .json file
    """

    extruded_wirechain = dict()

    for gds, layer in jsondata['Layers'].items():
        if layer['name'] not in ['J2', 'I0', 'I1BU']:
            if (int(gds), 0) in cell_wirechain.get_polygons(True):
                tools.green_print('Constructing layer: ' + layer['name'])

                layer_polygons = cell_wirechain.get_polygons(True)[(int(gds), 0)]
                extruded_wirechain[int(gds)] = geom_extrude_wirechain(layer, int(gds), layer_polygons, geom)

    tools.cyan_print('3D modeling setup finished\n')

    return extruded_wirechain


def terminals(extruded_wirechain, geom, config, jsondata):
    """
    Extract the terminals on the edges of a layer.

    Notes
    -----
    The y-direction sideconnects have a key entry of (99, 0).
    The x-direction sideconnects have a key entry of (99, 1).
    """

    sideconnects = list()

    side_cell = gdsyuna.Cell('Sideconnect Cell')

    gds_term = int(jsondata['Params']['TERM']['gds'])

    if (gds_term, 0) not in config.yuna_polygons:
        raise ValueError('No terminals found')

    # TODO: Test for multiple layers in the wirechain.
    for gds, layer in jsondata['Layers'].items():
        if layer['type'] == 'wire' and (int(gds), 0) in config.yuna_polygons:
            points = config.yuna_polygons[(int(gds), 0)]
            points = np.vstack([points[0], points[0][0]])

            for p1, p2 in zip(points[:-1], points[1:]):

                bb = np.array([p1, p2, p2, p1])

                sc_width = 10e4

                for i in [0, 1]:
                    if abs(p1[i] - p2[i]) < 1e-9:
                        bb[0][i] += sc_width
                        bb[1][i] += sc_width
                        bb[2][i] -= sc_width
                        bb[3][i] -= sc_width

                polygon = gdsyuna.Polygon(bb, layer=99, datatype=0, verbose=False)
                side_cell.add(polygon)

                side = Sideconnect([p1, p2], bb, layer=99, datatype=0, verbose=False)
                sideconnects.append(side)

    terminal_line(extruded_wirechain, geom, config, sideconnects, jsondata)


def terminal_line(ex, geom, config, sideconnects, jsondata):
    """
    Notes
    -----
    The y-direction sideconnects have a key entry of (99, 0).
    The x-direction sideconnects have a key entry of (99, 1).
    """

    polygons = config.auron_cell.get_polygons(True)

    terminal_sides = list()

    for side in sideconnects:
        if (63, 0) in polygons:
            for ipoly in tools.angusj(polygons[(63, 0)], [side.points], 'intersection'):
                poly = gdsyuna.Polygon(ipoly, layer=99, datatype=2, verbose=False)
                if poly.area() > (0.7 * side.area()):
                    terminal_sides.append(side)
        else:
            print('... no terminals found in IC layout')

    check_terminal_sides(terminal_sides)
    geom_extrude_terminals(ex, geom, terminal_sides, jsondata)


# TODO: Future test maybe?
def check_terminal_sides(sideconnects):
    term_side_cell = gdsyuna.Cell('Termrinal Sideconnect Cell')

    for side in sideconnects:
        poly = gdsyuna.Polygon(side.points, layer=side.layer, datatype=side.datatype)
        term_side_cell.add(poly)


def square_loop(geom, p_arrays):
    """Construct square using built in geometry."""

    points = []
    for point in p_arrays:
        new_point = geom.add_point(point, 0.05)
        points.append(new_point)

    points = points + [points[0]]

    lines = []
    for point1, point2 in zip(points[:-1], points[1:]):
        line = geom.add_line(point1, point2)
        lines.append(line)

    line_loop = geom.add_line_loop(lines)

    return line_loop


def geom_extrude_terminals(ex, geom, sideconnects, jsondata):
    """

    """

    for i, side in enumerate(sideconnects):
        c1 = [c*10e-9 for c in side.edge[0]]
        c2 = [c*10e-9 for c in side.edge[1]]

        begin = float(jsondata['Layers']['1']['start']) * 10e-6
        height = float(jsondata['Layers']['1']['height']) * 10e-6

        c1.append(begin)
        c2.append(begin)

        c3 = [c1[0], c1[1], c1[2] + height]
        c4 = [c2[0], c2[1], c2[2] + height]

        p_arrays = [c1, c3, c4, c2]
        square = square_loop(geom, p_arrays)

        surf1 = geom.add_plane_surface(square)
        geom.add_physical_surface(surf1, label=i)

        # geo_object.boolean_fragments([surf1], [surf2])

        extrude_id = ex[1][0][0]
        geom.boolean_difference([extrude_id], [surf1], delete_other=False)

    # TODO: Error occurs when I return a value.
    pygmsh.generate_mesh(geom, geo_filename='sideconnects.geo')

    # meshio.write('3d_model.vtk', *layer_mesh)
