import numpy as np

class Diversity:
    def __init__(self,min_tab,max_tab,bin_size):
        self.min_tab = min_tab
        self.max_tab = max_tab
        self.bin_size = bin_size
    def _bins(self,content:np.ndarray):
        coords = (content-self.min_tab)/(self.max_tab - self.min_tab)
        coords //= self.bin_size
        c = np.unique(coords,axis=0)
        return c
    def __call__(self,content:np.ndarray):
        output = len(self._bins(content)) 
        return output
