import numpy as np
from pathlib import Path
from peak_pick import peak_pick
import settings
import os, sys, time

def composite_spectrum(path: str, MZ_AXIS: np.ndarray) -> np.ndarray:
    '''
    Average all the averaged spectra into one composite spectrum for all mzML files on the given file path (for each polarity mode).
    
    Parameters
    ----------
    path: str
        Path to the averaged .csv files created from the mzML files. 
    
    MZ_AXIS: np.ndarray
        Numpy NDArray containing the linearly-spaced new m/z axis.
        
    Returns
    -------
    spectrum_pos: np.ndarray
        An array containing the composite spectrum of all measurements found on the file path in the positive ion mode.
    
    spectrum_neg: np.ndarray
        An array containing the composite spectrum of all measurements found on the file path in the negative ion mode.
    '''
    
    # Log script execution time
    st = time.time()
    
    path = Path(path)
    # Average the averaged spectra to create a composite spectrum of all mzML files on the file path
    print("Preparing the composite spectrum:", flush=True)

    with open(path / "composite_spectrum_pos.csv", "w+") as spectrum_pos, open(path / "composite_spectrum_neg.csv", "w+") as spectrum_neg:
        
        # Prepare arrays for intensity values
        avg_int_pos = np.zeros(len(MZ_AXIS))
        num_pos = 0
        avg_int_neg = np.zeros(len(MZ_AXIS))
        num_neg = 0
        
        # Process all directories
        for root, dirs, files in os.walk(path):
            for file in files:
                if 'avg' in file:
                    file_path = Path(root) / file
                    print(f"Processing file {file_path}...", flush=True)
                    data = np.genfromtxt(file_path, delimiter=',')
                    corr_intensity = data.transpose()[1]
                    if 'pos' in file:
                        num_pos += 1
                        avg_int_pos += corr_intensity
                    elif 'neg' in file:
                        num_neg += 1
                        avg_int_neg += corr_intensity
       
        avg_int_pos /= num_pos
        avg_int_neg /= num_neg
        composite_pos = np.array((MZ_AXIS, avg_int_pos))
        composite_neg = np.array((MZ_AXIS, avg_int_neg))
        composite_pos = np.transpose(composite_pos)
        composite_neg = np.transpose(composite_neg)
        
        np.savetxt(spectrum_pos, composite_pos, delimiter=",", encoding='utf-8')
        np.savetxt(spectrum_neg, composite_neg, delimiter=",", encoding='utf-8')
        
        # Print execution time 
        et = time.time()
        elapsed_time = et - st
        print("Composite spectrum created in: ", round(elapsed_time, 2), " seconds.")
    
