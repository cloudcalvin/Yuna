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

    # def __iadd__(self, other):
    #     if isinstance(other, Structure) or isinstance(other, StructureList):
    #         self.structures.add(other)
    #     elif isinstance(other, Library):
    #         for i in other.structures:
    #             self.structures.add(i)
    #     return self
