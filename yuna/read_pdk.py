import os
import json

from yuna import settings


def get_pdk():
    # pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(settings.pdk_name) as data_file:
        data = json.load(data_file)

    pdk_layers = [*data['Layers']['Ix'], *data['Layers']['via']]

    material_stack = {}
    for layer in pdk_layers:
        if layer['rank'] in material_stack:
            material_stack[layer['rank']].append(layer)
        else:
            material_stack[layer['rank']] = [layer]

    return data, material_stack
    

