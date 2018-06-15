from yuna.masternode import *

import os
import gdspy
import json


class Via(MasterNode):

    params = {
        'stack': [9],
        'metals': [10, 14],
        'color': '#A0A0A0'
    }


v1 = Via(text='via_Via', position=[1, 0])


def get_pdk():
    pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(pdk) as data_file:
        data = json.load(data_file)
    return data


pdk = get_pdk()


mlist = []
for key, layer in pdk['Cells']['Vias'].items():
    if key != 'color':

        params = {}
        params['params'] = layer

        MyNode = type('MyVia', (MasterNode,), params)
        
        mm = MyNode(text=key, position=[33, 67])

        mlist.append(mm)
