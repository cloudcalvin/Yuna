import numpy as np
import math


def get_grids_per_unit():
    unit = 1e-6
    grid = 5e-9

    return (unit/grid) * 10e-6


def _points_to_float(points):
    layer = np.array(points).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y) for y in x] for x in pl]
        polygons.append(poly)
    return polygons


def snap_points(points, grids_per_unit=None):
    """
    Round a list of points to a grid value
    """

    if grids_per_unit is None:
        grids_per_unit = get_grids_per_unit()
    else:
        raise ValueError('please define grids per unit')
    
    points = _points_to_float(points)

    polygons = list()

    for coords in points:
        poly = list()
        for coord in coords:
            p1 = (math.floor(coord[0] * grids_per_unit + 0.5)) / grids_per_unit
            p2 = (math.floor(coord[1] * grids_per_unit + 0.5)) / grids_per_unit
            poly.append([int(p1), int(p2)])
        polygons.append(poly)

    return polygons
