from yuna.pdk.properties import LabelProperties


class TerminalProperties(LabelProperties):

    def __init__(self, raw_pdk_data):
        params = raw_pdk_data['Layers']['term']['63']
        super(TerminalProperties, self).__init__(**params)

    #     self.gds = gds
    #
    #     if 'ETL' in data:
    #         self.etl = data['ETL']
    #     else:
    #         self.etl = None
    #
    #     self.position = None
    #     self.stack = []
    #     # self.metals = []
    #
    # def get_label_data(self):
    #     pass
    #
    # def set_stack(self, stack):
    #     self.stack = stack
    #
    # def set_position(self, num):
    #     self.position = float(num)
    #
    # def set_width(self, num):
    #     self.width = float(num)
    #
    # # def add_contact_layer(self, gds):
    # #     if isinstance(gds, list):
    # #         self.metals = gds
    # #     else:
    # #         self.metals.append(gds)
