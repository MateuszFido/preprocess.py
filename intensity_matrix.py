import os, time
import numpy as np
import pandas as pd
from pathlib import Path
from pandas.errors import EmptyDataError
from tic_correlation import tic_correlate

# Log script execution time
st = time.time()

def intensity_matrix(path: str):
    '''
    Creates a Pandas DataFrame and writes it into a .csv file containing an intensity matrix
    of shape n x m, where n - samples (files), m - features. The file is saved in the same path
    as the timetraces provided through path.
    
    Parameters
    ----------
    path: str 
        String containing the path to timetraces of processed features. 
    
    Returns
    -------
    None
    '''
    
    print(f"Running intensity matrix on {path}...")
    
    samples = {}

    filelist_csv = [timetrace for timetrace in os.listdir(path / "time_traces") if timetrace.endswith("_trace.csv") and not timetrace.startswith("~")]
    for file in filelist_csv:
        features = {}
        try:
            if "pos" in file or "neg" in file:
                # read contents
                data = np.genfromtxt(path / "time_traces" / file, delimiter=",") 
                # iterate through all the features
                for i in range(0, len(data)-2):    # skip 2 first lines: 1st is scan ID, 2nd is TIC
                    feature = data[i+2]
                    # pre-compute the intensity 
                    intensity = round(np.mean(feature[1:]))
                    if intensity < 10e2:
                        continue
                    # check for TIC correlation 
                    if not tic_correlate(data[1][1:], feature[1:]):
                        continue
                    # pre-compute the m/z which is on index 0 of the feature's time trace
                    mz = "+" + f'{feature[0]}' if "pos" in file else "-" + f'{feature[0]}'
                    try:
                        if intensity > features[mz]: 
                            # and if the mean feature intensity is greater than the curent value for this feature
                            # (avoids overlapping features with the same m/z)
                            features[mz] += intensity
                        else:
                            continue
                    except(KeyError):   # if the feature hasn't been added to the dict yet
                        features[mz] = intensity
        except EmptyDataError:
            continue  # Skip empty files
        if "pos" in file:
            sample_name = os.path.basename(file).split("_pos")[0]  # Get the last folder as the sample name
        else:
            sample_name = os.path.basename(file).split("_neg")[0]
        if sample_name not in samples:
            samples[sample_name] = features
        else:
            samples[sample_name].update(features)

    samples = {k: v for k, v in sorted(samples.items())} 
    intensity_matrix = pd.DataFrame.from_dict(data=samples, orient='index')

    # Sort the DataFrame by index (m/z values)
    intensity_matrix.sort_index(inplace=True)
    # Save only those features that appear in more than X% of all samples, default 0
    threshold = round(0.0 * len(intensity_matrix))    
    intensity_matrix.dropna(thresh=threshold, axis=1, inplace=True)
    intensity_matrix.fillna(value=1, inplace=True)
    intensity_matrix=intensity_matrix.T
    # Write the DataFrame to a .csv file
    intensity_matrix.to_csv(os.path.join(path, "intensity_matrix.csv"))

print("Done.")

# Print execution time 
et = time.time()
elapsed_time = et - st
print("Intensity matrix constructed in: ", round(elapsed_time, 2), " seconds.")


