#!/usr/local/bin/python3

# This program, which has to be run in a directory with a coordinate file called coords (sorry, this was just a one-time thing), generates an assemble of Gaussian input files where the parameter a of the B3LYP functional varies following a numpy.linspace distribution. :)

import numpy as np

def convert(number):
    numstring = str(round(number,4))
    numstring = "".join(numstring.split("."))
    numstring = numstring + "0"*(5 - len(numstring))
    return numstring

def linegen(a,b,c):
    line = ("# opt BLYP/cc-pvtz "
           "iop(3/76=10000{}) "
           "iop(3/77={}{}) "
           "iop(3/78={}10000)".format(convert(a),convert(b),convert(1-a),convert(c)))
    return line

# testing

with open("coords", "r") as coordfile:
    coordinates = coordfile.readlines()

for a in np.linspace(0.01,0.99,20):
    with open("a" + convert(a)[:3] + "-H2O.gjf", "w") as gjf:
        gjf.write(linegen(a, 1-a, 1-a) + "\n\n")
        gjf.write("a={}, b={}, c={}".format(a, 1-a, 1-a) + "\n\n")
        gjf.write("0 1\n")
        for line in coordinates:
            gjf.write(line)
        gjf.write("\n")
