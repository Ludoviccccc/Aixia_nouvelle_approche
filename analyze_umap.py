import pickle
import numpy  as np
from exploration.load_file import load
from diversity.diversty import Diversity
import matplotlib.pyplot as plt

if __name__=='__main__':
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
    #diversity_ = Diversity(min_tab = min_tab,
    #                        max_tab = max_tab,
    #                        num_bins = 10)
    #
    #print(f'diversity imgep {diversity_(content_imgep_tab)}/10**{dim_out}')
    #diversity_imgep_list = [diversity_(content_imgep_tab[:print_freq*step]) for step in range(N//print_freq)]
    #plt.plot(range(0,N,print_freq),diversity_imgep_list,'-.',label="imgep")
    #
    #
    #print(f'diversity random {diversity_(content_random_tab)}/10**{dim_out}')
    #
    #diversity_random_list = [diversity_(content_random_tab[:print_freq*step]) for step in range(N//print_freq)]
    #plt.plot(range(0,N,print_freq),diversity_random_list,'-.',label="random")
    #plt.legend()
    #plt.title('diversity over experiences')
    #plt.xlabel('experience')
    #plt.ylabel(f'number of bins filled out of 10**{dim_out}')
    #plt.show()
    #
    ##Attempt to reduce dimension - UMAP
    #import umap
    #from sklearn.cluster import HDBSCAN
    ########################################################
    #tab_misses_l2_imgep = np.array(content_imgep['memory_observation']['cache_misses_l2'])
    #data = tab_misses_l2_imgep
    ##min max norm
    #print('data shape', data.shape)
    #print('min data',data.min(axis=0).shape)
    #data = (data - data.min(axis=0))/(1+ data.max(axis=0) - data.min(axis=0))

    #reducer = umap.UMAP(n_components=3,metric="cosine")
    #embedding = reducer.fit_transform(data)
    #print(embedding.shape)
    #plt.figure()
    #plt.scatter(
    #embedding[:, 0],
    #embedding[:, 1])
    #plt.title('umap on l2 cache misses')
    #plt.show()
    #hdb = HDBSCAN(copy=True, min_cluster_size=400)
    #hdb.fit(embedding)
    #hdb.labels_
    #print('labels',np.unique(hdb.labels_))
    #data_list = {key:[] for key in np.unique(hdb.labels_)}
    #for j in range(N):
    #    data_list[hdb.labels_[j]].append(embedding[j])
    #plt.figure()
    #for j,key in enumerate(data_list):
    #    plt.scatter(np.array(data_list[key])[:,0],np.array(data_list[key])[:,1],color = ['black','blue','yellow','pink','red'][j],label=f'label = {key}')
    #plt.show()
    
    #######################################################

    data = np.array(content_imgep['numpy_view'])
    #min max norm
    print('data shape', data.shape)
    print('min data',data.min(axis=0).shape)
    data = (data - data.min(axis=0))/(1+ data.max(axis=0) - data.min(axis=0))

    #reducer = umap.UMAP()
    #embedding = reducer.fit_transform(data)
    #print(embedding.shape)
    #plt.figure()
    #plt.scatter(
    #embedding[:, 0],
    #embedding[:, 1])
    #plt.title('umap on entire imgep data')
    #plt.show()
    #######################################################
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_samples, silhouette_score
    for n_clusters in range(2,6):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto").fit(data)
        labels = kmeans.labels_
        silhouette_avg = silhouette_score(data, labels)
        print(
        "For n_clusters =",
        n_clusters,
        "The average silhouette_score is :",
        silhouette_avg,
        )
