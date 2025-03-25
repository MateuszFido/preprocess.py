import numpy as np
from scipy.signal import find_peaks, peak_widths, peak_prominences
import matplotlib.pyplot as plt

class Peak():
    '''Support class for Peak objects. \n
    
    Properties:
    -----------
    mz: np.ndarray
        Numpy array of mz values computed from indices of intensity axis, returned by scipy.find_peaks().
    index: int
        Index of the peak centroid. 
    width: list 
        Peak boundaries calculated at 0.9 of peak amplitude.
        '''

    def __init__(self, index: int, mz: np.ndarray, width: list):
        self.index = index
        self.mz = mz
        self.width = width

    def __str__(self):
        return f"Feature with m/z range: {self.mz} and intensity range: {self.int_range} "

def peak_pick(spectrum: np.ndarray, MZ_AXIS: np.ndarray) -> list:
    '''
    Using the SciPy find_peaks() function, performs peak picking and integration of peaks from average mass spectra.
        
    Parameters
    ----------
    spectrum: np.ndarray
        Composite spectrum on which to pick peaks.
    
    MZ_AXIS: np.ndarray
        Linear m/z axis as the reference for peak width and intensity.
    
    Returns
    -------
    
    peaklist: list 
        List of Peak objects.
    '''

    peaklist = []

    # Transpose into rows and get the intensity array

    # Transpose into rows and get the intensity array
    corr_intensity = spectrum.transpose()[1]
    # Find peaks by cutting off at a given intensity to remove noise
    peaks = find_peaks(corr_intensity, height=1000, distance=50)

    # Find widths at the base of the peak 
    widths, width_heights, left, right = peak_widths(corr_intensity, peaks[0], rel_height=0.9)
    counter = 0
    # For all peaks found, extract their properties and append the Peak to peaklist
    for peak_idx in peaks[0]:
        mz = MZ_AXIS[int(np.floor(left[counter])):int(np.ceil(right[counter]))]   # m/z range
        width = [int(np.floor(left[counter])), int(np.ceil(right[counter]))]      # left and right base
        peak = Peak(peak_idx, mz, width)
        counter += 1
        peaklist.append(peak)

    print(f"Found {len(peaklist)} peaks.")

    '''
    Graphing interface for debugging purposes

    print(peaks)
    fig = plt.figure()
    ax = fig.subplots()
    plt.plot(MZ_AXIS, corr_intensity)
    ax.scatter(MZ_AXIS[peaks[0]], peaks[1]['peak_heights'], color = 'r', s=15)
    ax.legend()
    ax.grid()
    plt.show()
    '''

    return peaklist

