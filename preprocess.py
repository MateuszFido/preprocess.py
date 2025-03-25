'''
Last modified: 2025-Mar-25
@author: Mateusz Fido, mateusz.fido@org.chem.ethz.ch
ETH Zürich

This script reads in and parses mzML files using the Pyteomics
metabolomics library for Python. It calculates average mass spectra
by linearly interpolating their intensity on a resampled m/z axis 
with a given resolution. Based on these, it creates composite mass spectra 
from all measurements in a given polarity mode.

It then performs peak picking on the composite spectra by using the SciPy
library function find_peaks(), using peak height as cut-off criteria, and stores
peak data that can then be passed into other functions.

Subsequently, it calculates time traces of all the features by integrating the
interpolated intensity within the m/z boundaries of a peak. 

Finally, it creates a Pandas DataFrame of the intensity matrix of n samples x m features,
filters out features not present in at least X% of all samples (user-modifiable), 
and writes the DataFrame to a .csv file. 

References:
===========
Matlab Code of Jiayi Lan and Miguel de Figueiredo 
Python Code of Cedric Wüthrich
https://pyteomics.readthedocs.io/en/latest/index.html
'''

import os, time
from pathlib import Path
import numpy as np
import csv
import shutil
from average import average
from peak_pick import peak_pick
from read_mzml import read_mzml
from time_trace import time_trace
from composite_spectrum import composite_spectrum
from settings import MZ_AXIS
from intensity_matrix import intensity_matrix

# Log script execution time
st = time.time()

# Defined when executing the script from a batch module or the console
PATH = Path(os.sys.argv[1])   
print(f"Found path ${PATH}...")

def clear():
    '''
    Helper function. Clears the console for better readability.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def main(path):
    """
    Main function to process mzML files, generate composite spectra, calculate time traces, 
    and construct an intensity matrix. It ensures the necessary directory structure is in place, 
    performs file cleanup, and invokes various processing steps.

    Parameters
    ----------
    path: Path
        Path to the directory containing mzML files to be processed.

    Returns
    -------
    None
    """
    clear()
    print("""Open-source metabolomics preprocessing script for HRMS data. Python v.3.11. and above
    Distributed under the MIT License. 
    Last modified: 2025-Mar-25
    @author: Mateusz Fido, github.com/MateuszFido
    ETH Zürich\n
    Disclaimer: This workload is computationally intensive and not designed for consumer hardware.
    The pipeline should be run on a high-performance computing cluster.\n""")

    # Prepare the directory structure
    if "average" in os.listdir(path.absolute()):
        pass
    else:
        os.mkdir(path.absolute() / "average")
    if "time_traces" in os.listdir(path.absolute()):
        pass
    else:
        os.mkdir(path.absolute() / "time_traces")

    average(path / "average", MZ_AXIS)

    # Average the averaged spectra to create a composite spectrum of all mzML files on the file path
    if "composite_spectrum" in os.listdir(path.parent.absolute()):
        pass
    else:
        composite_spectrum(path, MZ_AXIS)
    
    # Construct the respective time traces 
    time_trace(path / "time_traces", MZ_AXIS)

    # Write the intensity matrix of all samples and all peaks
    intensity_matrix(path)

# Instantiate the script 
main(PATH)

# Print execution time 
et = time.time()
elapsed_time = et - st
print("Execution time: ", round(elapsed_time, 2), " seconds.")


