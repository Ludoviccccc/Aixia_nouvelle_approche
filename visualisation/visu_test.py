import numpy as np
import sys
sys.path.append('../../')
from exploration.load_file import load
from scipy import stats as st
import pickle
import os
def compute_total_diversity(content_rand_name,content_name,m=2,name='diversity_comparaison'):    
    diff = lambda tab,j: np.sum(np.abs(tab[j+1:,:]-tab[j,:])**2,axis=1)
    content_rand = load(content_rand_name,0)
    N = len(content_rand['tabular_view'])
    diversities_rand = np.zeros((m,(N//1000)+1))
    diversities_std = np.zeros(((N//1000)+1))
    for l in range(m):
        distances = [[] for j in range(N)]
        content_rand = load(content_rand_name,l)
        t_crit_interval = st.t.interval(confidence=0.95, df=m - 1)
        print(t_crit_interval)
        for j in range(N):
            distances[j] = diff(content_rand['tabular_view'],j)
        for j,n in enumerate(range(0,N+1,1000)):
            diversities_rand[l,j] = np.sum([np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])])
    diversities_rand_var = np.var(diversities_rand,axis=0).reshape((-1))
    diversities_rand_mean = np.mean(diversities_rand,axis=0).reshape((-1))
    #print(diversities_rand_var.shape)
    diversities = np.zeros((m,len(content_name),1+N//1000))
    start = 0
    for f,vec in enumerate(content_name):
        name = vec[0]
        for l in range(m):
            content_imgep = load(name,l)
            distances = [[] for j in range(len(content_imgep['tabular_view']))]
            for j in range(len(content_imgep['tabular_view'])):
                distances[j] = diff(content_imgep['tabular_view'],j)
            for j,n in enumerate(range(0,N+1,1000)):
                diversities[l,f,j] = np.sum([np.sum(o[:n-i]) for i,o in  enumerate(distances[:n])])
    diversities_imgep_var = np.var(diversities,axis=0)
    diversities_imgep_mean = np.mean(diversities,axis=0)
    #print(diversities_imgep_var)
    #print(diversities_imgep_mean)
    

    output = {'imgep':{'mean':diversities_imgep_mean,'var':diversities_imgep_var},
            'random':{'mean':diversities_rand_mean,'var':diversities_rand_var},
            't_crit_interval':t_crit_interval,
            'm':m,
            'N':N}
    with open(os.path.join('results','stats_plots.pkl'),'wb') as f:
        pickle.dump(output,f)
    
#    for f,vec in enumerate(content_name):
#        name = vec[0]
#        label = vec[1]
#        y = diversities_imgep_mean[f][start:]
#        x = np.arange(0,N+1,1000)[start:]
#        ci = diversities_imgep_var[f][start:] *t_crit_interval[1]/np.sqrt(m)
#        print('ci shape', ci.shape)
#        plt.plot(x,y,'-o',label=label)
#        #plt.fill_between(x, (y-ci), (y+ci), color='b', alpha=.1)
#    plt.plot(np.arange(0,N+1,1000)[start:],diversities_rand_mean[start:],'-o',label=f'random')
#    plt.grid()
#    plt.title('Entire space Diversity IMGEP vs RANDOM', fontsize=19)
#    plt.ylabel('sum of squares of distances between all pairs', fontsize=12)
#    plt.xlabel('iterations', fontsize=19)
#    plt.xticks(range(0,10001,1000)[start:])
#    plt.legend(prop={'size': 19})
#    #plt.savefig(name)
#    plt.show()
#    exit()
