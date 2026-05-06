import numpy as np
import pickle
import os.path
import copy
import random
class History:
    def __init__(self,
                    length_ = 10,
                    capacity:int=10000,
                    ):
        self.memory_program = {"core0":[]}
        self.capacity = capacity
        self.event ={} 
        self._j = 0
        self.names = []
        self.length_ = length_
        self.numpy_view = 0
        self.rand_id = random.uniform(0,1)

    def __eq__(self,other):
        return self.__dict__== other.__dict__
    def __getitem__(self,id_):
        return self.memory_program['core0'][id_]
    def as_tab(self):
        if self._j==0:
            raise TypeError("no element stored yet")
        return self.numpy_view[:self._j]
    def __len__(self):
        return len(self.memory_program["core0"])
    def store(self,sample:dict,obs:dict):
        if self._j>=self.capacity:
            raise Exception("Exceeded capacity")
        self.memory_program["core0"].append(sample)
        tab = []
        for key in obs:
            object_ = list(obs[key].values())
            tab += object_
            if key in self.event:
                self.event[key].append(object_)
            else:
                self.event[key] = [object_]
        if self._j ==0:
            self.length_ = len(tab)
            self.numpy_view = np.zeros((self.capacity,self.length_))
        self.numpy_view[self._j] = tab
        self._j+=1
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
