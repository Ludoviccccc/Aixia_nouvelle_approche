import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def bin_diversity(content):
    div = 5*np.ones(content.shape[1])
    coords = (content)//div
    c = np.unique(coords,axis=0)
    return c
def plot_total_diversity(content_rand,content_list,name='diversity_comparaison'):    
    max_ = np.max(content_rand['tabular_view'],axis=0)
    N = len(content_rand['tabular_view'])
    diff = lambda tab,j: np.sum(np.abs(tab[j+1:,:]-tab[j,:])**2,axis=1)
    distances = [[] for j in range(N)]
    diversities_rand = np.zeros((N//1000)+1)
    for j in range(N):
        distances[j] = diff(content_rand['tabular_view'],j)
    for j,n in enumerate(range(0,N+1,1000)):
        diversities_rand[j] = np.sum([np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])])
    
    diversities = np.zeros((len(content_list),1+N//1000))
    start = 0
    for f,vec in enumerate(content_list):
        content_imgep,label = vec[0],vec[1]
        distances = [[] for j in range(len(content_imgep['tabular_view']))]
        for j in range(len(content_imgep['tabular_view'])):
            distances[j] = diff(content_imgep['tabular_view'],j)
        for j,n in enumerate(range(0,N+1,1000)):
            diversities[f,j] = np.sum([np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])])

        plt.plot(np.arange(0,N+1,1000)[start:],diversities[f][start:],'-o',label=label)#+f'value = {round(diversities[f][-1]/1e11,1)}1e11')
    plt.plot(np.arange(0,N+1,1000)[start:],diversities_rand[start:],'-o',label=f'random')# value = {round(diversities_rand[-1]/1e11,1)}1e11',alpha=.3)
    plt.grid()
    plt.title('Entire space Diversity IMGEP vs RANDOM', fontsize=19)
    plt.ylabel('sum of squares of distances between all pairs', fontsize=12)
    plt.xlabel('iterations', fontsize=19)
    plt.xticks(range(0,10001,1000)[start:])
    plt.legend(prop={'size': 19})
    plt.savefig(name)
    plt.show()

def diversity_for_comparaison_bin_method_time(args:list[np.ndarray],name=None):
    labels = []
    contents = []
    diversities = []
    plt.figure()
    step = 500
    time_var = ['mutual_diff_time_core0',
                'mutual_diff_time_core1',
                'mutual_diff_time']
    data_out = pd.DataFrame([])
    f, (ax1, ax2) = plt.subplots(1, 2, sharex=True,figsize=(12,5))
    for f,value in enumerate(args):
        content = value[0]
        idx_time = np.array([j for j in range(len(content['names'])) if content['names'][j] in time_var])
        idx_remain = np.array([j for j in range(len(content['names'])) if not (content['names'][j] in time_var)])
        label = value[1]
        labels.append(label)
        diversity_time = [0]+[len(bin_diversity(content['tabular_view'][:j,idx_time])) for j in range(0,len(content['tabular_view']),step) if j!=0]+ [len(bin_diversity(content['tabular_view'][:,idx_time]))]
        diversity_remain = [0]+[len(bin_diversity(content['tabular_view'][:j,idx_remain])) for j in range(0,len(content['tabular_view']),step) if j!=0]+ [len(bin_diversity(content['tabular_view'][:,idx_remain]))]
        ax1.plot(range(0,len(content['tabular_view'])+1,step),diversity_time,'-o',label=label)
        ax2.plot(range(0,len(content['tabular_view'])+1,step),diversity_remain,'-o',label=label)
        data_out[f'time_{f}'] = diversity_time
        data_out[f'miss_{f}'] = diversity_remain
    data_out['x'] = np.arange(0,len(content['tabular_view'])+1,step)
    data_out.to_csv('progression_seperate.csv',header= True)
    ax1.grid()
    ax1.set_ylabel('diversity:bins filled ',fontsize=19)
    ax1.set_xlabel('iterations',fontsize=19)
    ax1.legend( prop={'size': 19})
    ax2.grid()
    ax2.set_ylabel('diversity:bins filled ',fontsize=19)
    ax2.set_xlabel('iterations',fontsize=19)
    ax2.legend( prop={'size': 19})
    ax1.set_title('Time space diversity',fontsize=19)
    ax2.set_title('Miss and hit space diversity',fontsize=19)
    if name:
        k = 0
        while os.path.isfile(f'{name}_{k}.png'):
            k+=1
        plt.savefig(f'{name}_{k}.pdf')
    plt.show()
    return labels,diversities
