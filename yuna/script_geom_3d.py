import os
import gdspy

from yuna.geom_3d import generate_3d_model

gds_name = 'one_bit'
cell_name = 'OneBit'
pdk_name = 'pdf'

gds_file = os.getcwd() + '/technology/' + gds_name + '.gds'
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gds_file, unit=1.0e-12)
cell = gdsii.extract(cell_name)

rikku_geom = generate_3d_model(cell)
