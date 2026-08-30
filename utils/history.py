import numpy as np
import pickle
import os.path
import copy
import random
import pandas as pd


from itertools import combinations

def get_all_subsets(input_list):
    subsets = []
    for r in range(len(input_list) + 1):
        # combinations() returns tuples, so we convert them to lists
        for combo in combinations(input_list, r):
            subsets.append(list(combo))
    return subsets

class History:
    def __init__(self,
                    capacity:int=10000,
                    unused:list=[], #list[str] name of elements that are unsued in imgep exploration
                    ):
        self.memory_parameter = []
        self.capacity = capacity
        self.memory_observation ={} 
        self.memory_observation_temp ={} 
        self.memory_observation_idx_temp ={} 
        self._j = 0
        self.rand_id = random.uniform(0,1)
        self.unused = unused
        self.components = ['bus_interference',
                             'ddr_interference',
                             'ddr_scheduler_interference',
                             'L2_cache_interference']
        self.memory_components = []
        self.memory_micro_components = []
        self.memory_combinations = {}
        power_set = get_all_subsets(list(range(len(self.components))))
        self.combinations = get_all_subsets(self.components)
        for sub in power_set:
            chain = ''
            for j in range(4):
                if j in sub:
                    chain+='1'
                else:
                    chain+='0'
            self.memory_combinations[chain] = []

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
        out = self.memory_observation[if_type].values
        return out
    def __len__(self):
        return len(self.memory_parameter)
    def store(self,parameter:dict,obs:dict):
        if self._j>=self.capacity:
            raise Exception("Exceeded capacity")
        #saves codes
        self.memory_parameter.append(parameter)
        #saves interference events and their type
        combination_vector = []

        for if_type in obs[0]:
            if len(list(obs[0][if_type].values())[0])>0:
                tab = np.array(list(obs[0][if_type].values()))
                tab = np.reshape(tab,(len(tab),-1))[:,0]
                if if_type in self.memory_observation:
                    self.memory_observation_temp[if_type].append(tab)
                    self.memory_observation_idx_temp[if_type].append(self._j)
                else:                             
                    #if if_type has never been stored yet, one creates a key and a dataframe in self.memory_observation
                    self.memory_observation[if_type] = pd.DataFrame(index = obs[0][if_type].keys())
                    self.memory_observation[if_type][self._j] = tab
                    self.memory_observation_temp[if_type] = []
                    self.memory_observation_idx_temp[if_type] = []

        # saves the combination of components that are involved
        encod = np.zeros((4,))
        binary_rep = ''
        for j,component in enumerate(self.components):
            if len(obs[0][component][list(obs[0][component].keys())[0]])>0:
                encod[j] = 1
                binary_rep +='1'
            else:
                binary_rep +='0'
        self.memory_combinations[binary_rep].append(combination_vector)
        self.memory_components.append(encod)
        # saves the microcomponents that are involved with one hot encoding
        self.memory_micro_components.append(obs[1])
        
        if (self._j-1)%10==0 and self._j>0:
            self.update_memory()
        self._j+=1
    def update_memory(self):
        for if_type in self.components:
            if if_type in self.memory_observation:
                load_df  = pd.DataFrame({col:self.memory_observation_temp[if_type][j] for j,col in enumerate(self.memory_observation_idx_temp[if_type])},index=self.memory_observation[if_type].index)
                self.memory_observation[if_type] = pd.concat([self.memory_observation[if_type],load_df],axis=1)
                self.memory_observation_temp[if_type] = []
                self.memory_observation_idx_temp[if_type] = []

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
