import numpy as np

# Define the hard-coded m/z axis, used throughout the whole script
MZ_MIN = 50
MZ_MAX = 500 
RES = 0.0001
DATA_POINTS = int((MZ_MAX - MZ_MIN)/RES)

global MZ_AXIS

MZ_AXIS = np.linspace(MZ_MIN, MZ_MAX, DATA_POINTS, dtype=np.float64)


