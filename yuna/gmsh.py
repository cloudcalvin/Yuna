"""
    Hacker: 1h3d*n
    For: Volundr
    Docs: Algorithm 1
    Date: 31 April 2017

    Description: Write the gmsh file for meshing.

    --> Layer 80 is the wire layer difference from
        the moat layer.
    --> Layer 71 is the via layer union with the
        wire layer.
    --> Layer 70 is the moat layer union with the
        wire layer.
"""

WIRE_LIST = [81, 80, 72, 71]
HOLE_LIST = [70]

class Gmsh:
    file = None

    def __init__(self, file_name, cell_poly, hole_poly):
        self.file_name = file_name
        self.cell_poly = cell_poly
        self.hole_poly = hole_poly

    def open(self):
        self.file = open(self.file_name, "w")

        self.file.write('/******************************************** \n')
        self.file.write(' * \n')
        self.file.write(' * Gmsh rectangle volume \n')
        self.file.write(' * \n')
        self.file.write(' ********************************************/ \n\n')
        self.file.write('// Discretization size \n')
        self.file.write('lc1 = 0.1e-4; \n\n')
        self.file.write('// Ground \n')
        self.file.write('t2 = 350E-9; \n')
        self.file.write('layers1 = 1; \n\n')
        self.file.write('// units \n')
        self.file.write('ws = 1E-6; \n\n')

    def structure(self):
        self.file.write("// Structure \n")
        index = 0
        count = 1

        global WIRE_LIST

        for key in self.cell_poly:
            if key[0] in WIRE_LIST:
                for poly in self.cell_poly[key]:
                    for i in range(len(poly)):
                        string = "Point(" + str(count+i) + ")"
                        string = string + " = {" + str(poly[i][0]) + "*ws, "
                        string = string + str(poly[i][1]) + "*ws, t2, lc1}; \n"
                        self.file.write(string)
                    count = count + len(poly)
            # elif (key == (70, 0)):
            #     for poly in self.cell_poly[key]:
            #         for i in range(len(poly)):
            #             string = "Point(" + str(count+i) + ")"
            #             string = string + " = {" + str(poly[i][0]) + "*ws, "
            #             string = string + str(poly[i][1]) + "*ws, t2, lc1}; \n"
            #             self.file.write(string)
            #         count = count + len(poly)
            index = index + 1

        # Add hole polygons
        if (self.hole_poly is not None):
            if isinstance(self.hole_poly[0][0], list):
                self.file.write("\n// Holes \n")
                for poly in self.hole_poly:
                    print poly
                    for i in range(len(poly)):
                        string = "Point(" + str(count+i) + ")"
                        string = string + " = {" + str(poly[i][0]) + "*ws, "
                        string = string + str(poly[i][1]) + "*ws, t2, lc1}; \n"
                        self.file.write(string)
                    count = count + len(poly)
                    index = index + 1
            else:
                self.file.write("\n// Holes \n")
                for poly in self.hole_poly:
                    string = "Point(" + str(count) + ")"
                    string = string + " = {" + str(poly[0]) + "*ws, "
                    string = string + str(poly[1]) + "*ws, t2, lc1}; \n"
                    self.file.write(string)
                    count = count + 1
                    # index = index + 1

    def structure_lines(self):
        self.file.write("\n// Structure Lines \n")
        index = 0
        count = 1
        for key in self.cell_poly:
            if key[0] in WIRE_LIST:
                for poly in self.cell_poly[key]:
                    for i in range(len(poly)):
                        string = "Line(" + str(count+i) + ")" + " = {"
                        string = string + str(count+i) + ","
                        if (i == len(poly)-1):
                            string = string + str(count) + "}; \n"
                            self.file.write(string)
                        else:
                            string = string + str(count+i+1) + "}; \n"
                            self.file.write(string)
                    count = count + len(poly)
            # elif (key == (70, 0)):
            #     for poly in self.cell_poly[key]:
            #         for i in range(len(poly)):
            #             string = "Line(" + str(count+i) + ")" + " = {"
            #             string = string + str(count+i) + ","
            #             if (i == len(poly)-1):
            #                 string = string + str(count) + "}; \n"
            #                 self.file.write(string)
            #             else:
            #                 string = string + str(count+i+1) + "}; \n"
            #                 self.file.write(string)
            #         count = count + len(poly)
            # index = index + 1

        if (self.hole_poly is not None):
            if isinstance(self.hole_poly[0][0], list):
                for poly in self.hole_poly:
                    for i in range(len(poly)):
                        if (i == len(poly)-1):
                            self.file.write("Line(" + str(count+i) + ")"
                                                    + " = {" + str(count+i)
                                                    + "," + str(count)
                                                    + "}; \n")
                        else:
                            self.file.write("Line(" + str(count+i) + ")"
                                                    + " = {" + str(count+i)
                                                    + "," + str(count+i+1)
                                                    + "}; \n")
                    count = count + len(poly)
                    index = index + 1
            else:
                for i in range(len(self.hole_poly)):
                    if (i == len(self.hole_poly)-1):
                        self.file.write("Line(" + str(count+i) + ")"
                                                + " = {" + str(count+i)
                                                + "," + str(count) + "}; \n")
                    else:
                        self.file.write("Line(" + str(count+i) + ")"
                                                + " = {" + str(count+i) + ","
                                                + str(count+i+1) + "}; \n")
                count = count + len(poly)
                count = count + 1

    def structure_loops(self):
        self.file.write("\n// Structure Loop \n")
        index = 0
        count = 1
        for key in self.cell_poly:
            if key[0] in WIRE_LIST:
                for poly in self.cell_poly[key]:
                    self.file.write("Line Loop(" + str(index+1) + ") = {")
                    for i in range(len(poly)):
                        if (i == len(poly)-1):
                            self.file.write(str(count+i) + "}; \n")
                        else:
                            self.file.write(str(count+i) + ",")
                    count = count + len(poly)
                    index = index + 1
            # elif (key == (70, 0)):
            #     for poly in self.cell_poly[key]:
            #         self.file.write("Line Loop(" + str(index+1) + ") = {")
            #         for i in range(len(poly)):
            #             if (i == len(poly)-1):
            #                 self.file.write(str(count+i) + "}; \n")
            #             else:
            #                 self.file.write(str(count+i) + ",")
            #         count = count + len(poly)
            #         index = index + 1

        if (self.hole_poly is not None):
            if isinstance(self.hole_poly[0][0], list):
                for poly in self.hole_poly:
                    self.file.write("Line Loop(" + str(index+1) + ") = {")
                    for i in range(len(poly)):
                        if (i == len(poly)-1):
                            self.file.write(str(count+i) + "}; \n")
                        else:
                            self.file.write(str(count+i) + ",")
                    count = count + len(poly)
                    index = index + 1
            else:
                self.file.write("Line Loop(" + str(index+1) + ") = {")
                for i in range(len(self.hole_poly)):
                    if (i == len(self.hole_poly)-1):
                        self.file.write(str(count+i) + "}; \n")
                    else:
                        self.file.write(str(count+i) + ",")
                count = count + len(poly)
                index = index + 1

    # Every line loop that closes creates a surface.
    # We want the surface for the moat union to be
    # different so we can take those graph vertices.
    def plane_surface(self):
        self.file.write("\n// Plane Surface \n")
        index = 0
        for key in self.cell_poly:
            if key[0] in WIRE_LIST:
                for poly in self.cell_poly[key]:
                    self.file.write("Plane Surface(" + str(index+1)
                                                     + ") = {" + str(index+1)
                                                     + "}; \n")
                    index = index + 1
            elif (key == (70, 0)):
                for poly in self.cell_poly[key]:
                    self.file.write("Plane Surface(" + str(index+1) + ") = {"
                                                     + str(index+1) + "}; \n")
                    index = index + 1

        if (self.hole_poly is not None):
            for poly in self.hole_poly:
                self.file.write("Plane Surface(" + str(index+1) + ") = {"
                                                 + str(index+1) + "}; \n")
                index = index + 1

    def physical_surface(self):
        self.file.write("\n// Physical Surface \n")
        index = 0
        for key in self.cell_poly:
            if key[0] == 80:
                for poly in self.cell_poly[key]:
                    string = "Physical Surface(" + str(index+1) + ") = {"
                    string = string + str(index+1) + "}; \n"
                    self.file.write(string)
                    index = index + 1
            if key[0] == 81:
                for poly in self.cell_poly[key]:
                    string = "Physical Surface(\"via" + str(index+1) + "\") = {"
                    string = string + str(index+1) + "}; \n"
                    self.file.write(string)
                    index = index + 1
            elif key[0] == 70:
                for poly in self.cell_poly[key]:
                    string = "Physical Surface(\"moat\") = {"
                    string = string + str(index+1) + "}; \n"
                    self.file.write(string)
                    index = index + 1
            elif key[0] == 71:
                for poly in self.cell_poly[key]:
                    string = "Physical Surface(\"jj" + str(index+1) + "\") = {"
                    string = string + str(index+1) + "}; \n"
                    self.file.write(string)
                    index = index + 1
            elif key[0] == 72:
                for poly in self.cell_poly[key]:
                    string = "Physical Surface(\"jj_gc" + str(index+1) + "\") = {"
                    string = string + str(index+1) + "}; \n"
                    self.file.write(string)
                    index = index + 1

    def extrude(self):
        self.file.write("\n// Extrude \n")
        index = 0
        for key in self.cell_poly:
            for poly in self.cell_poly[key]:
                string = "info" + str(index+1) + "[] = Extrude {0,0,t2} {Surface{"
                string = string + str(index+1) + "}; Layers{{layers1},{1}};}; \n"
                self.file.write(string)
                index = index + 1

        if (self.hole_poly is not None):
            for poly in self.hole_poly:
                self.file.write("info" + str(index+1)
                                + "[] = Extrude {0,0,t2} {Surface{"
                                + str(index+1)
                                + "}; Layers{{layers1},{1}};}; \n")
                index = index + 1

    def physicals(self):
        self.file.write('\nPhysical Point(".f -s 10E9 -e 10E9 -n 1") = {}; \n')
        self.file.write('Physical Volume(".v1 -s 0.0 -l 270E-9") = {info1[1]}; \n\n')

        index = 0
        for poly in self.hole_poly:
            self.file.write('Physical Point(".h ' + str(index) + '") = {}; \n')
            index = index + 1

        index = 0

        if (self.hole_poly is not None):
            for poly in self.hole_poly:
                self.file.write('Physical Surface(".t -p ' + str(index)
                                + '") = {info' + str(index+2)
                                + '[2],info' + str(index+2) + '[3],info'
                                + str(index+2) + '[4],info' + str(index+2)
                                + '[5]}; \n')
                index = index + 1

    def automate(self):
        self.file.write('Mesh.Algorithm = 1; \n')
        self.file.write('Mesh.CharacteristicLengthMin = 100; \n')

    def close(self):
        self.file.close()
