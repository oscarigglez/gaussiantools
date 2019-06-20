#!/anaconda3/bin/python

import numpy as np
import pandas as pd
import sys

class Vib:
    def __init__(self, vib_line):
        vib_parts = vib_line.split()
        self.name = vib_parts[1]
        self.type = self.name[0]
        self.d = vib_parts[2]
        self.value = float(vib_parts[3])
        self.weight = float(vib_parts[4])
        atom_substring = self.d[self.d.find('(')+1:self.d.find(')')]
        self.atoms = [int(x) for x in atom_substring.split(',')]

class Nmode:
    def __init__(self, mode_id, wavenumber, vib_list):
        self.id = int(mode_id)
        self.wavenumber = float(wavenumber)
        self.vibs = []
        for i in range(len(vib_list)):
            self.vibs.append(Vib(vib_list[i]))

class System:
    def __init__(self, filename, mol_atoms):
        self.filename = filename
        self.id = str(filename[:-4])

        with open(filename, 'r') as readfile:
            self.lines = readfile.readlines()

        self.wavenumber_list = []
        for i in range(len(self.lines)):
            if "Frequencies" in self.lines[i]:
                self.wavenumber_list += self.lines[i].split()[2:]
            else:
                pass

        rawmodes = []
        reading_mode = False
        for i in range(len(self.lines)):
            if "Normal Mode" in self.lines[i]:
                reading_mode = True
                mode_start = i
            elif "-"*80 in self.lines[i] and reading_mode and i - mode_start > 3:
                mode_end = i
                rawmodes.append(self.lines[mode_start+4:mode_end])
                reading_mode = False
            else:
                pass

        self.modes = []
        for i in range(len(rawmodes)):
            self.modes.append(Nmode(i + 1, self.wavenumber_list[i], rawmodes[i]))
        print(len(self.modes))

        self.mol_atoms = mol_atoms

    def con(self):
        for mode in self.modes:
            mode.mol = 0
            mode.mix = 0
            mode.sur = 0
            for vib in mode.vibs:
                if all(i in self.mol_atoms for i in vib.atoms):
                    #mol += abs(vib.value)
                    vib.kind = 'molecule'
                    mode.mol += vib.weight
                elif any(i in self.mol_atoms for i in vib.atoms):
                    #mix += abs(vib.value)
                    vib.kind = 'mixed'
                    mode.mix += vib.weight
                else:
                    #sur += abs(vib.value)
                    vib.kind = 'surface'
                    mode.sur += vib.weight
            total = (mode.mol + mode.mix + mode.sur)/100.0
            mode.wmol = mode.mol/total
            mode.wmix = mode.mix/total
            mode.wsur = mode.sur/total
            print("Mode n: {}".format(mode.id))
            print("Molecule: {:.2f}, Surface: {:.2f}, Mixed: {:.2f}\n".format(mode.wmol,
                mode.wsur,
                mode.wmix))

    def makedf(self):
        df = pd.DataFrame(index=[mode.id for mode in self.modes],
                          data=list(zip([mode.wavenumber for mode in self.modes],
                                        [mode.wmol for mode in self.modes],
                                        [mode.wsur for mode in self.modes],
                                        [mode.wmix for mode in self.modes])),
                          columns=['Wn', 'Mol%', 'Sur%', 'Mix%'])
        df.index.name='Mode'
        print(df[(df['Mol%'] > 70) & (df['Sur%'] < 10) & (df['Wn'] > 1000) & (df['Wn'] < 1800)])
        df.to_csv("intmodes_TEST.csv")

# Execution
for filename in sys.argv[1:]:
    system = System(filename, list(range(1, 27)))
    system.con()
    system.makedf()
