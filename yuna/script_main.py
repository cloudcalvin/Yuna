import os
import gdspy

from yuna.overdrive import *


gds_name = 'one_bit'
cell_name = 'OneBit'
pdk_name = 'pdf'

gds_file = os.getcwd() + '/technology/' + gds_name + '.gds'
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gds_file, unit=1.0e-12)
cell = gdsii.extract(cell_name)

# pdk_file = os.getcwd() + '/technology/' + pdk_name + '.json'

json_devices = {'via': 1, 'ntron': 7}

yuna_geom = grand_summon(cell, json_devices=json_devices)