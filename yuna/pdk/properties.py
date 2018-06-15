import gdspy


class PolygonProperties(gdspy.Polygon):
    """
    Link the polygon properties to the polygon points set
    using the gdspy.Polygon library object.

    Parameters
    ----------
    points : array-like[N][2]
        Coordinates of the vertices of the polygon.
    **kwargs : dict
        Contains the parameters of the polygon as
        readin from the PDK. Or set manually for a PCell.
    """

    def __init__(self, points, **kwargs):
        self._assign_properties(kwargs)
        super(PolygonProperties, self).__init__(points=points,
                                                layer=kwargs['layer'],
                                                datatype=kwargs['datatype'])

    def _assign_properties(self, kwargs):
        """
        Assign properties to the Polygon class instance dynamically.
        """

        # print('\n[*] Setting polygon property attributes:')
        for key, value in kwargs.items():
            if key not in ['layer', 'datatype']:
                # print(key, value)
                setattr(self, key, value)


class LabelProperties(gdspy.Label):
    """
    Link the polygon properties to the polygon points set
    using the gdspy.Label library object.

    Parameters
    ----------
    position : array-like[2]
        Text anchor position.
    **kwargs : dict
        Contains the parameters of the label as
        readin from the PDK. Or set manually for a PCell.
    """

    def __init__(self, position, **kwargs):
        self._assign_properties(kwargs)
        super(LabelProperties, self).__init__(position=position,
                                              text=kwargs['text'],
                                              layer=kwargs['layer'])

    def _assign_properties(self, kwargs):
        """
        Assign properties to the Label class instance dynamically.
        """

        # print('\n[*] Setting label property attributes:')
        for key, value in kwargs.items():
            if key not in ['layer', 'text']:
                # print(key, value)
                setattr(self, key, value)
