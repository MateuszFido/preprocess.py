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

import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from view import Ui_MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
 