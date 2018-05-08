
from matplotlib import pyplot
from shapely.geometry import MultiPoint, Point
from shapely.geometry import Polygon


def convert_node_to_2d(polygon):
    um = 10e-6

    my_points = list()
    for points in polygon:
        pp = list(points)
        # del pp[2]

        pp[0] = pp[0] * um
        pp[1] = pp[1] * um

        my_points.append(pp)

    return my_points


def simplify(poly):
    # fig = pyplot.figure(1, figsize=SIZE, dpi=90)

    um = 1e1

    # print(convert_node_to_2d(poly))

    # pp = convert_node_to_2d(poly)
    # p = Polygon(pp)

    xmax, xmin = poly.max(), poly.min()

    p = Polygon(poly)
    # p = Polygon([(0, 0), (1*um, 1*um), (1*um, 0)])

    # 1
    # ax = fig.add_subplot(121)

    q = p.simplify(1.5e5)

    # patch1a = PolygonPatch(p, facecolor=GRAY, edgecolor=GRAY)
    # ax.add_patch(patch1a)

    # patch1b = PolygonPatch(q, facecolor=BLUE, edgecolor=BLUE, alpha=0.5, zorder=2)
    # ax.add_patch(patch1b)

    # ax.set_title('a) tolerance 0.2')
    #
    # xrange = [xmin*um, xmax*um]
    # yrange = [xmin*um, xmax*um]
    # ax.set_xlim(*xrange)
    # ax.set_ylim(*yrange)
    # ax.set_aspect(1)

    #2
    # ax = fig.add_subplot(122)
    #
    # r = p.simplify(0.5)
    #
    # patch2a = PolygonPatch(p, facecolor=GRAY, edgecolor=GRAY, alpha=0.5, zorder=1)
    # ax.add_patch(patch2a)

    # patch2b = PolygonPatch(r, facecolor=BLUE, edgecolor=BLUE, alpha=0.5, zorder=2)
    # ax.add_patch(patch2b)

    # ax.set_title('b) tolerance 0.5')
    #
    # # xrange = [-3*um, 3*um]
    # # yrange = [-3*um, 3*um]
    # xrange = [0*um, 1*um]
    # yrange = [0*um, 1*um]
    # ax.set_xlim(*xrange)
    # ax.set_ylim(*yrange)
    # ax.set_aspect(1)

    # pyplot.show()

    return list(q.exterior.coords)
