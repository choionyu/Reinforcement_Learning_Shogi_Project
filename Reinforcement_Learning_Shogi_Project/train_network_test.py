import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
import torch.optim as optim
import os
import numpy as np

from dual_network import DN_INPUT_SHAPE

from pathlib import Path
from dual_network import ResNet18, PATH
import pickle

# 파라미터 준비
RN_EPOCHS = 100  # 학습 횟수

def load_data():
  history_path = sorted(Path('./data').glob('*.history'))[-1]
  with history_path.open(mode='rb') as f:
    return pickle.load(f)

def train_network():
  history = load_data()
  xs, y_policies, y_values = zip(*history)
  print(len(history))
  print('history = ', history)
  # model = ResNet18()
  # model.load_state_dict(torch.load(PATH))

  # cudnn.benchmark = True
  # optimizer = optim.Adam(model.parameters(), weight_decay=0.0002)

  # for _ in range(RN_EPOCHS):
  #   torch.cuda.empty_cache()
  #   train(model, optimizer)

  # torch.save(model.state_dict(), PATH)

  # del model

def train(model, optimizer):
  device = 'cuda'
  model = model.to(device)
  model = torch.nn.DataParallel(model)

  history = load_data()
  xs, y_policies, y_values = zip(*history)
  xs = np.array(xs, dtype=np.float32)
  y_values =np.array(y_values, dtype = np.float32)
  # print(xs.shape)
  # print(len(xs))
  a, b, c = DN_INPUT_SHAPE

  xs = xs.reshape(len(xs), a, b, c)
  # print(xs.shape)
  xs = torch.tensor(xs, requires_grad=True)
  y_policies = torch.tensor(y_policies, requires_grad=True)
  y_values = torch.tensor(y_values, requires_grad=True)

  xs = xs.to(device)
  y_policies = y_policies.to(device)
  y_values = y_values.to(device)

  # print(xs, y_policies, y_values)
  # print(xs.shape)

  optimizer.zero_grad()
  model.eval()
  with torch.no_grad():
    p, v = model(xs)

  v = v.reshape(len(v))
  # print(y_policies.shape)
  # v = v.reshape(len(v))
  # print(v.shape)
  # print(y_values.shape)

  model.train()
  celoss = nn.CrossEntropyLoss()
  mseloss = nn.MSELoss()
  loss1 = celoss(p, y_policies)
  loss2 = mseloss(v, y_values)
  
  loss1.backward(retain_graph=True)
  loss2.backward()

  optimizer.step()

# 동작 확인
if __name__ == '__main__':
    train_network()



