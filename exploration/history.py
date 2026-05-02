import numpy as np
import pickle
import os.path
import copy
class History:
    def __init__(self,
                    length_ = 10,
                    capacity:int=10000,
                    ):
        self.memory_program = {"core0":[]}
        self.capacity = capacity
        self.event ={} 
        self.j = 0
        self.tab = []
        self.names = []
        self.length_ = length_
    def as_tab(self):
        return np.array(self.tab)
    def __len__(self):
        return len(self.memory_program["core0"])
    def store(self,sample:dict,obs:dict):
        #l = sample["event"].values.shape[0]
        self.memory_program["core0"].append(sample["program"]["core0"])
        for key in obs:
            if key in self.event:
                self.event[key].append(list(obs.values()))
            else:
                self.event[key] = [list(obs.values())]
        self.j+=1
    def content(self):
        return {
                "memory_program":self.memory_program,
                }
    def save_pickle(self, name:str=None):
        k = 0
        while os.path.isfile(f"{name}_{k}.pkl"):
            k+=1
        output = self.content()
        with open(f"{name}_{k}.pkl", "wb") as f:
            pickle.dump(output, f)
