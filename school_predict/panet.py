# 导入相应包
import torch
import torch.nn.functional as F


class PAnet(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output, hidden_num=1):
        super(PAnet, self).__init__()
        self.hidden1 = torch.nn.Linear(n_feature, n_hidden)   # hidden1 layer
        self.hidden2 = torch.nn.ModuleList([torch.nn.Linear(n_hidden, n_hidden) for i in range(hidden_num)])
        self.predict = torch.nn.Linear(n_hidden, n_output)   # output layer        
        
    def forward(self, x):
        x = F.relu(self.hidden1(x)) 
        for i, h in enumerate(self.hidden2):
            x = F.relu(h(x))
        x = self.predict(x) # linear output
        return x

def panet(df_data, col_x, col_y, predict_range):
    data = df_data
    x = data[col_x].to_list()
    y = data[col_y].to_list()
    x = torch.unsqueeze(torch.FloatTensor(x), dim=1) 
    x = x - x[0]
    cp = torch.unsqueeze(torch.FloatTensor(y), dim=1)
    cp = cp / 1000

    predict_x = [[x[-1] + i - x[0]] for i in range(1, predict_range + 1)]

    EPOCH = 20000 # 训练次数
    LR = 0.00001 # 学习率
    HIDDEN_SIZE = 32 # 隐藏层网络宽度
    HIDDEN_LAYERS = 8 # 隐藏层深度

    loss_list = []
    cn_panet = PAnet(n_feature=1, n_hidden=HIDDEN_SIZE, n_output=1, hidden_num=HIDDEN_LAYERS-1)     # define the network
    optimizer = torch.optim.SGD(cn_panet.parameters(), lr=LR)  # 调小学习率
    loss_func = torch.nn.MSELoss()  # this is for regression mean squared loss
    cn_panet.train()
    for t in range(EPOCH):
        prediction = cn_panet(x)          # input x and predict based on x
        loss = loss_func(prediction, cp)     # must be (1. nn output, 2. target)
        loss_list.append(loss.detach())

        optimizer.zero_grad()                # clear gradients for next train
        loss.backward()                      # backpropagation, compute gradients
        optimizer.step()                     # apply gradients 
    cn_panet.eval()
    predict_x = torch.FloatTensor(predict_x)
    with torch.no_grad():
        results = cn_panet(predict_x)
        results = results * 1000
    return results.view(-1).numpy().tolist()