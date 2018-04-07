import gdsyuna
import pygmsh
import meshio
import numpy as np
import pyclipper

from yuna import tools
from collections import namedtuple

from pygmsh.opencascade.surface_base import SurfaceBase
from pygmsh.opencascade.volume_base import VolumeBase
from pygmsh.built_in.volume import Volume

from .terminal import Terminal

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


class SurfaceLabel(object):
    _ID = 0

    def __init__(self, gds, datatype, id0=None):
        self.gds = gds
        self.datatype = datatype

        if id0 is None:
            self.id = 's{{{}}}{{{}}}{{{}}}'.format(self.gds, self.datatype, SurfaceLabel._ID)
            SurfaceLabel._ID += 1
        else:
            self.id0


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

            surface_label = SurfaceLabel(poly.layer, poly.datatype)

            pp = poly.get_points(z)

            if poly.holes:
                print('     .hole detected')

                hh = poly.get_holes(z)
                mhole = geom.add_polygon(hh, lcar=0.1, make_surface=False)
                gp = geom.add_polygon(pp, lcar=0.1, holes=[mhole.line_loop], make_surface=True)
            else:
                gp = geom.add_polygon(pp, lcar=0.1, make_surface=True)

            Surface = namedtuple('Surface', ['surface', 'label'])
            ss = Surface(surface=gp.surface, label=surface_label.id)

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
        gdspy library cell object after polygon manipulations
    jsondata : dict()
        Process configuration data from .json file
    """

    wirechain = dict()

    if gds in datafield.mask:
        # TODO: Fix this hardcode
        if gds in [21, 6, 1]:
            for datatype, poly_list in datafield.mask[gds].items():
                update_wirechain(geom, poly_list, wirechain, datafield)

            for key, surfaces in wirechain.items():
                for ss in surfaces:
                    ex = geom.extrude(ss.surface, [0, 0, key.width])

                    geom.add_physical_surface(ss.surface, ss.label)
                    geom.add_physical_volume(ex[1], ss.label)

                    extruded[gds] = ex


def terminals(geom, cell, datafield):
    terms = dict()

    for key, polygons in datafield.get_terminals().items():
        for points in polygons:
            for lbl in cell.labels:
                if pyclipper.PointInPolygon(lbl.position, points) == 1:
                    print('     .label detected: ' + lbl.text)
                    terms[lbl.text] = Terminal([points])

    for name, term in terms.items():
        print(name, term)
        term.set_vector()
        term.metal_connection(cell, datafield, name)
        term.metal_edge(datafield)
        term.extrude(geom, datafield)

    tools.write_cell((99, 0), 'Terminal Edges', terms)
