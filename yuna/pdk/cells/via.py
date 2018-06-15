from yuna.pdk.cells.cell_base import CellBase


class ViaPdk(CellBase):
    """

    """

    def __init__(self, name, data):
        super(ViaPdk, self).__init__(data)

        self.name = name
        self.stack = data['stack']
        self.metals = data['metals']
        self.color = '#A0A0A0'

    def __str__(self):
        return 'pdk.cells.vias.Via (id={}, name={}, stack={},metals={})'.format(
            self.id, self.name, self.stack, self.metals)

    def metals(self):
        pass

    def stack(self):
        pass
