from yuna.pdk.layers.layer_base import LayerBase


class NtronProperties(LayerBase):

    def __init__(self, data):
        super(NtronProperties, self).__init__(data)

        if 'ETL' in data:
            self.etl = data['ETL']
        else:
            self.etl = None

        self.position = None
        self.stack = []
        self.metals = []

    def set_stack(self, stack):
        self.stack = stack

    def set_position(self, num):
        self.position = float(num)

    def set_width(self, num):
        self.width = float(num)

    def add_contact_layer(self, gds):
        if isinstance(gds, list):
            self.metals = gds
        else:
            self.metals.append(gds)
