#!/usr/local/bin/python3

import logging
import numpy as np
import matplotlib.pyplot as plt
import sys
from mpl_toolkits import mplot3d

class Atom:
    def __init__(self, n, symbol, x, y , z):
        self.n = n
        self.symbol = symbol
        self.x = x
        self.y = y
        self.z = z
        self.coords = np.array([self.x, self.y, self.z])

class Structure:
    def __init__(self, filename):
        self.filename = filename
        self.id = str(filename[:-4])
        with open(filename, "r") as coord_file:
            self.coord_lines = coord_file.readlines()[2:]
        self.atoms = []
        for i in range(len(self.coord_lines)):
            line = self.coord_lines[i].split()
            self.atoms.append(Atom(i + 1, line[0],
                                    float(line[1]),
                                    float(line[2]),
                                    float(line[3])))
        x = np.average([atom.x for atom in self.atoms])
        y = np.average([atom.y for atom in self.atoms])
        z = np.average([atom.z for atom in self.atoms])
        self.center = np.array([x, y, z])

    def printcard(self):
        print("File ID: {}\n"
              "Number of atoms: {}\n"
              "Center located at {}".format(self.id,
                                            len(self.atoms),
                                            self.center))

    def get_surface(self):
        plane_atoms = input("Please type the number "
                             "of 3 atoms separated by spaces: ")
        (a, b, c) = [self.atoms[int(i) - 1].coords
                     for i in plane_atoms.split()]
        base = get_base(a, b, c)
        dist = float(input("Distance to the molecular plane in Angstroms: "))
        dens = float(input("Number of points per square Angstrom: "))
        (l1, l2) = [float(i) for i in input("Type the dimensions of the rectangle: ").split()]
        self.dir1, self.dir2 = rect_surf(self.center, base, dist, dens, l1, l2)
        surfile = open("{}.sur".format(self.id), "w")
        points = []
        for i in self.dir1:
            for j in self.dir2:
                surfile.write("    ".join([str(i), str(j)] + ["\n"]))
                point = self.center + i*base[1] + j*base[2] + base[0]*dist
                points.append(point)
        surfile.close()
        self.surface = [Atom(i, "Bq", points[i][0], points[i][1], points[i][2])
                        for i in range(len(points))]

    def write_gjfs(self):
        link0 = "# nmr=giao b3lyp/6-31G* nosymm geom=connectivity guess=huckel"
        with open("{}.gjf".format(self.id), "w") as gjf:
            gjf.write("{}\n\ninput\n\n0 1\n".format(link0))
            for atom in self.atoms:
                #gjf.write("    ".join([atom.symbol] +
                #          [str(i) for i in [atom.x, atom.y, atom.z]] + ["\n"]))
                gjf.write("{}    {:f}    {:f}    {:f}\n".format(atom.symbol, atom.x, atom.y, atom.z))
            for i in range(len(self.surface)):
                atom = self.surface[i]
                gjf.write("    ".join([atom.symbol] +
                          [str(i) for i in [atom.x, atom.y, atom.z]] + ["\n"]))
            gjf.write("\n")
            for i in range(len(self.atoms) + len(self.surface)):
                gjf.write("{}\n".format(i + 1))
            gjf.write("\n")
            with open("{}-sur.xyz".format(self.id), "w") as xyz:
                xyz.write(str(len(self.atoms) + len(self.surface)) + "\n\n")
                for atom in self.atoms:
                    xyz.write("{}    {:f}    {:f}    {:f}\n".format(atom.symbol, atom.x, atom.y, atom.z))
                for i in range(len(self.surface)):
                    atom = self.surface[i]
                    xyz.write("    ".join([atom.symbol] +
                              [str(i) for i in [atom.x, atom.y, atom.z]] + ["\n"]))
                xyz.write("\n")

