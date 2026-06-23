import pickle
import numpy  as np
from exploration.load_file import load
from diversity.diversty import Diversity
import matplotlib.pyplot as plt


#Load data
folder = "results"
N = 10000
k=1
address_x = 5
print_freq = 1000
name_imgep = f'{folder}/imgep_N_{N}_k_{k}'
name_random = f'{folder}/random_expl_N_{N}'
content_imgep = load(name_imgep)
content_imgep_tab = content_imgep['numpy_view']
content_random = load(name_random)
content_random_tab = content_random['numpy_view']
dim_out = 40
#Compute diversity
##################################
min_tab = np.zeros((dim_out,))
max_tab = np.ones((dim_out,))*10
min_tab[-1] = 0
#max_tab[-1] = 300
diversity_ = Diversity(min_tab = min_tab,
                        max_tab = max_tab,
                        num_bins = 10)

print(f'diversity imgep {diversity_(content_imgep_tab)}/10**{dim_out}')
diversity_imgep_list = [diversity_(content_imgep_tab[:print_freq*step]) for step in range(N//print_freq)]
plt.plot(range(0,N,print_freq),diversity_imgep_list,'-.',label="imgep")


print(f'diversity random {diversity_(content_random_tab)}/10**{dim_out}')

diversity_random_list = [diversity_(content_random_tab[:print_freq*step]) for step in range(N//print_freq)]
plt.plot(range(0,N,print_freq),diversity_random_list,'-.',label="random")
plt.legend()
plt.title('diversity over experiences')
plt.xlabel('experience')
plt.ylabel(f'number of bins filled out of 10**{dim_out}')
plt.show()

print(min(content_imgep['memory_observation']['time_core0']))
print(max(content_imgep['memory_observation']['time_core0']))
#
#
##Observe time values
###########################################################""
#plt.figure()
#plt.plot(range(N),content_random['memory_observation']['time_core0'],'.',label='random')
#plt.plot(range(N),content_imgep['memory_observation']['time_core0'],'.',label='imgep')
#plt.xlabel('id')
#plt.ylabel('temps cycle')
#plt.legend()
#
##Observe time values wrt average distance of used address to main address address_x
###########################################################""
#def distance2address(address,parameter):
#    parameter_adresses = [parameter[key][1] for key in parameter]
#    output = np.mean(np.abs(address - np.array(parameter_adresses)))
#    return output
#
#mean_distance_to_address_program_imgep = np.array([distance2address(5,param) for param in content_imgep['memory_parameter']])
#mean_distance_to_address_program_random = np.array([distance2address(5,param) for param in content_random['memory_parameter']])
#plt.figure()
#plt.plot(mean_distance_to_address_program_random,content_random['memory_observation']['time_core0'],'.',label="random")
#plt.plot(mean_distance_to_address_program_imgep,content_imgep['memory_observation']['time_core0'],'.',label="imgep")
#plt.xlabel(f'mean L1 distance between used addresses and address X={address_x}')
#plt.ylabel('execution time')
#plt.legend()
#plt.show()
#########################################################
#len_param_random = [len(param) for param in content_random['memory_parameter']]
#len_param_imgep = [len(param) for param in content_imgep['memory_parameter']]
#plt.figure()
#ll=N
#plt.scatter(range(N)[:ll],len_param_random[:ll],label='random')
#plt.scatter(range(N)[:ll],len_param_imgep[:ll],label='imgep')
#plt.legend()
#plt.show()
#Attempt to identify clusters
#######################################################
tab_misses_l2_imgep = np.array(content_imgep['memory_observation']['cache_misses_l2'])
from sklearn.cluster import HDBSCAN
hdb = HDBSCAN(copy=True, min_cluster_size=400)
data = tab_misses_l2_imgep
#min max norm
print('data shape', data.shape)
print('min data',data.min(axis=0).shape)
data = (data - data.min(axis=0))/(1+ data.max(axis=0) - data.min(axis=0))
hdb.fit(data)
print('labels',np.unique(hdb.labels_))
data_list = {key:[] for key in np.unique(hdb.labels_)}
for j in range(N):
    data_list[hdb.labels_[j]].append(tab_misses_l2_imgep[j])
plt.figure()
for j in range(-1,2):
    #if j==0:
    #    pass
   plt.plot(np.mean(data_list[j],axis=0),'-o',label=f'label {j}')
   plt.plot(np.std(data_list[j],axis=0),'-o',label=f'std label {j}')
plt.title('average number of miss for each window')
plt.legend()
plt.show()
#
#
#
for j in range(N):
    plt.plot(tab_misses_l2_imgep[j],['black','blue','yellow','pink','red'][hdb.labels_[j]])
plt.show()
