


class Junction(object):

    def __init__(self, data):

        self.name = data['name']

        if 'ETL' in data:
            self.etl = data['ETL']
        else:
            self.etl = None

        self.color = data['color']
        self.position = None
        self.width = None
        self.rank = None
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