class PlotData:

    def __init__(self, surfile, logfile):
        self.surfile = surfile
        self.logfile = logfile
        self.id = logfile[:-4]
        self.read_sur()
        self.read_log()

    def read_sur(self):
        with open(self.surfile, "r") as opensur:
            surlines = opensur.readlines()
        self.xdata = np.array([float(line.split()[0]) for line in surlines])
        self.ydata = np.array([float(line.split()[1]) for line in surlines])

    def read_log(self):
        with open(self.logfile, "r") as openlog:
            loglines = openlog.readlines()
        self.isodata = -np.array([float(line.split()[4])
                                 for line in loglines
                                 if "Bq   Isotropic" in line])
        for i in range(len(self.isodata)):
            item = self.isodata[i]
            if abs(item) > 2000:
                self.isodata[i] = item/abs(item)

    def draw2d(self):
        f_size = 16
        plt.rc("font", size = f_size)          # controls default text sizes
        plt.rc("axes", titlesize = f_size)     # fontsize of the axes title
        plt.rc("axes", labelsize = f_size)     # fontsize of the x and y labels
        plt.rc("xtick", labelsize = f_size)    # fontsize of the tick labels
        plt.rc("ytick", labelsize = f_size)    # fontsize of the tick labels
        plt.rc("legend", fontsize = f_size)    # legend fontsize
        plt.rc("figure", titlesize = f_size)   # fontsize of the figure title
        fig, ax = plt.subplots()
        plt.rcParams["font.family"] = "sans-serif"
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
        ax.margins(0,0)
        ax.axis("scaled")
        ax.set_xlim(np.amin(self.xdata), np.amax(self.xdata))
        ax.set_ylim(np.amin(self.ydata), np.amax(self.ydata))
        plt.xlabel(r"d ($\AA$)")
        plt.ylabel(r"d ($\AA$)")
        #im = ax.tricontourf(self.xdata, self.ydata, self.isodata, 50, cmap="seismic")
        plt.tricontourf(self.xdata, self.ydata, self.isodata, 50, cmap="seismic")
        plt.colorbar(extend="both", label="NICS (ppm)")
        plt.clim(-np.amax(abs(self.isodata)), np.amax(abs(self.isodata)))
        plt.savefig("{}.pdf".format(self.id), bbox_inches = "tight", pad_inches = 0)

def get_base(c1, c2, c3):
    v1 = c2 - c1
    v2 = c3 - c1
    cp = np.cross(v1, v2)
    bn = -cp/np.linalg.norm(cp)
    b1 = v1/np.linalg.norm(v1)
    cp = np.cross(bn, b1)
    b2 = cp/np.linalg.norm(cp)
    return np.array([bn, b1, b2])

def rect_surf(center, base, dist, dens, l1, l2):
    area = l1*l2
    N = int(area*dens)
    c1 = l1/(l1 + l2)
    c2 = l2/(l1 + l2)
    m1 = int(np.sqrt(N/(c1/c2)))
    m2 = int(m1*c1/c2)
    dir1 = np.linspace(0, l1, m1) - l1/2
    dir2 = np.linspace(0, l2, m2) - l2/2
    trueN = m1*m2
    print("Linear density in direction 1 is {} ({} points over {} Angstrom)\n"
          "Linear density in direction 2 is {} ({} points over {} Angstrom)\n"
          "Total surface density is {} ({} points over {} square Angstrom)"
          "".format(m1/l1, m1, l1, m2/l2, m2, l2, trueN/(area), trueN, area))
    return dir1, dir2

# UI
print("Hi! What do you wanna do?\n"
      "1. Generate a surface and a gjf from a xyz coordinate file\n"
      "2. Plot the results of a calculation")
option = int(input("> "))
if option == 1:
    structure = Structure(input("Type the full name of the xyz file: "))
    structure.printcard()
    structure.get_surface()
    structure.write_gjfs()
elif option == 2:
    surfile, logfile = str(input("Type the full names of the sur and log files, "
                                "separated by a space: ")).split()
    dataobject = PlotData(surfile, logfile)
    dataobject.draw2d()
