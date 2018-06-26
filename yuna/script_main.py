import os
import gdspy

from yuna.overdrive import grand_summon

gds_name = 'one_bit'
cell_name = 'OneBit'
pdk_name = 'pdf'

gds_file = os.getcwd() + '/technology/' + gds_name + '.gds'
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gds_file, unit=1.0e-12)
cell = gdsii.extract(cell_name)

yuna_geom = grand_summon(cell)
