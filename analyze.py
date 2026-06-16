import pickle
from exploration.load_file import load
folder = "results"
N = 10000
k=1
name = f'{folder}/imgep_N_{N}_k_{k}'
content = load(name)

#print(content['numpy_view'].shape)
#print(content['memory_observation'].keys())

import numpy as np
#out = np.linalg.svd(content['numpy_view'])
##print(out[1])
#import matplotlib.pyplot as plt
#
#plt.plot(range(len(out[1])),out[1],'-o')
#plt.show()

#from sklearn.mixture import GaussianMixture
#
#
#gm = GaussianMixture(n_components=2, random_state=0).fit(content['numpy_view'])
#print(gm.aic(content['numpy_view']))
#
#
#

from option1.representation2 import VAE,vae_training


vae = VAE(content['numpy_view'].shape[1],5)
import torch
dataset = np.array(content['numpy_view'])
dataset = torch.Tensor(dataset)
print(sum(dataset[:,-1]))
print(dataset.min(dim=0)[0].shape)
#exit()
dataset = (dataset - dataset.min(dim=0)[0])/(dataset.max(dim=0)[0] - dataset.min(dim=0)[0])
vae_training(dataset,vae,n_epochs=1000)
#
#from sklearn.cluster import HDBSCAN
#from sklearn.datasets import load_digits
#
#
##X, _ = load_digits(return_X_y=True)
#
#hdb = HDBSCAN(copy=True, min_cluster_size=20)
#hdb.fit(dataset)
#
#hdb.labels_.shape == (dataset.shape[0],)
#
#
#print(np.unique(hdb.labels_).tolist())
