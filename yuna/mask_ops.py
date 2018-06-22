import pyclipper

from yuna.polygon import Polygon
from shapely.geometry import Polygon as ShapelyPolygon



def element_center(element):
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    return (cx, cy)


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