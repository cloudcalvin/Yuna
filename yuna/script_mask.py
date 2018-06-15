import gdspy
import os


gds_file = os.getcwd() + '/technology/' + 'one_bit.gds'
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gds_file, unit=1.0e-12)
cell = gdsii.extract('OneBit')

subcell = cell.copy('Polygon Flatten',
                     exclude_from_current=True,
                     deep_copy=True)
subcell.flatten()

gds_poly = cell.get_polygons(True)

if (4, 0) in gds_poly:
    print(gds_poly[(4, 0)])

# gdspy.LayoutViewer()