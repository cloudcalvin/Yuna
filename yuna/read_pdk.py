import os
import json


def get_pdk():
    pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(pdk) as data_file:
        data = json.load(data_file)
    return data
    

