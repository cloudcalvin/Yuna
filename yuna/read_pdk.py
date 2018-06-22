import os
import json

from yuna import settings


def get_pdk():
    # pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(settings.pdk_name) as data_file:
        data = json.load(data_file)
    return data
    

