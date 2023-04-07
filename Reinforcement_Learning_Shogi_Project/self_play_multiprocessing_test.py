"""# self_play.py
# 셀프 플레이
"""

# 패키지 임포트
from game import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
from pathlib import Path
import numpy as np
import pickle
import os

import torch
from dual_network import PATH, ResNet18

# import time, sys
from multiprocessing import Process, Queue

# 파라미터 준비
SP_GAME_COUNT = 2 # * THREAD # 500 # 셀프 플레이를 수행할 게임 수(오리지널: 25,000)
SP_TEMPERATURE = 1.0  # 볼츠만 분포의 온도 파라미터
THREAD = 4 # cpu쓰레드 갯수

# 선 수를 둔 플레이어 가치
def first_player_value(ended_state):
    # 1: 선 수 플레이어 승리, -1: 선 수 플레이어 패배, 0: 무승부
    if ended_state.is_lose():
        return -1 if ended_state.is_first_player() else 1
    return 0

# 학습 데이터 저장
def write_data(history):
    now = datetime.now()
    os.makedirs('./data/', exist_ok=True)  # 폴더가 없는 경우에는 생성
    path = './data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    with open(path, mode='wb') as f:
        pickle.dump(history, f)

# # 1 게임 실행
# def play1(model):
#     # 학습 데이터
#     history = []

#     # 상태 생성
#     state = State()

#     while True:
#         # 게임 종료 시
#         if state.is_done():
#             break

#         # 합법적인 수의 확률 분포 얻기
#         scores = pv_mcts_scores(model, state, SP_TEMPERATURE)

#         # 학습 데이터에 상태와 정책 추가
#         policies = [0] * DN_OUTPUT_SIZE
#         for action, policy in zip(state.legal_actions(), scores):
#             policies[action] = policy
#         history.append([state.pieces_array(), policies, None])

#         # 행동 얻기
#         action = np.random.choice(state.legal_actions(), p=scores)

#         # 다음 상태 얻기
#         state = state.next(action)

#     # 학습 데이터에 가치 추가
#     value = first_player_value(state)
#     for i in range(len(history)):
#         history[i][2] = value
#         value = -value

#     return history

# 1 게임 실행, 멀티프로세싱
def play_with_multiprocessing(queue, model):
    # 학습 데이터
    history = []

    # 상태 생성
    state = State()

    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 합법적인 수의 확률 분포 얻기
        scores = pv_mcts_scores(model, state, SP_TEMPERATURE)

        # 학습 데이터에 상태와 정책 추가
        policies = [0] * DN_OUTPUT_SIZE
        for action, policy in zip(state.legal_actions(), scores):
            policies[action] = policy
        history.append([state.pieces_array(), policies, None])

        # 행동 얻기
        action = np.random.choice(state.legal_actions(), p=scores)

        # 다음 상태 얻기
        state = state.next(action)

    # 학습 데이터에 가치 추가
    value = first_player_value(state)
    for i in range(len(history)):
        history[i][2] = value
        value = -value

    queue.put(history)
    return

# 셀프 플레이
def self_play():
    # 학습 데이터
    history = []

    # 베스트 플레이어 모델 로드
    model = ResNet18()
    model.load_state_dict(torch.load(PATH, map_location=torch.device('cpu')))
    # model = load_model('./model/best.h5')

    # 여러 차례 게임 실행
    for i in range(SP_GAME_COUNT):
        # 게임 1회 실행
        # h = play1(model)
        tasks = []
        queue = Queue()

        for i in range(0, THREAD):
            thrd = Process(target = play_with_multiprocessing, args = (queue, model)) 
            tasks.append(thrd)
            thrd.start()

        for task in tasks:
            task.join()

        queue.put('END')
        while True:
            tmp = queue.get()

            if tmp == 'END':
                break
            history.extend(tmp)

        print()
        print('len(history) = ', len(history))

        # 출력
        print('\rSelfPlay {}/{}'.format((i+1)*(THREAD), SP_GAME_COUNT*(THREAD)), end='')
    print('')

    # 학습 데이터 저장
    write_data(history)

    # 모델 삭제
    del model

# 동작 확인
if __name__ == '__main__':
    self_play()