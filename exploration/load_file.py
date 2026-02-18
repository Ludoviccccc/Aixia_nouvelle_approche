import pickle
import numpy as np
import os

def load(name,k=None):
    if k==None:
        k = 1
        while os.path.isfile(f"{name}_{k}.pkl"):
            k+=1
        k-=1
    with open(f'{name}_{k}.pkl','rb') as f:
        contentbis = pickle.load(f)
    print(f'{name}_{k}.pkl')

    return contentbis
class open_content_list:
    def __init__(self,folder,k,N,algo):
        self.k = k
        self.N = N
        self.algo = algo
        self.folder = folder
        self.time_var = ['mutual_diff_time_core0','mutual_diff_time_core1','mutual_diff_time']
    def __call__(self,j_list:list)->list:
        content_list = []
        for j in j_list:
            if self.algo in ['imgep','operators']:
                name = f'{self.algo}_run_{self.k}_{self.N}_{j}.pkl'
            else:
                if self.k>1:
                    break
                name = f'{self.algo}_run_{self.N}_{j}.pkl'
            if j%100==0:
                print(f'opening {name}')
            try:
                with open(os.path.join(self.folder,name),'rb') as f:
                    stats = pickle.load(f)
                    content_list.append(stats['tabular_view'])
                    self.idx_time = np.array([j for j in range(len(stats['names'])) if stats['names'][j] in self.time_var])
                    self.idx_remain = np.array([j for j in range(len(stats['names'])) if not (stats['names'][j] in self.time_var)])

            except:
                print(f'failed at opening {name}')
        return content_list

class open_content_all_list:
    def __init__(self,folder,k,N,algo):
        self.k = k
        self.N = N
        self.algo = algo
        self.folder = folder
    def __call__(self,j_list:list)->list:
        content_list = []
        for j in j_list:
            if self.algo in ['imgep','operators']:
                name = f'{self.algo}_run_{self.k}_{self.N}_{j}.pkl'
            else:
                if self.k>1:
                    break
                name = f'{self.algo}_run_{self.N}_{j}.pkl'
            if j%100==0:
                print(f'opening {name}')
            try:
                with open(os.path.join(self.folder,name),'rb') as f:
                    stats = pickle.load(f)['memory_perf']
                    dict_ = {key:{'miss_ratios_detailled':stats[key]['miss_ratios_detailled']} for key in ['mutual','core0','core1']}
                    content_list.append(dict_)
            except:
                print(f'failed at opening {name}')
        return content_list
