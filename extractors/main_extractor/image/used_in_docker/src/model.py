import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
# import matplotlib.pyplot as plt
import time
import os
import copy
import json
import data


def load_model(model_path=''): # load model
    print('==> Loading model..')
    checkpoint = None
    if torch.cuda.is_available():
        checkpoint = torch.load(model_path)
    else:
        checkpoint = torch.load(model_path, map_location=lambda storage, loc: storage)
    model_ft = checkpoint['net']
    best_acc = checkpoint['acc']
    start_epoch = checkpoint['epoch']
    return model_ft


def predict(model, datas):  # predict
    model.eval()
    using_gpu = torch.cuda.is_available()
    prediction = None

    for batch_number in range(len(datas)):
        cur_data = data.get_images(datas[batch_number])
        inputs = torch.Tensor(cur_data)
        if using_gpu:
            inputs = Variable(inputs.cuda())
        else:
            inputs = Variable(inputs)

        outputs = model(inputs)
        _, preds = torch.max(outputs.data, 1)

        if prediction is None:
            prediction = np.array(preds)
        else:
            prediction = np.concatenate((prediction, preds))

    return prediction
