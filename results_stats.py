import sys
sys.path.append('../../')
import pickle
import os
import numpy as np
from scipy.special import stdtr, stdtrit
from multiprocessing import Pool
import time
from exploration.load_file import open_content_list
import pandas as pd
# This codes loads results of multiple IMGEP/RANDOM exploration runs in parallel (using Pool)
# and evaluates the diversity evolution in parallel and determines asymptotic confidence intervals for each point of the curves

def bin_diversity(content):
    div = 5*np.ones(content.shape[1])
    coords = (content)//div
    c = np.unique(coords,axis=0)
    return c

def evaluate_hist_diversity(content_list):
    step = 1000
    n_func = 5
    diversity = [0]+ [len(bin_diversity(content_list[:j])) for j in range(0,len(content_list),step) if j!=0]+ [len(bin_diversity(content_list))]
    return diversity
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
    CI_algo = pd.DataFrame([])
    N = 10000
    M = 500
    output_name = 'ci_diversity.csv'
    j_list = range(M)
    print('start opening files')
    start_time = time.time()
    for algo in algo_list:
        for k in k_values:
            print(algo, f'k ={k}')
            if k>1 and algo=='rand':
                break
            n_p = 5
            n_func = 20
            content_list = []
            for l in range(1+M//(n_func*n_p)):
                if l ==M//(n_func*n_p):
                    with Pool(70) as p: 
                        content_list_temp = [open_content_list(folder,k,N,algo)(range(l,l+M%(n_p*n_func)))]
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
                        batch_div = p.map(evaluate_hist_diversity,content_list[j*n_func:])
                else:
                    with Pool(70) as p: 
                        batch_div = p.map(evaluate_hist_diversity,content_list[j*n_func:(j+1)*n_func])
                diversity_list+=batch_div
            diversity_list = np.array(diversity_list)
            print('diversity_list', diversity_list.shape,algo,f'k={k}')
            div = CI(diversity_list)
            for key in div:
                CI_algo[f'{algo}_{k}_{key}'] = div[key]
    CI_algo.to_csv(output_name)
    print(f'{output_name} written!')
    print('Total time:',(time.time() - start_time)//3600,'H',((time.time()-start_time)%3600)//60,'    m',f"{(time.time()-start_time)%3600%60:.2f}",'s')
