from pathlib import Path
import numpy as np
import os, time, shutil
from pyteomics import mzml
from PyQt6.QtCore import pyqtSignal, QThread

class AverageThread(QThread):
    progress_signal = pyqtSignal(str, int)

    def __init__(self, path: str, mz_axis: np.ndarray):
        super(AverageThread, self).__init__()
        self.path = Path(path)
        self.mz_axis = mz_axis

    def run(self):
        st = time.time()
        filelist = [file for file in os.listdir(self.path.parent.absolute()) if file.lower().endswith(".mzml")]
        counter = 0
        self.progress_signal.emit(f"\nStarting the averaging...", 0)
        for file in filelist:
            counter += 1
            mzml_path = mzml.MzML(str(self.path.parent.absolute() / file))  # Instantiate the MzML reader object
            intensities = np.zeros(len(self.mz_axis))
            for j in range(0, len(mzml_path)):
                if mzml_path[j]['ms level'] == 1:
                    mz_array = np.ndarray.transpose(mzml_path[j]['m/z array'])                  # Get m/z values from the MzML path
                    intensity_array = np.ndarray.transpose(mzml_path[j]['intensity array'])     # Get their intensities 
                    int_interp = np.interp(self.mz_axis, mz_array, intensity_array, left=0, right=0) # Interpolate continuous intensity signal from discrete m/z 
                    intensities += int_interp                                                   # and intensities over the new, linear m/z axis
                else:
                    continue
            
            self.progress_signal.emit(f"\nAveraging spectra for: {file}, {counter} out of {len(filelist)}...", int((counter/len(filelist))*100))

            avg_intensity = intensities / len(mzml_path)   # Average the signal
            data_matrix = np.array((self.mz_axis, avg_intensity), dtype=np.float64)
            data_matrix = np.transpose(data_matrix)                      
        
            # Save background-corrected, resampled m/z-intensities
            with open(self.path / "avg_{}.csv".format(file).replace('.mzml', ""), "w+") as average_csv:
                np.savetxt(average_csv, data_matrix, delimiter=",", encoding='utf-8')

        self.progress_signal.emit(f"\nAveraging complete in {round(time.time() - st, 2)} seconds.", 100)