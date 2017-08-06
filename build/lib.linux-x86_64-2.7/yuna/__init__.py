import os
import yuna.utils.read


def yunacall(gds, ldf):
    os.chdir('..')
    viewgds = True

    layers = yuna.utils.read.ldf(ldf)
    write = yuna.utils.write.Write(viewgds)

    generate_gds(write, gds, layers, ldf)
