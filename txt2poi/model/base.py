import torch
import numpy as np
import os
import sys
import pandas as pd
from torch._C import dtype
import torch.utils.data as data
import torch.nn.functional as F

train=os.path.exists('./train.csv')
dev=os.path.exists('./dev.csv')

if not (train and dev):
    data_df = pd.read_csv('/home/fjb/ccf-edupre/data/info/matched_gdpoi_point.csv', encoding='gbk')
    train_df = data_df.sample(frac=0.8)
    dev_df = data_df[~data_df.index.isin(train_df.index)]
    train_df[['point_x','point_y','gd_point_x','gd_point_y']].to_csv('./train.csv', index=False)
    dev_df[['point_x','point_y','gd_point_x','gd_point_y']].to_csv('./dev.csv', index=False)

class XyzDataset(data.Dataset):
    """
    Base Dataset
    """
    def __init__(self, root, name):
        self.root = root
        path = os.path.join(root, name + ".csv")
        if not os.path.exists(path):
            print("[ERROR] {} file does not exist!".format(path))
            assert(0)
        self.data = pd.read_csv(path)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        point_x = row['point_x']
        point_y = row['point_y']
        gd_point_x = row['gd_point_x']
        gd_point_y = row['gd_point_y']

        x = [point_x, point_y]
        x = torch.FloatTensor(x)
        y = [gd_point_x, gd_point_y]
        y = torch.FloatTensor(y)

        return x, y
    
    def __len__(self):
        return len(self.data)

dataset = XyzDataset('./', 'train')
train_data_loader = data.DataLoader(dataset=dataset, batch_size=512, shuffle=True, pin_memory=True)

dataset = XyzDataset('./', 'dev')
dev_data_loader = data.DataLoader(dataset=dataset, batch_size=512, pin_memory=True)

class MLP(torch.nn.Module):
    def __init__(self,n_feature,n_hidden,n_output):
        super(MLP,self).__init__()
        #两层感知机
        self.hidden = torch.nn.Linear(n_feature,n_hidden)
        self.hidden1 = torch.nn.Linear(n_hidden,n_hidden)
        self.hidden2 = torch.nn.Linear(n_hidden,n_hidden)
        self.hidden3 = torch.nn.Linear(n_hidden,n_hidden)
        self.hidden4 = torch.nn.Linear(n_hidden,n_hidden)
        self.predict = torch.nn.Linear(n_hidden,n_output)
 
    def forward(self,x):
        x = F.relu(self.hidden4(self.hidden3(self.hidden2(self.hidden1(self.hidden(x))))))
        x = self.predict(x)
        return x
 
model = MLP(2,64,2)  #输入节点1个，隐层节点8个，输出节点
if torch.cuda.is_available():
    model.cuda()
optimizer = torch.optim.SGD(model.parameters(), lr = 0.00001)
loss_func = torch.nn.MSELoss()
epochs = 5000
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
best_loss = 10000000000

for epoch in range(epochs):
    model.train()
    for step, (x, y) in enumerate(train_data_loader):
        if torch.cuda.is_available():
            x = x.cuda()
            y = y.cuda()
        prediction = model(x)
        loss = loss_func(prediction, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # sys.stdout.write('[Train] epoch {0:2} step: {1:3} | loss: {2:3.4f}'.format(epoch, step, loss.item()) + '\r')
        # sys.stdout.flush()
    
    model.eval()
    with torch.no_grad():
        for step, (x, y) in enumerate(dev_data_loader):
            if torch.cuda.is_available():
                x = x.cuda()
                y = y.cuda()
            prediction = model(x)
            loss = loss_func(prediction, y)
            if loss < best_loss:
                best_loss = loss
                best_predictions = prediction
            sys.stdout.write('[Dev] epoch {} | loss: {:.4f}'.format(epoch, loss.item()) + '\r')
            sys.stdout.flush()

pre_xs = []
pre_ys = []
dev_df = pd.read_csv('./dev.csv')
for pre in best_predictions:
    pre_x = pre[0].item()
    pre_y = pre[1].item()
    pre_xs.append(pre_x)
    pre_ys.append(pre_y)
dev_df['prex'] = pre_xs
dev_df['prey'] = pre_ys
dev_df.to_csv('./dev.csv', index=False)


