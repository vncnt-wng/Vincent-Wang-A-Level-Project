"""
put data into correct form for network input/target outputs
"""

import torch
from torch import autograd
import random as r

typicalSpread = 0.00007


def readIn(dataPath):
    toReturn = []

    with open(dataPath, 'r') as file:
        #skip header line
        next(file)
        for line in file:
            ohlc = line.split(',')[1:-1]
            toReturn.append([float(x) for x in ohlc])
    
    return toReturn


def getMovementTargets(noPrev, toPredict, data):

    targets = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):

        #most recent close price
        finalClose = data[i+noPrev-1][3]

        value = data[i+noPrev+toPredict][3] - finalClose
        if value >= typicalSpread:
            targets.append([1, 0, 0])
        elif value <= -(typicalSpread):
            targets.append([0, 0, 1])
        else:
            targets.append([0, 1, 0])

    return autograd.Variable(torch.tensor(targets).float())


def getPredictionTargets(noPrev, toPredict, data):

    targets = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):
        #take the close price
        targets.append([data[i+noPrev+toPredict][-1]])

    return autograd.Variable(torch.tensor(targets).float())


def getLSTMProcessed(noPrev, toPredict, data):
    #separate into the inputs for one feedForward run
    inputs = []
    means = []

    for i in range(0, len(data) - noPrev - toPredict):
        total = 0
        temp = []

        for j in range(i, i+noPrev):
            temp.append(data[j])
            total += data[j][-1]

        #"normalise"
        mean = total/noPrev
        means.append(torch.tensor([mean]))
        normalised = []

        for x in range(0, len(temp)):
            ohlcNorm = []
            for y in range(0, len(temp[x])):
                ohlcNorm.append(temp[x][y]-mean)
            normalised.append(ohlcNorm)

        inputs.append(normalised)
    return torch.stack(means), autograd.Variable((torch.tensor(inputs))*100)


def getConvProcessed(noPrev, toPredict, data, takeRelative=False):
    
    inputs = []

    #for each item in datafile
    for i in range(0, len(data) - noPrev - toPredict):
        
        #most recent close price
        finalClose = 0 
        
        if takeRelative: 
            finalClose = data[i+noPrev-1][3]

        #"rotate" data so it can be convolved
        o, h, l, c = [], [], [], []
        for j in range(i, i+noPrev):
            
            localOpen = 0
            
            if takeRelative: 
                data[j][0]
                
            o.append(data[j][0] - finalClose)
            h.append(data[j][1] - localOpen)
            l.append(data[j][2] - localOpen)
            c.append(data[j][3] - finalClose)
        inputs.append([o, h, l, c])


    #return inputs and as autograd variable, scale the relative values used
    if takeRelative:
        return autograd.Variable(torch.tensor(inputs)*1000)
    else:
        return autograd.Variable(torch.tensor(inputs))


def getBatch(inputs, targets):
    #take a proportion of the training data
    batchProp = 0.2
    length = int(len(inputs)*batchProp)
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]


def splitData(tensor):
    #split data into training/testing
    splitProp = 0.8
    splitIndex = int(len(tensor)*splitProp)

    return tensor[:splitIndex], tensor[splitIndex:]


def get(noPrev, toPredict, dataPath, conv=False, price=False):
    #get data from previous timesteps + the target for the prediction

    data = readIn(dataPath)
    inputs = None
    targets = None
    means = None

    if conv:
        inputs = getConvProcessed(noPrev, toPredict, data)
    else:
        means, inputs = getLSTMProcessed(noPrev, toPredict, data)
    
    if price:
        targets = getPredictionTargets(noPrev, toPredict, data)    
    else:
        targets = getMovementTargets(noPrev, toPredict, data)  

    #move to GPU
    inputs = inputs.cuda()
    targets = targets.cuda()
    means = means.cuda()

    meansSep = splitData(means)
    insSep = splitData(inputs)
    targetSep = splitData(targets)

    return meansSep[0], meansSep[1], insSep[0], insSep[1], targetSep[0], targetSep[1]


def getRandom(inputs, targets, length):
    #return random sample 
    startIndex = r.randint(0, len(inputs) - length)
    return inputs[startIndex:startIndex+length], targets[startIndex:startIndex+length]

"""    
trai, trat, testi, test = get(1, 1, "data/OHLC15sample.csv", conv=False, raw=True)
print(trai)
"""