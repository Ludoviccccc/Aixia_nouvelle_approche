import numpy as np
import pickle
import os.path
import copy
import random
class History:
    def __init__(self,
                    capacity:int=10000,
                    ):
        self.memory_parameter = []
        self.capacity = capacity
        self.memory_observation ={} 
        self._j = 0
        self.names = []
        self.numpy_view = 0
        self.rand_id = random.uniform(0,1)

    def __eq__(self,other):
        return self.__dict__== other.__dict__
    def __getitem__(self,id_):
        return self.memory_parameter[id_]
    def as_tab(self):
        if self._j==0:
            raise TypeError("no element stored yet")
        return self.numpy_view[:self._j]
    def __len__(self):
        return len(self.memory_parameter)
    def store(self,sample:dict,obs:dict):
        if self._j>=self.capacity:
            raise Exception("Exceeded capacity")
        self.memory_parameter.append(sample)
        tab = []
        for key in obs:
            object_ = list(obs[key].values())
            tab += object_
            if key in self.memory_observation:
                self.memory_observation[key].append(object_)
            else:
                self.memory_observation[key] = [object_]
        if self._j ==0:
            self.numpy_view = np.zeros((self.capacity,len(tab)))
        self.numpy_view[self._j] = tab
        self._j+=1
    def content(self):
        return {
                "memory_parameter":self.memory_parameter,
                "memory_observation":self.memory_observation,
                "numpy_view":self.numpy_view,
                }
    def save_pickle(self, name:str=None):
        k = 0
        while os.path.isfile(f"{name}_{k}.pkl"):
            k+=1
        output = self.content()
        with open(f"{name}_{k}.pkl", "wb") as f:
            pickle.dump(output, f)

    def take(self,content,count):
        self.memory_parameter = content["memory_parameter"][:count]
        self.numpy_view = content["numpy_view"][:]
        for key in content["memory_observation"]:
            self.memory_observation[key] = content["memory_observation"][key][:count]
        self._j = count
