# preprocess.py
Open-source set of Python scripts for preprocessing untargeted metabolomics data in the mzML file format.

Last modified: 2025-Mar-25\
@author: Mateusz Fido (github.com/MateuszFido)\
mateusz.fido@org.chem.ethz.ch\
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

# Installation
1. Install a Python interpreter (3.11. or above)
2. Install the required dependencies (e.g., `$ pip install -r requirements.txt`):
   - pandas
   - numpy
   - scipy
   - tqdm
   - pyteomics

Latest version of these packages are recommended.

# Usage
Run the pipeline by executing the main script on a path containing .mzml files to be processed:

   `$ python3 preprocess.py path/to/mzml-files`

# References:
Matlab Code of Jiayi Lan and Miguel de Figueiredo\
Python Code of Cedric Wüthrich\
https://pyteomics.readthedocs.io/en/latest/index.html

