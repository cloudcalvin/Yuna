import os


def init():
    pdk_default = os.getcwd() + '/technology/' + 'raytheon.json'
    device_defaults = {0: 'ix', 1: 'via', 7: 'ntron'}

    global pdk_name
    global json_devices

    pdk_name = pdk_default
    json_devices = device_defaults
