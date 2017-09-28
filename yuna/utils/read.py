import numpy as np
import os
import operator
import json

import yuna.utils.tools
import yuna.utils.system

from pprint import pprint
from itertools import chain


def config(config_file):
    """
        Reads the config file that is written in
        JSON. This file contains the logic of how
        the different layers will interact.
    """

    data = None
    with open(config_file) as data_file:
        data = json.load(data_file)
    return data


def ldf(process):
    """
        1)  Hypres design rules.

            Layer    GDS    Description
            -----    ---    -----------
            M0       30     Ground
            M1       1      Wire layer 1
            M2       6      Wire layer 2
            M3       10     Wire layer 3
            I1       3      Via M2 to M1
            I2       8      Via M2 to M3

        2)  AIST design rules.

            Layer    GDS    Description
            -----    ---    -----------
            GP       1      Ground plane
            GC       2      Contact hole between GP and BAS
            RES      3      Resistor
            BAS      4      Lower electrode of JJ and lower wiring
            JP       5      Protection for JJ
            JJ       6      Josephson junction
            BC       7      Contact hole between BAS and COU
            COU      8      Upper wiring
            RC       9      Contact hole between RES and BAS
            JC       10     Contact hole between JJ and COU
            CC       11     Contact hole between COU and CTL
            CTL      12     Top wiring or shield layer

            Notes
            -----
            * JJ always goes down to BAS.
            * Does the JJ connect CTL to BAS?
              Or just COU to BAS?s

        Parameters:
            file_name : LDF file name

        TODO:
            Still have to read the $Parameters part.
    """

    layers_dict = dict()

    bool_parameters = False
    bool_layer = False

    cwd = os.getcwd()
    ldf_file = cwd + '/tests/ldf/' + process + '.ldf'

    with open(ldf_file, 'r') as fil:
        data = fil.readlines()

    temp_dict = dict()

    for line in data:
        words = line.split()

        if len(words[0]) > 0:
            if words[0] == '$Parameters':
                bool_parameters = True
            if words[0] == '$EndParameters':
                bool_parameters = False

            if words[0] == '$Layer':
                bool_layer = True
            if words[0] == '$EndLayer':

                layers_dict[int(temp_dict['Number'])] = temp_dict
                temp_dict = {}

                bool_layer = False

            if bool_layer:
                if (words[0][0] != '*') and (words[0][0] != '$'):
                    temp_dict[words[0]] = words[2]

            # if (bool_parameters):

    # sorted_key = sorted(layers_dict.items(), key=operator.itemgetter(0))
    # layers_dict = dict(sorted_key)

    # if auron.utils.system.verbose:
        # print(auron.utils.tools.pretty(layers_dict))

    return layers_dict
    
    
    
    
    
    
    
    
    
    
    
    
    
