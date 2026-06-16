import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.lr_scheduler import MultiplicativeLR

from torch.utils.data import DataLoader
import numpy as np
class AE(nn.Module):
    def __init__(self,in_,dim):
        super().__init__()
        self.linear1 = nn.Linear(in_,32)
        self.linear2 = nn.Linear(32,10)
        self.linear3 = nn.Linear(10,10)
        self.linear4 = nn.Linear(10,32)
        self.linear5 = nn.Linear(32,32)
        self.linear6 = nn.Linear(32,in_)
        self.actv = nn.ReLU()

    def forward(self,x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x
    def encoder(self,x):
        x = self.linear1(x)
        x = self.actv(x)
        x = self.linear2(x)
        x = self.actv(x)
        x = self.linear3(x)
        return x
    def decoder(self,x):
        x = self.actv(x)
        x = self.linear4(x)
        x = self.actv(x)
        x = self.linear5(x)
        x = self.actv(x)
        x = self.linear6(x)
        return x

def training(dataset,ae,n_epochs = 1000,lr=1e-6,batch_size = 128):
    optim = torch.optim.Adam(ae.parameters(),lr=lr)
    data = DataLoader(dataset,batch_size = batch_size,shuffle=True)
    lmbda = lambda epoch: 0.99999
    scheduler = MultiplicativeLR(optim, lr_lambda=lmbda)
    loss_record = []
    for epoch in range(n_epochs):
        local_loss_record = []
        for x in data:
            optim.zero_grad()
            loss = F.mse_loss(x,ae(x))
            loss.backward()
            optim.step()
            local_loss_record.append(loss.item())
        mean_loss = np.mean(local_loss_record)
        loss_record.append(mean_loss)
        scheduler.step()
        if epoch%100==0:
            print(f'epoch {epoch}, loss {mean_loss}')



class Representation:
    def __init__(self,dim=12):
        self.dim = dim
        self.v_t = 0
    def __call__(self,x:np.array):
        return (x@self.v_t.T)[:,:self.dim]
    def update(self,x):
        u,sig,v_t = np.linalg.svd(x)
        self.v_t = v_t
        self.sig = sig
        lmbda = lambda x:1.0/x/(1/sum(1.0/x))
        self.weights = lmbda(self.sig[:self.dim])