def plot_diversity_hist_and_sum(content_rand,content_list,name='diversity_comparaison'):
    max_ = np.max(content_rand['tabular_view'],axis=0)
    N = len(content_rand['tabular_view'])
    diff = lambda tab,j: np.sum(np.abs(tab[j+1:,:]-tab[j,:])**2,axis=1)
    distances = [[] for j in range(N)]
    diversities_sum_rand = np.zeros((N//1000)+1)
    for j in range(N):
        distances[j] = diff(content_rand['tabular_view'],j)
    for j,n in enumerate(range(0,N+1,1000)):
        diversities_sum_rand[j] = np.sum([np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])])
    
    diversities_sum = np.zeros((len(content_list),1+N//1000))

    data_sum = pd.DataFrame([])
    data_hist = pd.DataFrame([])
    f, (ax1, ax2) = plt.subplots(1, 2, sharex=True,figsize=(12,5))
    start = 0
    step = 500
    for f,vec in enumerate(content_list):
        content_imgep,label = vec[0],vec[1]
        distances = [[] for j in range(len(content_imgep['tabular_view']))]
        for j in range(len(content_imgep['tabular_view'])):
            #distance between point j and all points j+k gathered after it, k>0
            distances[j] = diff(content_imgep['tabular_view'],j)
        for j,n in enumerate(range(0,N+1,1000)):
            #novelty associated with each point i collected before n
            #novelty here is the sum of all distances between a point and his neighbors previously sampled
            nov_ = [np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])]
            # sum of all the novelties for points i collected before n to obtain the diversity at time n
            diversities_sum[f,j] = np.sum(nov_)
        #store diversitysum values in data_out
        data_sum[f'sum_{f}'] = diversities_sum[f]
        #plot sum diversity for imgep
        ax1.plot(np.arange(0,N+1,1000)[start:],diversities_sum[f][start:],'-o',label=label)#+f'value = {round(diversities_sum[f][-1]/1e11,1)}1e11')
        #hist diversity for imgep
        diversity = [0]+ [len(bin_diversity(content_imgep['tabular_view'][:j])) for j in range(0,len(content_imgep['tabular_view']),step) if j!=0]+ [len(bin_diversity(content_imgep['tabular_view']))]
        #store diversity hist values in data_out 
        data_hist[f'hist_{f}'] = diversity
        #plot hist diversity for imgep
        ax2.plot(range(0,len(content_imgep['tabular_view'])+1,step),diversity,'-o',label=label)
    # plot sum diversity for random
    ax1.plot(np.arange(0,N+1,1000)[start:],diversities_sum_rand[start:],'-o',label=f'random')# value = {round(diversities_sum_rand[-1]/1e11,1)}1e11',alpha=.3)
    diversity = [0]+[len(bin_diversity(content_rand['tabular_view'][:j])) for j in range(0,len(content_rand['tabular_view']),step) if j!=0]+ [len(bin_diversity(content_rand['tabular_view']))]
    #store random sum diversity in data_out
    data_sum['random'] = diversities_sum_rand
    data_hist['random'] = diversity
    data_sum['x'] = np.arange(0,N+1,1000)
    data_hist['x'] = np.arange(0,len(content_imgep['tabular_view'])+1,step)
    data_sum.to_csv('progression_sum.csv',header=True)
    data_hist.to_csv('progression_hist.csv',header=True)


    # plot hist diversity for random
    ax2.plot(range(0,len(content_rand['tabular_view'])+1,step),diversity,'-o',label=label)
    ax1.grid()
    ax2.grid()
    ax1.set_title('Entire space Diversity', fontsize=19)
    ax2.set_title('Entire space Diversity', fontsize=19)
    ax1.set_ylabel('sum of squares of distances between all pairs', fontsize=12)
    ax2.set_ylabel('number of bins filled', fontsize=19)
    ax1.set_xlabel('iterations', fontsize=19)
    ax2.set_xlabel('iterations', fontsize=19)
    ax1.legend(prop={'size': 19})
    plt.savefig(name)
    plt.show()
