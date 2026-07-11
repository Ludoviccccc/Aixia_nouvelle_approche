import numpy as np

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
