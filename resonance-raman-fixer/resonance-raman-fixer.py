#!/anaconda3/bin/python

import sys
import pandas as pd

class System:
    def __init__(self, filename):
        self.filename = filename
        self.id = str(filename[:-4])

        with open(filename, 'r') as readfile:
            lines = readfile.readlines()
            self.lines = lines

        RamAct_list, Alpha2_list, Beta2_list = ([], [], [])

        for i in range(len(lines)):
            line = lines[i]
            if "RamAct Fr=" in line:
                RamAct_list = RamAct_list + line.split('--')[1].split()
            elif "Alpha2 Fr=" in line:
                Alpha2_list = Alpha2_list + line.split('--')[1].split()
            elif "Beta2  Fr=" in line:
                Beta2_list = Beta2_list + line.split('--')[1].split()
            elif "Using perturbation frequencies:" in line:
                self.inwave = round(45.56335/float(line.split(':')[1]))
            else:
                pass

        self.star_list = []
        for i in range(len(RamAct_list)):
            ram = RamAct_list[i]
            if ram == "************":
                self.star_list.append(i)
                try:
                    RamAct_list[i] = 45*float(Alpha2_list[i]) + 7*float(Beta2_list[i])
                except:
                    RamAct_list[i] = 10E8
            else:
                pass
        print(self.star_list)

        self.RamAct_list = RamAct_list

        for i in range(len(RamAct_list)):
            print("Mode {}:\nRamAct = {}  Alpha2 = {}  Beta2 = {}\n".format(i + 1,
                RamAct_list[i], Alpha2_list[i], Beta2_list[i]))

    def makelog(self):
        lines = self.lines
        star_count = 0
        with open("{}_FIX.log".format(self.id), 'w') as fixlog:
            for i in range(len(lines)):
                line = lines[i]
                if "RamAct Fr=" in line:
                    while "************" in line:
                        line = line.replace("************",
                                str(round(self.RamAct_list[self.star_list[star_count]], 4)))
                        star_count += 1
                else:
                    pass
                fixlog.write(line)
  
    def makedf(self):
        df = pd.DataFrame(list(zip(range(len(self.RamAct_list) + 1)[1:], self.RamAct_list)),
                columns=['Mode', '{} nm'.format(self.inwave)])
        print(df.head())
        df.to_csv('{}nm.csv'.format(self.inwave), index=False)

class Mode:
    def __init__(self):
        pass




# Execution
for out in sys.argv[1:]:
    system = System(out)
    system.makelog()
