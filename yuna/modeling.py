import gdsyuna
import pygmsh
import meshio
import numpy as np

from yuna import tools
from collections import namedtuple

from pygmsh.opencascade.surface_base import SurfaceBase
from pygmsh.opencascade.volume_base import VolumeBase
from pygmsh.built_in.volume import Volume


nm_units = 10e-6


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


def update_wirechain(geom, poly_list, wirechain, datafield):
    """
    Parameters
    ----------
    geom : object
        pygmsh object
    poly_list : list
        List of DataField polygon objects.
    """

    for i, poly in enumerate(poly_list):
        if poly.data.name != 'TERM':
            assert type(poly.data.height) == float

            h = poly.data.height * nm_units
            z = poly.data.z_start * nm_units

            Layer = namedtuple('Layer', ['width', 'height'])
            ll = Layer(width=h, height=z)

            for all_points in poly.get_points():
                for points in all_points:
                    polyname = str(poly.layer) + '_' + str(poly.datatype) + '_' + str(i)
                    
                    pp = [[p[0], p[1], p[2] + z] for p in points]
                    gp = geom.add_polygon(pp, lcar=0.1, make_surface=True)
                    
                    Surface = namedtuple('Surface', ['surface', 'label'])
                    ss = Surface(surface=gp.surface, label=polyname)

                    if wirechain:
                        wirechain[ll].append(ss)
                    else:
                        wirechain[ll] = [ss]


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


def wirechain(geom, gds, layer, datafield, extruded):
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

    wirechain = dict()

    if gds in datafield.mask:
        for datatype, poly_list in datafield.mask[gds].items():
            update_wirechain(geom, poly_list, wirechain, datafield)

        for key, surfaces in wirechain.items():
            for ss in surfaces:
                ex = geom.extrude(ss.surface, [0, 0, key.width])
                
                geom.add_physical_surface(ss.surface, ss.label)
                geom.add_physical_volume(ex[1], ss.label)
                
                extruded[gds] = ex
                

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
