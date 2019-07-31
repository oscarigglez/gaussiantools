#!/anaconda3/bin/python

import sys
import numpy as np
import pandas as pd


class System:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', "system")
        self.ints = {}
        print("System instantiated!\n")


    def get_wn(self, filename):
        with open(filename, 'r') as openfile:
            lines = openfile.readlines()

        self.wn = []
        for i in range(len(lines)):
            line = lines[i]
            if "Frequencies --" in line:
                self.wn += [float(x) for x in line.split()[2:]]
            else:
                pass


    """
    def load_optfreq(self, filename):
        with open(filename, 'r') as openfile:
            lines = openfile.readlines()

        self.ints['SL'] = []
        for i in range(len(lines)):
            line = lines[i]
            if "Raman Activ --" in line:
                self.ints['SL'] += line.split()[3:]
            else:
                pass
    """


    def load_raman(self, filename):
        with open(filename, 'r') as openfile:
            lines = openfile.readlines()

        self.ints['SL'] = []
        for i in range(len(lines)):
            line = lines[i]
            if "Raman Activ --" in line:
                self.ints['SL'] += [float(x) for x in line.split()[3:]]
            else:
                pass


    def load_rr(self, filename):
        with open(filename, 'r') as openfile:
            lines = openfile.readlines()

        tmp = []
        for i in range(len(lines)):
            line = lines[i]
            if "RamAct Fr= 1--" in line:
                tmp += [float(x) for x in line.split("--")[1].split()]
            elif "Using perturbation frequencies:" in line:
                in_wl = round(45.56335/float(line.split(':')[1]))
            else:
                pass
        self.ints["{}nm".format(in_wl)] = tmp


    def load_intmodes(self, filename, mol_atoms):
        with open(filename, 'r') as openfile:
            lines = openfile.readlines()

        rawmodes = []
        reading_mode = False
        for i in range(len(lines)):
            line = lines[i]
            if "Normal Mode" in line:
                reading_mode = True
                mode_start = i
            elif "-"*80 in line and reading_mode and i - mode_start > 3:
                mode_end = i
                rawmodes.append(lines[mode_start+4:mode_end])
                reading_mode = False
            else:
                pass

        self.intmodes = {'mol%':[], 'mix%':[], 'sur%':[]}
        for mode in rawmodes:
            mol, mix, sur = (0, 0, 0)
            for vib in mode:
                vib_parts = vib.split()
                desc = vib_parts[2]
                atom_substring = desc[desc.find('(')+1:desc.find(')')]
                atoms = [int(x) for x in atom_substring.split(',')]
                value = float(vib_parts[3])

                if all(i in mol_atoms for i in atoms):
                    mol += abs(value)
                elif any(i in mol_atoms for i in atoms):
                    mix += abs(value)
                else:
                    sur += abs(value)

            total = (mol + mix + sur)/100
            wmol, wmix, wsur = np.array([mol, mix, sur])/total
            self.intmodes['mol%'].append(wmol)
            self.intmodes['mix%'].append(wmix)
            self.intmodes['sur%'].append(wsur)


    def make_df(self):
        df = pd.concat([pd.DataFrame(data=np.arange(1, len(self.wn) + 1), columns=['mode']),
                        pd.DataFrame(data=self.wn, columns=['wn']),
                        pd.DataFrame(data=self.intmodes),
                        pd.DataFrame(data=self.ints)],
                       axis=1)
        df.set_index('mode', inplace=True)
        try:
            nm_cols = [col for col in df.columns if "nm" in col]
            print(nm_cols)
            for col in nm_cols:
                df['{} ef'.format(col)] = np.log10(df[col]/df['SL'])
        except:
            pass
        print(df.head())
        print(df.info())
        df.to_csv("{}.csv".format(self.name))


# Execution and testing
"""
sys = System(name="PN")
sys.get_wn("pn-system/rr_466nm.log")
sys.load_raman("pn-system/sl.log")
sys.load_rr("pn-system/rr_466nm.log")
sys.load_rr("pn-system/rr_569nm.log")
sys.load_rr("pn-system/rr_581nm.log")
sys.load_intmodes("pn-system/intmodes.log", list(range(1, 27)))
sys.make_df()
"""

name = input("Enter a name for your system: ")
wn = input("Enter the path of the wn file: ")
intmodes = input("Enter the path of the intmodes file: ")
mol_atom_number = int(input("How many atoms belong to the molecule?: "))
sl = input("Enter the path of the SL file: ")
rr_basename = input("Enter the base name of your rr files as 'whatever-system-{}nm.out': ")
rr_range = input("Enter the starting, ending and step values for your laser as '300 500 3': ").split()
rr_range = [int(num) for num in rr_range]

sys = System(name=name)
sys.get_wn(wn)
sys.load_intmodes(intmodes, list(range(1, mol_atom_number + 1)))
sys.load_raman(sl)
for wl in np.arange(rr_range[0], rr_range[1], rr_range[2]):
    sys.load_rr(rr_basename.format(wl))
sys.make_df()
