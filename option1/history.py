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
        self.names = []
        self.length_ = length_
        self.tabular = []
    def __getitem__(self,id_):
        return self.memory_program['core0'][id_]
    def as_tab(self):
        return np.array(self.tabular)
    def __len__(self):
        return len(self.memory_program["core0"])
    def store(self,sample:dict,obs:dict):
        self.memory_program["core0"].append(sample)
        tab = []
        for key in obs:
            a = list(obs[key].values())
            tab += a
            if key in self.event:
                self.event[key].append(a)
            else:
                self.event[key] = [a]
        self.tabular.append(tab)
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
