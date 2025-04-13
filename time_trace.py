from pyteomics import mzml
import os, csv, time
import numpy as np
from scipy.integrate import trapezoid
from peak_pick import peak_pick
from pathlib import Path
import settings
from PyQt6.QtCore import QThread, pyqtSignal

# Log script execution time
st = time.time()

class TimeTraceThread(QThread):
    progress_signal = pyqtSignal(str, int)

    def __init__(self, path: str, MZ_AXIS: np.ndarray):
        super(TimeTraceThread, self).__init__()
        self.path = Path(path)
        self.MZ_AXIS = MZ_AXIS

    def run(self):
        path = self.path
        # Pick peaks on the composite spectra
        self.progress_signal.emit("\nPerforming peak picking...", 0)
        composite_pos = np.genfromtxt(path.parent.absolute() / "composite_spectrum_pos.csv", delimiter=',')
        composite_neg = np.genfromtxt(path.parent.absolute() / "composite_spectrum_neg.csv", delimiter=',')

        peaklist_pos = peak_pick(composite_pos, self.MZ_AXIS)
        peaklist_neg = peak_pick(composite_neg, self.MZ_AXIS)

        filelist = [file for file in os.listdir(path.parent.absolute()) if file.lower().endswith(".mzml")]

        # Process the time traces for every peak found
        counter = 0
        for file in filelist:
            counter += 1
            self.progress_signal.emit(f"\nFinding time traces for: {file}, {counter} out of {len(filelist)}...", int((counter/len(filelist))*100))
            if "pos" in str(file):
                data = self.trace(str(path.parent.absolute() / file), peaklist_pos, self.MZ_AXIS)
                with open(path / "{}.csv".format(file.lower()).replace('.mzml', "_trace"), "w+", newline='') as trace_csv:
                    writer = csv.writer(trace_csv)
                    for item in data:
                        writer.writerow(item)
            elif "neg" in str(file):
                data = self.trace(str(path.parent.absolute() / file), peaklist_neg, self.MZ_AXIS)
                with open(path / "{}.csv".format(file.lower()).replace('.mzml', "_trace"), "w+", newline='') as trace_csv:
                    writer = csv.writer(trace_csv)
                    for item in data:
                        writer.writerow(item)


        # Print execution time 
        et = time.time()
        elapsed_time = et - st

        self.progress_signal.emit(f"\nFinished writing time traces in {elapsed_time:.2f}.", 100)

    def trace(self, path: str, features: list, MZ_AXIS: np.ndarray) -> np.ndarray:
        tic = []                            # Placeholder data structures 
        scans = mzml.MzML(path)
        data = np.empty((len(features)+1, len(scans)))

        j = 0
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
        trc = np.ndarray.tolist(data)

        trc.insert(1, tic)

        return trc