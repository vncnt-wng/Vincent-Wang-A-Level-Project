import torch
from torch import autograd, nn
import torch.nn.functional as F
import torch.optim as optim

"""
testing saving and loading models/running many training sessions and picking the best

also
 - general cleanups 
 - move training to gpu
"""

batchSize = 20
timesteps = 24
noEpochs = 1000

typicalSpread = 0.00007

toPredict = 1


class model(nn.Module):
    
    def __init__(self, input_no, h1_no, out_no=3):
        super().__init__()
        self.c1 = nn.Conv1d(4, 2, 1)
        self.c2 = nn.Conv1d(2, 1, 1)
        self.h1 = nn.Linear(h1_no, 64)
        self.h2 = nn.Linear(64, 16)
        self.out = nn.Linear(16, out_no)

    def forward(self, x):
        x = F.relu(self.c1(x))
        x = F.relu(self.c2(x))
        x = F.relu(self.h1(x))
        x = F.relu(self.h2(x))
        x = F.relu(self.out(x))
        x = F.softmax(x, dim=2)
        return x


def readIn():
    dataPath = "overfit.txt"
    toReturn = []

    with open(dataPath, 'r') as file:
        #skip header line
        next(file)
        for line in file:
            ohlc = line.split(',')[1:-1]
            toReturn.append([float(x) for x in ohlc])
    
    return toReturn


def getData(noPrev, toPredict):
    
    data = readIn()

    batch = []
    targets = [] 

    #for each item in batch
    for i in range(0, batchSize):

        #most recent close price
        finalClose = data[i+noPrev-1][3]

        #"rotate" data so it can be convolved
        o, h, l, c = [], [], [], []
        for j in range(i, i+noPrev):
            localOpen = data[j][0]
            o.append(data[j][0] - finalClose)
            h.append(data[j][1] - localOpen)
            l.append(data[j][2] - localOpen)
            c.append(data[j][3] - finalClose)


        target = []

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            target.append([1, 0, 0])
        elif value <= -(typicalSpread):
            target.append([0, 0, 1])
        else:
            target.append([0, 1, 0])

        batch.append([o,h,l,c])
        targets.append(target)

    return autograd.Variable(torch.tensor(batch)*1000), autograd.Variable(torch.tensor(targets).float())



smallestLoss = 1 
bestModel = None

#get data from previous timesteps + the target for the prediction
batch, targets = getData(timesteps, toPredict)

#move to gpu
batch = batch.cuda()
targets = targets.cuda()

#run multiple models
for i in range(0, 50):

    print("Training model: " + str(i))

    #init network and optimizer
    net = model(timesteps*4, timesteps)
    optimizer = optim.Adam(net.parameters(), lr=0.002)

    #move net to gpu
    net = net.cuda()
    #set to training mode
    net.train()

    for j in range(0, noEpochs):
        out = net(batch)

        net.zero_grad()
        optimizer.zero_grad()

        lossFunc = nn.MSELoss()
        loss = lossFunc(out, targets)
        loss.backward()

        optimizer.step()

        #if on the final iteration of optimisation
        if j == noEpochs - 1:

            print("Final loss of: " + str(loss.item()) + "\n")
            if loss < smallestLoss:
                smallestLoss = loss
                bestModel = net.state_dict()
    

print("Best model had MSE loss of: " + str(smallestLoss.item()))
torch.save(bestModel, "testModel.pth")
