import numpy as np
from itertools import combinations

element_dict = {}

def find_normal(a, b, c):
    """
    Finds the normal vector to a plane defined by a set a set of three points
    """
    dir = np.cross((b - a), (c - a))
    norm = dir/np.linalg.norm(dir)
    return norm

class Structure:
    def __init__(self, elements, coords, **kwargs):
        self.name = kwargs.get('name', "system")
        self.elements = elements
        self.coords = coords
        self.atomlist = list(range(len(self.elements)))
        print("Molecule instantiated!\n")

    def find_center(self):
        x = self.coords[:,0].mean()
        y = self.coords[:,1].mean()
        z = self.coords[:,2].mean()
        self.center = np.array([x, y, z])

    def find_axis(self, print_info=False):
        combs = combinations(self.atomlist, 3)
        unique_combs = list(set(combs))
        norm_list = []
        for comb in unique_combs:
            a = self.coords[comb[0],:]
            b = self.coords[comb[1],:]
            c = self.coords[comb[2],:]
            norm = find_normal(a, b, c)
            norm_list.append(norm)
            if print_info:
                print("atoms {}, {} and {}: {} normal".format(comb[0],
                                                              comb[1],
                                                              comb[2],
                                                              norm))
        norm_array = np.array(norm_list)
        norm_mean = np.mean(norm_array, axis=0)
        self.main_axis = norm_mean/np.linalg.norm(norm_mean)
        #print(self.main_axis, np.linalg.norm(self.main_axis))

def read_xyz(xyz):
    with open(xyz, 'r') as open_xyz:
        xyz_lines = open_xyz.readlines()[2:]
    element_list = []
    xyz_list = []
    for line in xyz_lines:
        element_list.append(line.split()[0])
        xyz_list.append([float(coord) for coord in line.split()[1:]])
    return (element_list, np.asarray(xyz_list))
