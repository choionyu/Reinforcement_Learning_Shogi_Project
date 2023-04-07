"""# dual_network.py"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
import torch.optim as optim
import os
import numpy as np

from pathlib import Path
import pickle

# 파라미터 준비
DN_FILTERS = 128  # 컨볼루션 레이어 커널 수(오리지널 256）
# DN_RESIDUAL_NUM = 16  # 레지듀얼 블록 수(오리지널 19)
DN_INPUT_SHAPE = (14, 10, 9)  # 입력 셰이프
DN_OUTPUT_SIZE = 5220  # 행동 수(말의 이동 도착 위치(90) * 말의 이동 시작 위치(58))
PATH = './model/best.h5'

class BasicBlock(nn.Module):
    def __init__(self, in_planes, planes, stride=1):
        super(BasicBlock, self).__init__()

        self.conv1 = self.conv3x3(in_planes, planes)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = self.conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)

    def conv3x3(self, in_planes, planes, stride=1):
        return nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride,
                         padding=1, bias=False)

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += x
        # print(out.shape)
        return out

class ResNet(nn.Module):
  def __init__(self, block, num_blocks):
    super(ResNet, self).__init__()
    self.in_planes = DN_FILTERS

    # 64개의 3x3 필터(filter)를 사용
    self.conv1 = nn.Conv2d(14, DN_FILTERS, kernel_size=3, stride=1, padding=1, bias=False)
    self.bn1 = nn.BatchNorm2d(DN_FILTERS)
    print()
    self.layer1 = self._make_layer(block, DN_FILTERS, num_blocks[0], stride=1)
    self.layer2 = self._make_layer(block, DN_FILTERS, num_blocks[1], stride=1)
    self.layer3 = self._make_layer(block, DN_FILTERS, num_blocks[2], stride=1)
    self.layer4 = self._make_layer(block, DN_FILTERS, num_blocks[3], stride=1)
    self.linear_p = nn.Linear(DN_FILTERS, DN_OUTPUT_SIZE)
    self.linear_v = nn.Linear(DN_FILTERS, 1)

  def _make_layer(self, block, planes, num_blocks, stride):
    strides = [stride] + [1] * (num_blocks - 1)
    layers = []
    for stride in strides:
        layers.append(block(self.in_planes, planes, stride))
        self.in_planes = planes # 다음 레이어를 위해 채널 수 변경
    return nn.Sequential(*layers)

  def forward(self, x):
    # print('x = ', x.shape)
    out = torch.relu(self.bn1(self.conv1(x)))
    # print('out0 = ', out.shape)
    out = self.layer1(out)
    # print('out1 = ', out.shape)
    out = self.layer2(out)
    # print('out2 = ', out.shape)
    out = self.layer3(out)
    # print('out3 = ', out.shape)
    out = self.layer4(out)
    # print('out4 = ', out.shape)
    out = F.adaptive_avg_pool2d(out, (1, 1))
    # print('out5 = ', out.shape)
    out = out.view(out.size(0), -1)
    # print('out6 = ', out.shape)
    p = self.linear_p(out)
    v = self.linear_v(out)
    # print('p1 = ', p.shape)
    # print('v1 = ', v.shape)
    # p = F.softmax(p)
    v = torch.tanh(v)
    # print('p2 = ', p.shape)
    # print('v2 = ', v.shape)
    return p, v
  
def ResNet18():
  return ResNet(BasicBlock, [2, 2, 2, 2])

def dual_network():
  # 모델 생성이 완료된 경우 처리하지 않음
  if os.path.exists('./model/best.h5'):
    return
  
  model = ResNet18()
  os.makedirs('./model/', exist_ok=True)  # 폴더가 없는 경우 생성
  torch.save(model.state_dict(), PATH)

  del model

# 동작 확인
if __name__ == '__main__':
    dual_network()