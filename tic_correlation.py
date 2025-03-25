import numpy as np
import matplotlib.pyplot as plt

def tic_correlate(tic: np.ndarray, xic: np.ndarray) -> bool:
    '''
    Tests for Pearson's correlation between two signals. If positive, returns True.
    
    Parameters
    ----------
    tic: np.ndarray
        The total ion current for the given mzML file.
    xic: np.ndarray
        The extracted ion current for the given m/z feature.
        
    Returns
    -------
    True if Pearson's correlation coefficient is above 0.5. Otherwise returns False. 
    '''
    
    r = np.corrcoef(xic, tic)[1,0]
    
    if r > 0.5:
        return True
    else:
        return False
   
