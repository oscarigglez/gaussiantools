#!/usr/local/bin/python3

import colorsys
import matplotlib.pyplot as plt
import numpy as np
import sys


class Spectrum:
    def __init__(self, filename):
        self.filename = filename
        self.id = str(filename[:-4])
        with open(filename, "r") as readfile:
            self.lines = readfile.readlines()
        for word in self.lines[0].split():
            try:
                self.inwave = float(word)
            except ValueError:
                pass
        self.inwave = round(1E7/self.inwave)
        for i in range(len(self.lines)):
            line = self.lines[i]
            if "# Spectra" in line:
                self.spectrum = self.lines[i+2:]
                break
            else:
                pass

        (self.X, self.Y, self.dY) = ([], [], [])
        for point in self.spectrum:
            point = point.split()
            self.X.append(float(point[0]))
            self.Y.append(float(point[1]))
            self.dY.append(float(point[2]))

        for i in (self.X, self.Y, self.dY):
            i = np.asarray(i)

        self.waverange = (round(self.X[0], 1), round(self.X[-1], 1))

    def printcard(self):
        print("File ID: {}\n"
              "Incident wavelength: {} nm\n"
              "Numer of points: {}\n"
              "Wavenumber range: {}-{}\n".format(self.id, self.inwave, len(self.spectrum), \
                      self.waverange[0], self.waverange[1]))

class Unfolded:
    def __init__(self, specList, rangeString=""):
        self.specList = sorted(specList, key=lambda x: x.inwave, reverse=False)
        self.specNumber = len(self.specList)
        self.colorNumber = 100
        self.palette = [0]*self.specNumber
        for i in range(self.specNumber):
            f = i/self.specNumber
            r = 0.9-f
            #print(r)
            r, g, b = colorsys.hsv_to_rgb(r, 0.9, 0.9)
            self.palette[i] = (r, g, b)

        try:
            self.waverangeList = [[float(j) for j in i.split("-")] for i in rangeString.split()]
            self.rangeNumber = len(self.waverangeList)
            self.rangeDif = np.array([i[1]-i[0] for i in self.waverangeList])
            self.minDif = np.amin(self.rangeDif)
            self.propList = [i/self.minDif for i in self.rangeDif]
        except ValueError:
            self.waverangeList = [self.specList[0].waverange]
            self.propList = [1]


    def draw(self):
        self.maxY = np.amax(np.array([np.amax(i.Y) for i in self.specList]))
        self.Yrange = self.maxY*self.specNumber
        self.Ypadding = self.Yrange*0.02
        #print(self.maxY)
        fig, axs = plt.subplots(1, len(self.waverangeList), sharey=True, gridspec_kw = {'width_ratios':self.propList})
        for i in range(len(self.waverangeList)):
            try:
                ax = axs[i]
            except TypeError:
                axs = [axs]
                ax = axs[i]
            for j in range(len(self.specList)):
                spec = self.specList[j]
                multi = self.maxY/np.amax(spec.Y)*5.0#/7.0
                Ymod = j*self.maxY
                ax.plot(spec.X, np.multiply(spec.Y, multi) + Ymod, label=spec.inwave, color=self.palette[j])
                #axs[-1].text(0.96*self.waverangeList[-1][1], self.Ypadding + Ymod, str(spec.inwave) + " nm ", color=self.palette[j])
            ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
            ax.set_xlim(left=self.waverangeList[i][0], right=self.waverangeList[i][1])
            ax.set_ylim(bottom=-self.Ypadding, top=self.Yrange+self.Ypadding)
            ax.set_xlabel(r"Wavenumber $(cm^{-1})$")
        axs[0].set_ylabel(r"Intensity $(a.u.)$")
        handles, labels = axs[-1].get_legend_handles_labels()
        axs[-1].legend(handles[::-1], labels[::-1], title=r"Incident $\lambda$", loc='center left', bbox_to_anchor=(1,0.5))

        fig.tight_layout()
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=None)
#        plt.show()

    def drawder(self):
        self.maxY = np.amax(np.array([np.amax(i.dY) - np.amin(i.dY) for i in self.specList]))
        self.Yrange = self.maxY*self.specNumber
        self.Ypadding = self.Yrange*0.02
        fig, axs = plt.subplots(1, len(self.waverangeList), sharey=True, gridspec_kw = {'width_ratios':self.propList})
        for i in range(len(self.waverangeList)):
            try:
                ax = axs[i]
            except TypeError:
                axs = [axs]
                ax = axs[i]
            for j in range(len(self.specList)):
                spec = self.specList[j]
                Ymod = j*self.maxY
                ax.plot(spec.X, spec.dY + Ymod, label=spec.inwave, color=self.palette[j])
            ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
            ax.set_xlim(left=self.waverangeList[i][0], right=self.waverangeList[i][1])
            ax.set_ylim(bottom=-self.maxY/2-self.Ypadding, top=self.Yrange-self.maxY/2+self.Ypadding)
            ax.set_xlabel(r"Wavenumber $(cm^{-1})$")
        axs[0].set_ylabel(r"Intensity $(a.u.)$")
        handles, labels = axs[-1].get_legend_handles_labels()
        axs[-1].legend(handles[::-1], labels[::-1], title=r"Incident $\lambda$", loc='center left', bbox_to_anchor=(1,0.5))

        fig.tight_layout()
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=None)
        plt.show()

    def save(self):
        plt.savefig("plot.pdf")

    def printinfo(self):
        print("Number of spectra loaded: {}\n"
              "".format(self.specNumber))

def getSpecs():
    specs = []
    for i in sys.argv[1:]:
        spec = Spectrum(i)
        specs.append(spec)
        spec.printcard()
    return specs

# Testing and Execution
rangeString = str(input("Enter your desired wavenumber range (e.g. '1000-2000', or '1000-1850 3000-4000'): "))
print("1. Draw spectra\n2. Draw derivatives")
option = int(input("Type the number of your option: "))
specs = getSpecs()
plot = Unfolded(specs, rangeString)
plot.printinfo()
if option == 1:
    plot.draw()
elif option == 2:
    plot.drawder()
else:
    pass
plot.save()

