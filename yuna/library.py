import gdspy

from yuna.cell import Cell


class Library(gdspy.GdsLibrary):
    """

    """

    def __init__(self, name='library', infile=None, **kwargs):
        super().__init__(name=name, infile=None, **kwargs)
        # self.structures = StructureList()

    def __add__(self, other):
        print('Adding cell to library')

        if isinstance(other, Cell):
            element = other.get_cell()
        else:
            raise ValueError('Implement element support')

        self.add(element)

        return self

    def view(self):
        pass

    def write(self):
        pass

        # auron_cell = gdspy.Cell('geom_for_auron')
        # ix_cell = gdspy.Cell('geom_for_inductex')

        # geom.gds_auron(auron_cell)
        # geom.gds_inductex(ix_cell)

        # debug_dir = os.getcwd() + '/debug/'
        # pathlib.Path(debug_dir).mkdir(parents=True, exist_ok=True)

        # gdspy.GdsLibrary(name='auron_geom')
        # gdspy.write_gds(debug_dir + 'auron.gds',
        #                 [auron_cell],
        #                 name='auron_geom',
        #                 unit=1.0e-12)

        # gdspy.GdsLibrary(name='ix_geom')
        # gdspy.write_gds(debug_dir + 'ix.gds',
        #                 [ix_cell],
        #                 name='ix_geom',
        #                 unit=1.0e-12)

        # gdspy.write_gds(debug_dir + 'all_cells.gds',
        #                 unit=1.0e-12)

        # if viewer == 'ix':
        #     gdspy.LayoutViewer(cells='geom_for_inductex')
        # elif viewer == 'auron':
        #     gdspy.LayoutViewer(cells='geom_for_auron')
        # elif viewer == 'all':
        #     gdspy.LayoutViewer()
        # print('----- Yuna -----\n')





    # def __iadd__(self, other):
    #     if isinstance(other, Structure) or isinstance(other, StructureList):
    #         self.structures.add(other)
    #     elif isinstance(other, Library):
    #         for i in other.structures:
    #             self.structures.add(i)
    #     return self
