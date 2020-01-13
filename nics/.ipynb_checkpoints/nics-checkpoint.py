import moleculetools as mt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def build_predictors(x, y):
    x2 = np.square(x)
    y2 = np.square(y)
    x4 = np.square(x2)
    y4 = np.square(y2)
    xy = np.multiply(x, y)
    x2y2 = np.square(xy)
    return np.column_stack([x, y, x2, y2, x4, y4, xy, x2y2])

def make_grid(radius=5, density=50):
    spacing = np.linspace(-radius, radius, density)
    X2 = np.meshgrid(spacing, spacing)
    grid_shape = X2[0].shape
    return np.reshape(X2, (2, -1)).T

def write_gjf(molecule):
    link0 = "# nmr=giao b3lyp/6-31G* nosymm geom=connectivity guess=huckel"

# Execution
