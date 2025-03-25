from pyteomics import mzml
import os
from read_mzml import read_mzml
import time
import numpy as np
from pathlib import Path
import sys
import settings
from tqdm import tqdm

def average(path: str, mz_axis: np.ndarray) -> np.ndarray:
    '''
    Reads in .mzml files from path, using the Pyteomics library. Performs averaging of all spectral scans
    by linearly interpolating their intensities over a resampled, linearly-spaced
    m/z axis. Returns the averaged mass spectra in a 2-dimensional array: m/z, intensity.
    
    Parameters
    -----------
    path: path
        .mzml path object to be read by pyteomics' MzML object constructor.
    
    mz_axis: NDArray
        Numpy NDArray containing the linearly-spaced new m/z axis to be interpolated over.
        
    Returns
    -------
    data_matrix: NDArray
        2 x n (n = number of m/z values) matrix of averaged mass spectra in the format: m/z value, average intensity.
    '''
    
    path = Path(path)
    
    # Log script execution time
    st = time.time()
    
    print(f"Executing on filepath: ${path}...")
    
    # Find and list all the mzML files found on path
    filelist = [file for file in os.listdir(path.parent.absolute()) if file.lower().endswith(".mzml")]

    counter = 0
    for file in filelist:
        counter += 1
        print(f"Averaging spectra for: {file}, {counter} out of {len(filelist)}...")
        
        mzml_path = mzml.MzML(str(path.parent.absolute() / file))  # Instantiate the MzML reader object
        intensities = np.zeros(len(mz_axis))
        with tqdm(total=len(mzml_path)) as pbar:
            for j in range(0, len(mzml_path)):
                if mzml_path[j]['ms level'] == 1:
                    mz_array = np.ndarray.transpose(mzml_path[j]['m/z array'])                  # Get m/z values from the MzML path
                    intensity_array = np.ndarray.transpose(mzml_path[j]['intensity array'])     # Get their intensities 
                    int_interp = np.interp(mz_axis, mz_array, intensity_array, left=0, right=0) # Interpolate continuous intensity signal from discrete m/z 
                    intensities += int_interp                                                   # and intensities over the new, linear m/z axis
                else:
                    continue
                pbar.update(1)

        print("Saving to file avg_{}.csv...".format(file).replace('.mzml', ""))
        avg_intensity = intensities / len(mzml_path)   # Average the signal
        data_matrix = np.array((mz_axis, avg_intensity), dtype=np.float64)
        data_matrix = np.transpose(data_matrix)                      
        
        # Save background-corrected, resampled m/z-intensities
        with open(path / "avg_{}.csv".format(file).replace('.mzml', ""), "w+") as average_csv:
            np.savetxt(average_csv, data_matrix, delimiter=",", encoding='utf-8')


    # Print execution time 
    et = time.time()
    elapsed_time = et - st
    print("Averaged in: ", round(elapsed_time, 2), " seconds.")