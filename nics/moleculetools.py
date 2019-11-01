import numpy as np
from itertools import combinations

element_dict = {}

def unit_vector(vector):
    """
    Returns the unit vector of vector
    """
    return vector/np.linalg.norm(vector)

def angle_between(u, v):
    """
    Returns the angle in radians between vectors u and v
    """
    u_u = unit_vector(u)
    v_u = unit_vector(v)
    return np.arccos(np.clip(np.dot(u_u, v_u), -1, 1))

def cos_between(u, v):
    """
    Returns the angle in radians between vectors u and v
    """
    u_u = unit_vector(u)
    v_u = unit_vector(v)
    return np.clip(np.dot(u_u, v_u), -1, 1)

def find_normal(a, b, c):
    """
    Finds the normal unit vector to a plane defined by a set of three points
    """
    dir = np.cross((b - a), (c - a))
    normal = unit_vector(dir)
    return normal

def calc_rot_matrix(current_axis, desired_axis, points=None):
    rot_axis = np.cross(current_axis, desired_axis)
    w = unit_vector(rot_axis)
    wx, wy, wz = w
    as_w = np.array([[  0, -wz,  wy],
                     [ wz,   0, -wx],
                     [-wy,  wx,   0]])
    ang = angle_between(current_axis, desired_axis)
    cos = cos_between(current_axis, desired_axis)
    sin = np.sqrt(1 - cos**2)
    R = np.identity(3) + as_w*sin + np.square(as_w)*(1 - cos)
    return R

class Structure:
    def __init__(self, atoms, coords, **kwargs):
        self.name = kwargs.get('name', "system")
        self.atoms = atoms
        self.coords = coords
        self.natoms = len(self.atoms)
        self.atomlist = list(range(self.natoms))
        print("Molecule instantiated!\n")

    def find_center(self):
        x = self.coords[:,0].mean()
        y = self.coords[:,1].mean()
        z = self.coords[:,2].mean()
        self.center = np.array([x, y, z])

    def translate_to_center(self):
        trans_matrix = np.matmul(np.ones((self.natoms, 1)),
                                 np.reshape(self.center, (1, 3)))
        self.coords = self.coords - trans_matrix
        self.find_center()

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
        norm_array = np.array(norm_list)
        norm_mean = np.mean(norm_array, axis=0)
        self.main_axis = unit_vector(norm_mean)

    def rotate_to_z(self):
        z = np.array([0, 0, 1])
        rot_matrix = calc_rot_matrix(self.main_axis, z)
        self.coords = rot_matrix.dot(self.coords.T).T
        self.find_axis()

def read_xyz(xyz):
    with open(xyz, 'r') as open_xyz:
        xyz_lines = open_xyz.readlines()[2:]
    atom_list = []
    xyz_list = []
    for line in xyz_lines:
        atom_list.append(line.split()[0])
        xyz_list.append([float(coord) for coord in line.split()[1:]])
    return (atom_list, np.asarray(xyz_list))
