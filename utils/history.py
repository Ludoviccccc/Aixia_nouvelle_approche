import numpy as np
import pickle
import os.path
import copy
import random
class History:
    def __init__(self,
                    capacity:int=10000,
                    unused:list=[], #list[str] name of elements that are unsued in imgep exploration
                    ):
        self.memory_parameter = []
        self.capacity = capacity
        self.memory_observation ={} 
        self._j = 0
        self.rand_id = random.uniform(0,1)
        self.unused = unused
        self.components = ['bus_interference',
                             'ddr_interference',
                             'ddr_scheduler_interference',
                             'L2_cache_interference']
        self.memory_components = []


    def __eq__(self,other):
        return self.__dict__== other.__dict__
    def __getitem__(self,id_):
        return self.memory_parameter[id_]
    def as_tab(self,if_type):
        '''
        extracts values as an np.array for the considered type of if.
        the last columns corresponds to the id of the program
        Entry:
        type_if:'str'. type of interference i.e key of History.memory_observation
        '''
        if self._j==0:
            raise TypeError("no element stored yet")
        return np.array(list(self.memory_observation[if_type].values()))
    def __len__(self):
        return len(self.memory_parameter)
    def store(self,parameter:dict,obs:dict):
        if self._j>=self.capacity:
            raise Exception("Exceeded capacity")
        self.memory_parameter.append(parameter)
        for if_type in obs:
            if if_type in self.memory_observation:
                for key in self.memory_observation[if_type]:
                    if key!='idx':
                        self.memory_observation[if_type][key] += obs[if_type][key]
                self.memory_observation[if_type]['idx'] += [self._j]*len(obs[if_type][list(obs[if_type].keys())[0]])
            else:                             
                self.memory_observation[if_type] = obs[if_type]
                self.memory_observation[if_type]['idx'] = [self._j]*len(obs[if_type][list(obs[if_type].keys())[0]])
        encod = np.zeros((4,))
        for j,component in enumerate(self.components):
            encod[j] = 1
        self.memory_components.append(encod)
        self._j+=1
    def content(self):
        return {
                "memory_parameter":self.memory_parameter,
                "memory_observation":self.memory_observation,
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
