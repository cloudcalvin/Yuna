from yuna.pdk.layers.layer_base import LayerBase


class ViaProperties(LayerBase):

    def __init__(self, gds, data):
        self.gds = gds

        if 'ETL' in data:
            self.etl = data['ETL']
        else:
            self.etl = None

        self.width = data['width']
        self.stack = data['stack']

    # def set_stack(self, stack):
    #     self.stack = stack
    #
    # def set_position(self, num):
    #     self.position = float(num)
    #
    # def set_width(self, num):
    #     self.width = float(num)
    #
    # def add_contact_layer(self, gds):
    #     if isinstance(gds, list):
    #         self.metals = gds
    #     else:
    #         self.metals.append(gds)
