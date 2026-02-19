import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
def bin_diversity_time_space(content):
    '''
    bin diversity in product time space
    '''
    sup = np.where(content.max(axis=0)>1.0)[0]
    time_space = content[:,sup]
    div = 10*np.ones(time_space.shape[1])
    coords = (time_space)//div
    c = np.unique(coords,axis=0)
    return len(c)
def bin_diversity_miss_space(content):
    '''
    bin diversity in product time space
    '''
    sup = np.where(content.max(axis=0)<=1.0)[0]
    miss_space = content[:,sup]
    div = 5*np.ones(miss_space.shape[1])
    coords = 200*(miss_space)//div
    c = np.unique(coords,axis=0)
    return len(c)
def diversity_time_iteration(list_,name,title=None, folder="images"):
    plt.figure(figsize=(15,10))
    for arg in list_:
        content,label = arg[0],arg[1]
        print(content.keys())
        ll = len(content['tabular_view'])
        diversity_values = [bin_diversity_time_space(content['tabular_view'][:k]) for k in range(100,ll,100)]
        plt.plot(range(100,ll,100),diversity_values, '-o',label=label)
        plt.xlabel("iteration",fontsize=19)
        plt.ylabel("diversity",fontsize=19)
    if title:
        plt.title(title,fontsize=19)
    else:
        plt.title("time",fontsize=19)
    plt.legend(prop={'size': 19})
    if title:
        plt.savefig(f"{folder}/{name}")
    plt.show()
    plt.close()
def diversity_miss_iteration(list_,name,title=None, folder="images"):
    plt.figure(figsize=(15,10))
    for arg in list_:
        content,label = arg[0],arg[1]
        print(content.keys())
        ll = len(content['tabular_view'])
        diversity_values = [bin_diversity_miss_space(content['tabular_view'][:k]) for k in range(100,ll,100)]
        plt.plot(range(100,ll,100),diversity_values, '-o',label=label)
        plt.xlabel("iterations",fontsize=19)
        plt.ylabel("diversity",fontsize=19)
    if title:
        plt.title(title,fontsize=19)
    else:
        plt.title("time",fontsize=19)
    plt.legend(prop={'size': 19})
    if title:
        plt.savefig(f"{folder}/{name}")
    plt.show()
    plt.close()
def scatter_vs_miss(list_,name,title=None, folder="images"):
    plt.figure(figsize=(30,20))
    for j,arg in enumerate(list_):
        content,label = arg[0],arg[1]
        fig,(ax0,ax1) = plt.subplots(1,2,sharex=True,figsize=(12,5))
        x = content['memory_perf']['mutual']['diff_time_core0']
        y = content['memory_perf']['mutual']['diff_time_core1']
        z_0 = content['memory_perf']['mutual']['L2_miss_core0']
        z_0= (z_0 - z_0.min())/(z_0.max()-z_0.min())
        z_1 = content['memory_perf']['mutual']['L2_miss_core1']
        z_1= (z_1 - z_1.min())/(z_1.max()-z_1.min())
        cm = plt.cm.get_cmap('plasma')
        sc0 = ax0.scatter(x,y,c = z_0,label=label,cmap=cm)
        sc1 = ax1.scatter(x,y,c = z_1,label=label,cmap=cm)
        plt.colorbar(sc0, ax=ax0)
        plt.colorbar(sc1, ax=ax1)
        ax0.set_xlabel("time[mutual] - time[iso], core 0",fontsize=19)
        ax0.set_ylabel("time[mutual] - time[iso], core 1",fontsize=19)
        ax1.set_xlabel("time[mutual] - time[iso], core 0",fontsize=19)
        ax1.set_ylabel("time[mutual] - time[iso], core 1",fontsize=19)
        ax0.set_title("Nb L2 misses [mutual] -  Nb L2 misses [iso] core 0")
        ax1.set_title("Nb L2 misses [mutual] -  Nb L2 misses [iso] core 1")
        #plt.suptitle("delay vs nb L2 misses",fontsize=19)
        plt.legend(prop={'size': 19})
        plt.savefig(f"{folder}/delay_vs_L2_{j}")
        plt.show()
        plt.close()
        data = pd.DataFrame([])
        data['diff_time_core0'] = x
        data['diff_time_core1'] = y
        data['L2_miss_core0_normalized'] = z_0
        data['L2_miss_core1_normalized'] = z_1
        data.to_csv('scatter_vs_miss.csv',header='True')
