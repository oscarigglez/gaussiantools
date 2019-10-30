element_dict = {}

class Structure:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', "system")
        print("Molecule instantiated!\n")

def read_xyz(xyz):
    with open(xyz, 'r') as open_xyz:
        xyz_lines = open_xyz.readlines()[2:]
    return
