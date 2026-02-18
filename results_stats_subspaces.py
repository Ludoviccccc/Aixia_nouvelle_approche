import sys
sys.path.append('../../')
import pickle
import os
import numpy as np
from scipy.special import stdtr, stdtrit
from multiprocessing import Pool
from exploration.load_file import open_content_list
import pandas as pd
# This codes evaluates the diversity evolution of multiple IMGEP/RANDOM exploration runs
# in parallel (using Pool) and determines asymptotic confidence intervals for each point of the curves

def bin_diversity(content):
    div = 5*np.ones(content.shape[1])
    coords = (content)//div
    c = np.unique(coords,axis=0)
    return c
class evaluate_hist_diversity:
    def __init__(self,idx_time,idx_remain):
        self.idx_time = idx_time
        self.idx_remain = idx_remain
    def __call__(self,content_list):
        step = 1000
        n_func = 5
        diversity_time = [0]+ [len(bin_diversity(content_list[:j,self.idx_time])) for j in range(0,len(content_list),step) if j!=0]+ [len(bin_diversity(content_list[:,self.idx_time]))]
        diversity_remain = [0]+ [len(bin_diversity(content_list[:j,self.idx_remain])) for j in range(0,len(content_list),step) if j!=0]+ [len(bin_diversity(content_list[:,self.idx_remain]))]
        return [diversity_time,diversity_remain]
def Sn(diversity_array:np.ndarray):
    """
    computes the sigma estimator of the diversity values
    """
    mean_ = diversity_array.mean(axis=0)
    out = np.sqrt(np.sum((diversity_array - mean_)**2,axis=0)/(diversity_array.shape[0]-1))
    return out
def CI(diversity_array,alpha=.05):
    n = diversity_array.shape[0]
    qt = stdtrit(n-1,1-alpha)
    sig = Sn(diversity_array)
    mean_ = diversity_array.mean(axis=0)
    inf = mean_ - qt*sig*(1.0/np.sqrt(n))
    sup = mean_ + qt*sig*(1.0/np.sqrt(n))
    x_axis = 1000*np.arange(len(mean_))
    return {'mean':mean_,'inf':inf,'sup':sup,'iterations':x_axis}
if __name__=='__main__':
    N = 10000
    k_values = [1,2,3]
    folder = 'results_20' 
    algo_list = ['imgep','operators','rand']
    CI_algo_time = pd.DataFrame([])
    CI_algo_remain = pd.DataFrame([])
    N = 10000
    M = 500
    time_var = ['mutual_diff_time_core0',
                 'mutual_diff_time_core1',
                 'mutual_diff_time']
    j_list = range(M)
    idx_defined = False
    print('start opening files')
    idx_time = range(0,3)
    idx_remain = range(3,59)
    for algo in algo_list:
        for k in k_values:
            if algo=='rand' and k>1:
                break
            content_list = []
            n_p = 5
            n_func = 20
            for l in range(1+M//(n_func*n_p)):
                if l ==M//(n_func*n_p):
                    with Pool(70) as p: 
                        func_open = open_content_list(folder,k,N,algo)
                        content_list_temp = [func_open(range(l,l+M%(n_p*n_func)))]
                else:
                    with Pool(70) as p: 
                        content_list_temp = p.map(open_content_list(folder,k,N,algo),[range(n_func*n_p*l+m*n_p,n_func*n_p*l+(m+1)*n_p) for m in range(n_func)])
                for element in content_list_temp:
                    content_list +=element
            if len(content_list)==0:
                raise ValueError('empty content list')
            diversity_list = []
            n_func = 15
            for j in range(1+len(content_list)//n_func):
                if j==len(content_list)//n_func:
                    with Pool(70) as p: 
                        batch_div = p.map(evaluate_hist_diversity(idx_time,idx_remain),content_list[j*n_func:])
                else:
                    with Pool(70) as p: 
                        batch_div = p.map(evaluate_hist_diversity(idx_time,idx_remain),content_list[j*n_func:(j+1)*n_func])
                diversity_list+=batch_div
            diversity_list = np.array(diversity_list)
            diversity_array_time = diversity_list[:,0,:]
            diversity_array_remain = diversity_list[:,1,:]
            print('diversity_array_time', diversity_array_time.shape,algo,f'k={k}')
            print('diversity_array_remain', diversity_array_remain.shape,algo,f'k={k}')
            div_time = CI(diversity_array_time)  
            div_remain = CI(diversity_array_remain)
            for key in div_time:
                CI_algo_time[f'{algo}_{k}_{key}'] = div_time[key]
                CI_algo_remain[f'{algo}_{k}_{key}'] = div_remain[key]
    CI_algo_time.to_csv('ci_diversity_time.csv')
    print('ci_diversity_time.csv written!')
    CI_algo_remain.to_csv('ci_diversity_remain.csv')
    print('ci_diversity_remain.csv written!')
