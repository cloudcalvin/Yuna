import os


def init():
    pdk_default = os.getcwd() + '/technology/' + 'raytheon.json'

    global pdk_name
    pdk_name = pdk_default
