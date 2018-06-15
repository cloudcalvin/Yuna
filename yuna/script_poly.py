import json
import os
import gdspy

from yuna.lvs.structure import *


class M1(Polygon):

    ltype = 'inductances'
    
    params = {
        "layer": 1,
        "datatype": 0,
        "name": "M1",
        "rank": 0,
        "stack": [],
        "width": 6,
        "color": "#B266FF"
    }


class NbN(Polygon):

    ltype = 'inductances'
    
    params = {
        "layer": 5,
        "datatype": 0,
        "name": "M2",
        "rank": 0,
        "stack": [],
        "width": 6,
        "color": "#B266FF"
    }


m1 = M1(points=[1, 0, 0], layer=9, datatype=2)
nbn = NbN(points=[87, 0, 0], layer=5, datatype=1)


def get_pdk():
    pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(pdk) as data_file:
        data = json.load(data_file)
    return data


pdk = get_pdk()


def get_subcell():
    gds_file = os.getcwd() + '/technology/' + 'one_bit.gds'
    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(gds_file, unit=1.0e-12)
    cell = gdsii.extract('OneBit')

    subcell = cell.copy('Polygon Flatten',
                        exclude_from_current=True,
                        deep_copy=True)

    return subcell.flatten()


cell = get_subcell()

gds_poly = cell.get_polygons(True)

if (4, 0) in gds_poly:
    print(gds_poly[(4, 0)])

mlist = []
for params in pdk['Layers']['ix']:

    key = (params['layer'], params['datatype'])

    if key in gds_poly:
        polygon = gds_poly[key]

        ll = Layer(polygon, ltype='inductance', params=params)
        mlist.append(ll)





