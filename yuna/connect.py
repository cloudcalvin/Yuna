import tools
import gdsyuna


def get_ntron_box(gds, poly):
        """  """
        box_poly = gdsyuna.Polygon(poly, layer=gds, datatype=4)
        bb = box_poly.get_bounding_box()
        nbox = [[bb[0][0], bb[0][1]], 
                [bb[1][0], bb[0][1]],
                [bb[1][0], bb[1][1]],
                [bb[0][0], bb[1][1]]]
        return nbox


class BasisLayer():
    """ This is the basis wiring layer that connects
    the top-level wire with cells and terminals. """

    def __init__(self, gds, polygons):
        """  """
        self.gds = gds
        self.polygons = polygons
        self.baselayer = None
        
    def set_baselayer(self):
        tools.green_print('Union defualt baselayers: ' + str(self.gds))

        if (self.gds, 0) in self.polygons:
            poly = self.polygons[(self.gds, 0)]
            self.baselayer = tools.angusj(poly, poly, 'union')

    def connect_to_vias(self, auron_cell):
        """ Union vias with wires, but remove redundant
        vias that are not connected to any wires. """

        for via in self.polygons[(self.gds, 1)]:
            auron_cell.add(gdsyuna.Polygon(via, layer=self.gds, datatype=1))
            via_offset = tools.angusj_offset([via], 'up')
            if tools.angusj(via_offset, self.baselayer, 'intersection'):
                self.baselayer = tools.angusj([via], self.baselayer, 'union')

    def connect_to_jjs(self):
        """ We know the wires inside a jj, so we only have to 
        union it with wires and don't have to remove any jj layers. """

        for jj in self.polygons[(self.gds, 3)]:
            self.baselayer = tools.angusj([jj], self.baselayer, 'union')
        
    def connect_to_ntrons(self, atom, auron_cell):
        """ Union all the baselayers in the ntron cell
        and then find the bounding box. """

        nbox = None
        if self.gds == atom['wires']:
            poly = self.polygons[(self.gds, 4)]
            for box in tools.angusj(poly, poly, 'union'):
                nbox = get_ntron_box(self.gds, box)
                auron_cell.add(gdsyuna.Polygon(nbox, layer=self.gds, datatype=6))
            for poly in tools.angusj(poly, poly, 'union'):
                self.baselayer = tools.angusj([poly], self.baselayer, 'union')
        return nbox
        
        
        
        
        
        
