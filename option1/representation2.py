import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.lr_scheduler import MultiplicativeLR
from torch.utils.data import DataLoader
import numpy as np

class VAE(nn.Module):
    def __init__(self, in_, dim):
        super().__init__()
        self.dim = dim  # latent dimension
        
        # Encoder layers
        self.linear1 = nn.Linear(in_, 64)
        self.linear2 = nn.Linear(64, 32)
        self.linear3 = nn.Linear(32, 32)
        self.linear4 = nn.Linear(32, 10)
        self.linear5_mu = nn.Linear(10, dim)  # mean of latent distribution
        self.linear5_logvar = nn.Linear(10, dim)  # log variance of latent distribution
        
        # Decoder layers
        self.linear6 = nn.Linear(dim, 10)
        self.linear7 = nn.Linear(10, 32)
        self.linear8 = nn.Linear(32, 32)
        self.linear9 = nn.Linear(32, 64)
        self.linear10 = nn.Linear(64, in_)
        self.actv = nn.ReLU()

    def forward(self, x):
        mu, logvar = self.encoder(x)
        z = self.reparameterize(mu, logvar)
        recon_x = self.decoder(z)
        return recon_x, mu, logvar

    def encoder(self, x):
        x = self.linear1(x)
        x = self.actv(x)
        x = self.linear2(x)
        x = self.actv(x)
        x = self.linear3(x)
        x = self.actv(x)
        x = self.linear4(x)
        x = self.actv(x)
        mu = self.linear5_mu(x)
        logvar = self.linear5_logvar(x)
        return mu, logvar

    def decoder(self, z):
        z = self.linear6(z)
        z = self.actv(z)
        z = self.linear7(z)
        z = self.actv(z)
        z = self.linear8(z)
        z = self.actv(z)
        z = self.linear9(z)
        z = self.actv(z)
        z = self.linear10(z)
        return z

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def sample(self, num_samples, device='cpu'):
        """Generate samples from the latent space"""
        z = torch.randn(num_samples, self.dim).to(device)
        return self.decoder(z)

def vae_loss(recon_x, x, mu, logvar):
    """VAE loss = reconstruction loss + KL divergence"""
    # Reconstruction loss (MSE)
    recon_loss = F.mse_loss(recon_x, x, reduction='sum')
    
    # KL divergence between N(mu, logvar) and N(0, 1)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    return recon_loss + kl_loss

def vae_training(dataset, vae, n_epochs=1000, lr=1e-6, batch_size=128):
    """Training function for VAE"""
    optim = torch.optim.Adam(vae.parameters(), lr=lr)
    data = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    lmbda = lambda epoch: 0.99999
    scheduler = MultiplicativeLR(optim, lr_lambda=lmbda)
    loss_record = []
    mse_record = []
    
    for epoch in range(n_epochs):
        local_loss_record = []
        for x in data:
            optim.zero_grad()
            recon_x, mu, logvar = vae(x)
            loss = vae_loss(recon_x, x, mu, logvar)
            loss.backward()
            optim.step()
            local_loss_record.append(loss.item())
        mean_loss = np.mean(local_loss_record)
        loss_record.append(mean_loss)
        scheduler.step()
        
        if epoch % 100 == 0:
            print(f'epoch {epoch}, loss {mean_loss}')
        if epoch % 500 == 0:
            torch.save(vae.state_dict(), f"weights/vae_{epoch}.pt")
    
    return loss_record
