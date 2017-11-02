

class Via:
    """
    """

    def __init__(self, config):
        """
        """

        self.config = config

    def get_subject_clipper(self, poly):
        """  """

        Layers = self.config['Layers']

        polyclass = poly.keys()[0]
        polylayer = poly.values()[0]

        subjclip = None
        if polyclass == 'Layer':
            subjclip = Layers[polylayer]['result']
        elif polyclass == 'Module':
            print('Implement Module support.')

        return subjclip
