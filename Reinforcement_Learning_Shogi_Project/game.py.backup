
# 패키지 임포트
import random
import math

# 최대 둘수 있는 수
MAX_DEPTH = 200

# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None, depth=0,idx=None): # depth는 현재 누구 턴인지를 표시한다.
        # 방향 정수
        # self.dxy = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))

        # 말의 배치
        self.pieces = pieces if pieces != None else [0] * (9*10) # 초기 말 배치
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * (9*10)
        self.depth = depth
        

        self.idx = idx ## 스테이트 안에서 사용할 수 있는 전역변수 생성


        # 말의 초기 배치 (적 돌과 내돌의 배치 경우 4가지를 고려 해야한다.
        #                 각각 마상마상,상마상마,마상상마,상마마상)
        # 차 : 1, 졸: 2, 마: 3, 포: 4, 사: 5, 상: 6, 왕: 7

        if pieces == None or enemy_pieces == None:
            if self.idx == None: # 인덱스 설정을 하지 않는 기본값
              a, b, c, d = 3, 6, 3, 6 # 마상마상
            elif self.idx[0] == 0:
              a, b, c, d = 3, 6, 3, 6 # 마상마상
            elif self.idx[0] == 1:
              a, b, c, d = 3, 6, 6, 3 # 마상상마
            elif self.idx[0] == 2:
              a, b, c, d = 6, 3, 6, 3 # 상마상마
            elif self.idx[0] == 3:
              a, b, c, d = 6, 3, 3, 6 # 상마마상
            
            if self.idx == None: # 인덱스 설정을 하지 않는 기본값
              e, f, g, h = 3, 6, 3, 6 # 마상마상
            elif self.idx[1] == 0:
              e, f, g, h = 3, 6, 3, 6 # 마상마상
            elif self.idx[1] == 1:
              e, f, g, h = 3, 6, 6, 3 # 마상상마
            elif self.idx[1] == 2:
              e, f, g, h = 6, 3, 6, 3 # 상마상마
            elif self.idx[1] == 3:
              e, f, g, h = 6, 3, 3, 6 # 상마마상
                          
            self.pieces =  [0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,
                            2,0,2,0,2,0,2,0,2,
                            0,4,0,0,0,0,0,4,0,
                            0,0,0,0,7,0,0,0,0,
                            1,a,b,5,0,5,c,d,1]
                
            self.enemy_pieces =  [0,0,0,0,0,0,0,0,0,
                                  0,0,0,0,0,0,0,0,0,
                                  0,0,0,0,0,0,0,0,0,
                                  0,0,0,0,0,0,0,0,0,
                                  0,0,0,0,0,0,0,0,0,
                                  0,0,0,0,0,0,0,0,0,
                                  2,0,2,0,2,0,2,0,2,
                                  0,4,0,0,0,0,0,4,0,
                                  0,0,0,0,7,0,0,0,0,
                                  1,e,f,5,0,5,g,h,1]
        # print(self.pieces)
        # print(self.enemy_pieces)

    # 패배 여부 판정
    def is_lose(self):
      if self.is_draw():
          if self.cal_piece_score() > self.cal_enemy_piece_score():
            return False
          else:
            return True
      else:
        for i in range(90):
            if self.pieces[i] == 7:  # 왕이 존재한다면
                return False
        return True
        # # 본인의 점수가 10점보다 적다면 게임 끝(패배)
        # if playerScore<10:
        #   return True

    # 200턴안에 안끝나면 종료
    def is_draw(self):
        return self.depth >= MAX_DEPTH  # 200수 안에 안끝난다면

    # 게임 종료 여부 판정
    def is_done(self):
        return self.is_lose()
    
    # 기물 점수 계산
    # 차(1):13점, 졸(2):2점, 마(3):5점, 포(4):7점, 사(5):3점, 상(6):3점, 왕(7):0점
    def cal_piece_score(self):
      temp_list = [0] * 8
      score = 0
      for i in range(90):
        temp_list[self.pieces[i]] += 1
      
      # 왕의 점수 계산 X
      for i in range(1, 7):
        if i == 1:
          score += (13*temp_list[i])
        elif i == 2:
          score += (2*temp_list[i])
        elif i == 3:
          score += (5*temp_list[i])
        elif i == 4:
          score += (7*temp_list[i])
        elif i == 5 or i == 6:
          score += (3*temp_list[i])

      if not self.is_first_player():
        return score + 1.5
      return score

    def cal_enemy_piece_score(self):
      temp_list = [0] * 8
      score = 0
      for i in range(90):
        temp_list[self.enemy_pieces[i]] += 1
      
      # 왕의 점수 계산 X
      for i in range(1, 7):
        if i == 1:
          score += (13*temp_list[i])
        elif i == 2:
          score += (2*temp_list[i])
        elif i == 3:
          score += (5*temp_list[i])
        elif i == 4:
          score += (7*temp_list[i])
        elif i == 5 or i == 6:
          score += (3*temp_list[i])
      
      if not self.is_first_player():
        return score
      return score + 1.5
    
    # 듀얼 네트워크 입력 2차원 배열 얻기
    def pieces_array(self):
      # 플레이어 별 듀얼 네트워크 입력 1차원 배열 얻기
      def pieces_array_of(pieces):
        table_list = []
        # 1: 차, 2: 졸, 3: 마, 4: 포, 5: 사, 6: 상, 7: 왕
        for j in range(1, 8):
          table = [0] * 90
          table_list.append(table)
          for i in range(90):
            if pieces[i] == j:
              table[i] = 1
        return table_list
        
      # 듀얼 네트워크 입력 2차원 배열 반환
      return [pieces_array_of(self.pieces), pieces_array_of(self.enemy_pieces)]

    def is_first_player(self):
      return self.depth % 2 == 0

      
state = State()
print(state.cal_piece_score())
print(state.cal_enemy_piece_score())