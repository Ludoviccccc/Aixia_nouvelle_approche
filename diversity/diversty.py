import numpy as np

class Diversity:
    def __init__(self,min_tab,max_tab,num_bins):
        self.min_tab = min_tab
        self.max_tab = max_tab
        self.num_bins = num_bins
    def _bins(self,content:np.ndarray):
        coords = (content-self.min_tab)/(self.max_tab - self.min_tab)
        coords //= (1.0/self.num_bins)
        c = np.unique(coords,axis=0)
        return c
    def __call__(self,content:np.ndarray):
        output = len(self._bins(content)) 
        return output
