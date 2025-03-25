from pyteomics import mzml
import os, csv, time
import numpy as np
from scipy.integrate import trapezoid
from peak_pick import peak_pick
from pathlib import Path
import settings
from tqdm import tqdm

# Log script execution time
st = time.time()

def trace(path: str, features: list, MZ_AXIS: np.ndarray) -> np.ndarray:
    tic = []                            # Placeholder data structures 
    scans = mzml.MzML(path)
    data = np.empty((len(features)+1, len(scans)))

    j = 0
    with tqdm(total=len(scans), desc="Processing scans...") as pbar:
        for scan in scans:
            tic.append(scan['total ion current'])
            mz_array = np.ndarray.tolist(scan['m/z array'])
            intensity_array = np.ndarray.tolist(scan['intensity array'])
            int_interp = np.interp(MZ_AXIS, mz_array, intensity_array) # Interpolate intensity linearly for each scan from mz_array and intensity_array onto MZ_AXIS
            data[0][j] = scan['index']
            i = 1
            for feature in features:
                if i < len(features)+2:
                    data[i][0] = round(np.median(feature.mz), 4)
                feature_int = int_interp[feature.width[0]:feature.width[1]]
                time_trace = trapezoid(feature_int)
                data[i][j] = time_trace
                i += 1
            j += 1
            pbar.update(1)
    trc = np.ndarray.tolist(data)

    trc.insert(1, tic)

    return trc

def time_trace(path: str, MZ_AXIS: np.ndarray) -> np.ndarray:
    '''
    Takes an mzML file, a feature list, and a predefined m/z axis as arguments, and returns a time trace of these features. 
    The time trace is produced by linearly interpolating the intensity of every scan onto a new, uniformly-spaced m/z axis provided as an argument to the function,
    and integrating this intensity within the boundaries of m/z values of every feature in the feature list.
    
    Parameters
    ----------
    path: str
        Path to the source mzML file.
    
    features: list
        List of floats to be used for feature tracing.
        
    MZ_AXIS: np.ndarray
        m/z axis predefined at the top of the preprocessing script (preprocess.py).
    
    Returns
    -------
    trc: np.ndarray
        Numpy ndarray containing all the m/z values from features and their respective time traces.
        First row is scan numbers, second row is the total ion current at each scan.
        All subsequent rows are integrated feature intensities at each scan.
    '''
    path = Path(path)
    # Pick peaks on the composite spectra
    print("Performing peak picking...")
    
    composite_pos = np.genfromtxt(path.parent.absolute() / "composite_spectrum_pos.csv", delimiter=',')
    composite_neg = np.genfromtxt(path.parent.absolute() / "composite_spectrum_neg.csv", delimiter=',')

    peaklist_pos = peak_pick(composite_pos, MZ_AXIS)
    peaklist_neg = peak_pick(composite_neg, MZ_AXIS)

    filelist = [file for file in os.listdir(path.parent.absolute()) if file.lower().endswith(".mzml")]

    # Process the time traces for every peak found
    counter = 0
    for file in filelist:
        counter += 1
        print(f"Finding time traces for: {file}, {counter} out of {len(filelist)}...")
        if "pos" in str(file):
            data = trace(str(path.parent.absolute() / file), peaklist_pos, MZ_AXIS)
            with open(path / "{}.csv".format(file.lower()).replace('.mzml', "_trace"), "w+", newline='') as trace_csv:
                writer = csv.writer(trace_csv)
                for item in data:
                    writer.writerow(item)
        elif "neg" in str(file):
            data = trace(str(path.parent.absolute() / file), peaklist_neg, MZ_AXIS)
            with open(path / "{}.csv".format(file.lower()).replace('.mzml', "_trace"), "w+", newline='') as trace_csv:
                writer = csv.writer(trace_csv)
                for item in data:
                    writer.writerow(item)

    print("Done.")

# Print execution time 
et = time.time()
elapsed_time = et - st
print("Time traces written in: ", round(elapsed_time, 2), " seconds.")
