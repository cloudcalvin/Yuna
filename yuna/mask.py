import gdsyuna


class Mask(object):

    def __init__(self):
        self.name = name

        self.mask = cl.defaultdict(dict)

    def add(self, element, key=None):
        """
        Add a new element or list of elements to this cell.

        Parameters
        ----------
        element : object
            The element or list of elements to be inserted in this cell.

        Returns
        -------
        out : ``Cell``
            This cell.
        """

        if key is None:
            raise TypeError('key cannot be None')

        assert isinstance(element[0], list)

        fabdata = {**self.pcd.layers['ix'],
                   **self.pcd.layers['res'],
                   **self.pcd.layers['term'],
                   **self.pcd.layers['via'],
                   **self.pcd.layers['jj'],
                   **self.pcd.layers['ntron']}

        polygon = Polygon(key, element, fabdata)

        if key[1] in self.mask[key[0]]:
            self.mask[key[0]][key[1]].append(polygon)
        else:
            self.mask[key[0]][key[1]] = [polygon]
