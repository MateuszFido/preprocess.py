import os, time
import numpy as np
import pandas as pd
from pathlib import Path
from pandas.errors import EmptyDataError
from tic_correlation import tic_correlate
from PyQt6.QtCore import QThread, pyqtSignal

# Log script execution time
st = time.time()

class IntensityMatrixThread(QThread):
    progress_signal = pyqtSignal(str, int)

    def __init__(self, path: str):
        super(IntensityMatrixThread, self).__init__()
        self.path = Path(path)

    def run(self):
        self.progress_signal.emit("\nConstructing intensity matrix...", 0)
        samples = {}

        filelist_csv = [timetrace for timetrace in os.listdir(self.path / "time_traces") if timetrace.endswith("_trace.csv") and not timetrace.startswith("~")]
        counter = 0
        for file in filelist_csv:
            features = {}
            try:
                if "pos" in file or "neg" in file:
                    # read contents
                    data = np.genfromtxt(self.path / "time_traces" / file, delimiter=",") 
                    # iterate through all the features
                    for i in range(0, len(data)-2):    # skip 2 first lines: 1st is scan ID, 2nd is TIC
                        feature = data[i+2]
                        # pre-compute the intensity 
                        intensity = round(np.trapezoid(feature[1:]))
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

            counter += 1
            self.progress_signal.emit(f"\nProcessed {counter} out of {len(filelist_csv)}...", int((counter/len(filelist_csv))*100))

        samples = {k: v for k, v in sorted(samples.items())} 
        intensity_matrix = pd.DataFrame.from_dict(data=samples, orient='index')

        elapsed_time = time.time() - st
        self.progress_signal.emit(f"\nFinished constructing intensity matrix in {elapsed_time:.2f}.", 100)

        # Sort the DataFrame by index (m/z values)
        intensity_matrix.sort_index(inplace=True)
        # Save only those features that appear in more than X% of all samples, default 0
        threshold = round(0.0 * len(intensity_matrix))    
        intensity_matrix.dropna(thresh=threshold, axis=1, inplace=True)
        intensity_matrix.fillna(value=1, inplace=True)
        intensity_matrix=intensity_matrix.T
        # Write the DataFrame to a .csv file
        intensity_matrix.to_csv(os.path.join(self.path, "intensity_matrix.csv"))
        


