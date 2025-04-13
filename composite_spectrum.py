import numpy as np
from pathlib import Path
from peak_pick import peak_pick
import settings
import os, sys, time
from PyQt6.QtCore import QThread, pyqtSignal

class CompositeSpectrumThread(QThread):
    progress_signal = pyqtSignal(str, int)
    
    def __init__(self, path: str, MZ_AXIS: np.ndarray):
        super(CompositeSpectrumThread, self).__init__()
        self.path = Path(path)
        self.MZ_AXIS = MZ_AXIS
    
    def run(self):        
        # Start time
        st = time.time()
        # Average the averaged spectra to create a composite spectrum of all mzML files on the file path
        self.progress_signal.emit(f"\nPreparing the composite spectra...", 0)

        with open(self.path / "composite_spectrum_pos.csv", "w+") as spectrum_pos, open(self.path / "composite_spectrum_neg.csv", "w+") as spectrum_neg:
            
            # Prepare arrays for intensity values
            avg_int_pos = np.zeros(len(self.MZ_AXIS))
            num_pos = 0
            avg_int_neg = np.zeros(len(self.MZ_AXIS))
            num_neg = 0
            
            # Process all directories
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    if 'avg_' in file:
                        file_path = Path(root) / file
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
            composite_pos = np.array((self.MZ_AXIS, avg_int_pos))
            composite_neg = np.array((self.MZ_AXIS, avg_int_neg))
            composite_pos = np.transpose(composite_pos)
            composite_neg = np.transpose(composite_neg)
            
            np.savetxt(spectrum_pos, composite_pos, delimiter=",", encoding='utf-8')
            np.savetxt(spectrum_neg, composite_neg, delimiter=",", encoding='utf-8')
            
            # Print execution time 
            et = time.time()
            elapsed_time = et - st
            
            self.progress_signal.emit(f"\nFinished creating composite spectra in {elapsed_time:.2f} seconds.", 100)

