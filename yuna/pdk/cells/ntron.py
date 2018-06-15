from yuna.pdk.cells.cell_base import CellBase


class NtronPdk(CellBase):
    """

    """

    _ID = 0

    def __init__(self, name, data):
        super(NtronPdk, self).__init__(data)

        self.name = name
        self.metals = data['metals']
        self.color = '#F5555'

    def __str__(self):
        return 'pdk.cells.ntron.Ntron (id={}, name={}, metals={})'.format(
            self.id, self.name, self.metals)

    def metals(self):
        pass
