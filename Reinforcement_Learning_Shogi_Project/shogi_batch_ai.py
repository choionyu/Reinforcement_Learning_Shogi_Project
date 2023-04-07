# 장기판 규격 800,630
# 총프레임 860,690
# 여백 30
# 돌 이미지 크기 70x70
# (마상마상:0, 마상상마:1, 상마상마:2,상마마상,3)
# 선수 : 초, 후 수: 한


import tkinter as tk
from venv import create 
from PIL import Image, ImageTk
from game import State 
from pathlib import Path
from pv_mcts import pv_mcts_action
import numpy as np

from dual_network import ResNet18
import torch

TEMPERTURE = 1.0 # 볼츠만 온도 상수
# TEMPERTURE = [0.0, 1.0] # 볼츠만 온도 상수
# P = [0.7, 0.3]

# temperture = np.random.choice(TEMPERTURE, p=P)


class GameUI(tk.Frame): # 클래스는 보통 부모클래스가 뭔지를 넣는다.
    # __init__ 부분에서는 게임 상태와 PV MCTS로 행동 선택을 수행하는 함수와
    # 이미지 캔버스를 준비한다. 마지막으로 화면을 갱신하고, 초기화면을 표시한다.
    def __init__(self, idx, master=None, model = None):
        tk.Frame.__init__(self,master)
        # 타이틀 표시
        self.master.title("shogi_AI")
        print("idx = ",idx)

        # 선 수 후 수 판별을 위해
        self.idx = idx # idx[0] == 0 내가 선, idx[0] == 1 내가 후 

        # 게임 상태 생성
        self.state = State(idx = self.idx)
        self.select = -1 # 선택(-1: 없음, 0~89 매스)
        
        self.dict_index = self.create_index_dict()

        
        # 방향 정수 총 58
        self.dxy = [[0, -1], [0, -2], [0, -3], [0, -4], [0, -5], [0, -6], [0, -7], [0, -8], [0, -9], # 0-8  차,졸,포,사,왕
                    [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0],                  # 9-16
                    [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9],          # 17-25
                    [-1, 0], [-2, 0], [-3, 0], [-4, 0], [-5, 0], [-6, 0], [-7, 0], [-8, 0],          # 26-33
                    [1, -2], [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1], [-1, -2],          # 34-41  마
                    [2, -3], [3, -2], [3, 2], [2, 3], [-2, 3], [-3, 2], [-3, -2], [-2, -3],          # 42-49  상
                    [1, -1], [2, -2], [1, 1], [2, 2], [-1, 1], [-2, 2], [-1, -1], [-2, -2]]          # 50-57 궁성안의 대각선 움직임          # 42-49  상
        
        # PV MCTS를 활용한 행동 선택을 따르는 함수 생성
        model1 = ResNet18()
        model1.load_state_dict(torch.load('./model/before.h5', map_location=torch.device('cpu')))
        self.next_action1 = pv_mcts_action(model1, TEMPERTURE)

        model2 = ResNet18()
        model2.load_state_dict(torch.load('./model/after.h5', map_location=torch.device('cpu')))
        self.next_action2 = pv_mcts_action(model2, TEMPERTURE)

        # 이미지 로드
        self.win_lose_images = [] # 승 패 이미지
        self.images = [(None,None,None,None)]
        for i in range(1,8):
            image_cho = Image.open("cho_piece{}.png".format(i)) # 선 돌(내 돌) 
            image_han = Image.open("han_piece{}.png".format(i)) # 후 돌(적 돌)
            self.images.append((
                ImageTk.PhotoImage(image_cho),
                ImageTk.PhotoImage(image_han),
                ImageTk.PhotoImage(image_cho.rotate(180)), # 추 후 resize 예정
                ImageTk.PhotoImage(image_han.rotate(180))  # 추 후 resize 예정
            ))
        wimage = Image.open("win.png") 
        limage = Image.open("lose.png") 
        self.win_lose_images.append(ImageTk.PhotoImage(wimage.resize((250,250)))) # 승리 이미지 resize
        self.win_lose_images.append(ImageTk.PhotoImage(limage.resize((250,250)))) # 패배 이미지 resize
        
        #캔버스 생성
        self.c = tk.Canvas(self, width=860,height=690,highlightthickness = 0)
        

        if self.idx[0] == 0:  # 선수선택
            self.c.bind("<Button-1>",self.turn_of_human) # 클릭 판정
        else:  # 후수선택
            self.turn_of_ai1()
        self.c.pack()

        # # 추가
        # # 그림 갱신
        # if self.state.is_done():
        #     if self.state.is_lose() == True:
        #         self.on_draw(win_lose = 0) # 내 돌 승리시
        #     else:
        #         self.on_draw(win_lose = 1) # 내 돌 패배시
        # else:
        #     self.on_draw()  # 끝나지 않았을때는 그냥 그린다.

        # 그림 갱신
        self.on_draw() 

        
        self.idx = idx
        # self.state = State(idx = self.idx)
    
    # def turn_of_human에 대한 설명글
    # 1. 게임이 종료되는 경우 게임을 초기상태로 돌린다
    # 2. 선 수가 아닌 경우 사람은 조작할 수 없다.
    # 3. 클릭 위치로부터 행동(매스 번호)으로 변환 한다.
    # 4. 클릭 위치의 XY좌표로부터 행동으로 변환하고, 그 행동이 둘 수 잇는 수가 아닌 경우에는
    #    처리하지 않도록 한다.
    # 5. 둘 수 있는 수의 경우에는 state.next()로 다음 상태를 취득하고, 화면을 갱신한다.
    # 6. 직접 turn_of_ai()를 호출하면 AI 턴이 종료될 떄까지 사람의 턴으로 화면 갱신이 적용 되지
    #    않기 때문에 master.after()로 1밀리초 슬립을 한 뒤 호출한다.
    # 7.  말 선택과 이동 위치로부터 변환한 행동이 둘 수 있는 수가 아닌 경우 말 선택을 해제한다.
    # 8. 둘 수 있는 수인 경우 다음상태를 취득하고,화면을 갱신한다.
    # 9. AI의 턴으로 바꾼다.

    def who_is_first(self):
        if self.idx[0] == 0: # 내가 선공이면
            return True
        if self.idx[0] == 1: # 내가 후공이면
            return False
    
    # 클릭시 호출
    def turn_of_human(self, event):

        # 게임 종료 시
        if self.state.is_done():
            self.state = State() ## 돌 값을 초기화 해준다.
            self.on_draw() ## 화면을 초기화 한다.
            return
        
        p = self.coord_to_index(event.x, event.y) # 첫번째는 시작위치 인덱스 값 # 두 번째 클릭시 도착위치의 좌표
        # print('p = ', p)
        
        if (0 <= event.x <= 860) and (0 <= event.y <=690): # 장기판의 범위 안에 있으면
            if p is not None:
                select = p # 누른 곳의 좌표를 select 변수에 넣어준다.
        
        else: # 장기판의 범위가 넘어간 곳을 누르면 
            return # 그냥 패스

        # 말 선택 (처음 돌을 클릭한 좌표 인덱스값이 들어간다.)
        if self.select < 0: # 처음에는 -1이므로 여기에 걸림
            self.select = select # 누른곳의 좌표가 self.select에 들어간다.
            self.on_draw() # on_draw를 실행
            return
        
        # 말 선택과 이동을 행동으로 변환
        action = -1 # 왜 -1을 주지?
        if select < 90: # 이동 위치가 장기판 안에 있는 경우 (select의 범위는 89까지다.)
            if self.select < 90:  # 시작 위치가 장기판 안에 있는 경우
                action = self.state.position_to_action(p,self.position_to_direction(self.select,p))

            if not (action in self.state.legal_actions()): # 둘 수 있는수가 아니라면
                self.select = -1 # -1로 초기화 해야 시작 위치를 받을 수 있다.
                self.on_draw() # 그냥 무시한다.
                return

            self.state = self.state.next(action) # 다음 상태를 얻은 후
            self.select = -1 # 초기화 해주고
            

            if self.state.is_done():
                self.on_draw(win_lose = 0)
            else:
                self.on_draw()

            # # AI의 턴
            self.master.after(1, self.turn_of_ai)

    def turn_of_ai(self):
        if self.state.is_done(): # 게임 종료시 초기상태로 돌린다.
            return
        # 행동얻기
        action = self.next_action(self.state)
        # 다음 상태 얻기
        self.state = self.state.next(action)

        # 추가
        if self.state.is_done():
            self.on_draw(win_lose = 1)
        else:
            self.on_draw()

            if self.idx[0] == 1:
                self.master.after(1, self.c.bind("<Button-1>",self.turn_of_human))

    def turn_of_ai1(self):
        if self.state.is_done(): # 게임 종료시 초기상태로 돌린다.
            return
        # 행동얻기
        action = self.next_action1(self.state)
        # 다음 상태 얻기
        self.state = self.state.next(action)

        # 추가
        if self.state.is_done():
            self.on_draw(win_lose = 1)
        else:
            self.on_draw()
            self.master.after(1, self.turn_of_ai2)
    
    def turn_of_ai2(self):
        if self.state.is_done(): # 게임 종료시 초기상태로 돌린다.
            return
        # 행동얻기
        action = self.next_action2(self.state)
        # 다음 상태 얻기
        self.state = self.state.next(action)

        # 추가
        if self.state.is_done():
            self.on_draw(win_lose = 0)
        else:
            self.on_draw()
            self.master.after(1, self.turn_of_ai1)
    



    # 말의 이동 도착 위치를 말의 이동 방향으로 전환
    # 쉽게 말하자면 시작 위치와 도착 위치가 선택 되었을 경우 해당하는 방향 정수를 리턴한다.
    # 없으면 0 을 리턴
    def position_to_direction(self,position_src,position_dst):
        dx = position_dst % 9 - position_src % 9 # (이동 후 x좌표 - 이동 전 x좌표)
        dy = int(position_dst / 9) - int(position_src / 9) # (이동 후 y좌표 - 이동 전 y좌표)
        for i in range(58): # 58개의 방향정수 중
            if self.dxy[i][0] == dx and self.dxy[i][1] == dy: return i
        return 0
            # 만약 방향 정수 x값이 연산된 값이 같고 y방향 정수가 연산된 y값과 같다면 i를 리턴 



    def on_draw(self, win_lose = None): # 그림 갱신 
        # 매스 기본 프레임
        self.c.delete('all')
        self.c.create_rectangle(0, 0, 860, 690, width=0.0, fill='#EDAA56') # 외각 사각형
        self.c.create_rectangle(30, 30, 830, 660, outline='black',width=1.0, fill='#EDAA56') # 장기판 사각형
        
        #가로줄 그리기
        for i in range(1,8): 
            self.c.create_line(i*100+30,0+30,i*100+30,630+30,fill="#000000")
        #세로줄 그리기
        for i in range(9):
            self.c.create_line(0+30,i*70+30,800+30,i*70+30,fill="#000000")
        # 왕 x자 그리기(상대편 꺼)
        self.c.create_line(330,30,530,170,width=1.0,fill="#000000")
        self.c.create_line(330,170,530,30,width=1.0,fill="#000000")
        # 왕 x자 그리기(내 꺼)
        self.c.create_line(330,660,530,520,width=1.0,fill="#000000")
        self.c.create_line(330,520,530,660,width=1.0,fill="#000000")
        # 점 그리기 (상대꺼)
        self.c.create_oval(30,240,30,240,width=6.0,fill="#000000")
        self.c.create_oval(130,170,130,170,width=6.0,fill="#000000")
        self.c.create_oval(230,240,230,240,width=6.0,fill="#000000")
        self.c.create_oval(430,240,430,240,width=6.0,fill="#000000")
        self.c.create_oval(630,240,630,240,width=6.0,fill="#000000")
        self.c.create_oval(730,170,730,170,width=6.0,fill="#000000")
        self.c.create_oval(830,240,830,240,width=6.0,fill="#000000")
        # 점 그리기 (내꺼)
        self.c.create_oval(30,450,30,450,width=6.0,fill="#000000")
        self.c.create_oval(130,520,130,520,width=6.0,fill="#000000")
        self.c.create_oval(230,450,230,450,width=6.0,fill="#000000")
        self.c.create_oval(430,450,430,450,width=6.0,fill="#000000")
        self.c.create_oval(630,450,630,450,width=6.0,fill="#000000")
        self.c.create_oval(730,520,730,520,width=6.0,fill="#000000")
        self.c.create_oval(830,450,830,450,width=6.0,fill="#000000")

        # 돌 그리기
        for p in range(90): # 좌표 위치 인덱스를 p에 넣어준다. (p0가 무조건 내꺼)

            if self.idx[0] == 0:
                if self.state.is_first_player():
                    p0,p1 = (p,89-p)   # p0는 내 돌 배치, p1는 상대 돌 배치
                    who0, who1 = 0, 1
                else:
                    p0,p1 = (89-p,p)
                    who0, who1 = 1, 0
            else:
                if self.state.is_first_player():
                    p0,p1 = (89-p,p)   # p0는 내 돌 배치, p1는 상대 돌 배치
                    who0, who1 = 1, 0
                else:
                    p0,p1 = (p,89-p)
                    who0, who1 = 0, 1
            # p0,p1 = (p,89-p)
            
            if self.state.pieces[p0] != 0: # 해당 인덱스에 돌이 있다면 (내 돌 기준)
                self.draw_piece(p,self.who_is_first(),self.state.pieces[p0],who0)
            if self.state.enemy_pieces[p1] != 0: # 해당 인덱스에 돌이 있다면 (적 돌 기준)
                self.draw_piece(p,self.who_is_first(),self.state.enemy_pieces[p1],who1)

        # 커서 그리기
        if 0 <= self.select < 90:
            self.draw_cursor(int(self.select % 9) * 100 + 2, int(self.select / 9) * 70 + 2, self.select)

        # 승리 화면, 패배 화면 그리기
        if win_lose == 0: # 승리시
            self.c.create_image(430,345,image = self.win_lose_images[0])
        if win_lose == 1: # 패배시
            self.c.create_image(430,345,image = self.win_lose_images[1])
        


    def draw_piece(self, index, first_player,piece_type,who): # index: 매스번호, first_player:선수여부
         
        x = (index % 9) * 100 + 30 # + 30은 여분만큼 더해줘야 하기에
        y = int(index / 9) * 70  + 30
        if first_player: # 내가 선일때 나:0 상대: 3 
            my_batch = 0
            enemy_batch = 3

        else: # 상대가 선일때 나:1 상대: 2
            my_batch = 1
            enemy_batch = 2
        
        if who == 0:
            self.c.create_image(x,y, image = self.images[piece_type][my_batch]) 
        if who == 1:
            self.c.create_image(x,y, image = self.images[piece_type][enemy_batch])
  
    
    # 커서 그리기
    # 인 수 x,y는 캔버스의 xy좌표 , "size"는 커서의 폭과 높이로 픽셀 단위를 지정한다.
    def draw_cursor(self,x,y,index):
        self.c.create_rectangle(x, y, x+56, y+56, width=4.0,outline= "red") # 외각 사각형
        for action in self.state.legal_actions(index):
             dst,direc = self.state.action_to_position(action) # dst = 도착 위치 인덱스 direction: 방향 
             legal_x, legal_y = int(dst % 9) * 100 + 30, int(dst / 9) * 70 + 30
             self.c.create_oval(legal_x,legal_y,legal_x,legal_y,width=6.0,outline = "red",fill="red")
    
    def create_index_dict(self):
        dict_index = {}
        x1, x2, y1, y2 = 0, 0, 0, 0

        for i in range(90):
            x1 = 2 + ((i % 9)*100)
            y1 = 2 + ((i // 9)*70)
            x2 = x1 + 56
            y2 = y1 + 56

            dict_index[i] = [[x1, y1], [x2, y2]]
        return dict_index


    def coord_to_index(self, event_x, event_y):
        for i in range(90):
            if self.dict_index[i][0][0] <= event_x <= self.dict_index[i][1][0] and \
                self.dict_index[i][0][1] <= event_y <= self.dict_index[i][1][1]:
                return i
        
        return
            
        
    
    # # 한 돌 (1:한차,2:한졸,3:한마,4:한포,5:한사,6:한상,7:한왕)
    # def enemy_batch(self):
    #     if self.idx[0] == 0:
    #         images = self.han_images
    #     elif self.idx[0] == 1:
    #         images = self.cho_images
        
    #     self.c.create_image(30,30,image=images[1]) # 한 차
    #     self.c.create_image(130,30,image=images[3]) # 한 마
    #     self.c.create_image(230,30,image=images[6]) # 한 상
    #     self.c.create_image(330,30,image=images[5]) # 한 사
    #     self.c.create_image(530,30,image=images[5]) # 한 사
    #     self.c.create_image(630,30,image=images[3])# 한 상
    #     self.c.create_image(730,30,image=images[6])# 한 마
    #     self.c.create_image(830,30,image=images[1])# 한 차
    #     self.c.create_image(430,100,image=images[7]) # 한 왕
    #     self.c.create_image(130,170,image=images[4]) # 한 포
    #     self.c.create_image(730,170,image=images[4]) # 한 포

    #     # 한 졸 그리기
    #     for i in range(5):
    #         self.c.create_image(i*200+30,240,image=images[2])
        
  

        
    # def my_batch(self):
    #      # 초 돌 (1:초차,2:초졸,3:초마,4:초포,5:초사,6:초상,7:초왕)
    #      # 한 돌 (1:한차,2:한졸,3:한마,4:한포,5:한사,6:한상,7:한왕)
    #     if self.idx[0] == 0:
    #         images = self.cho_images
    #     elif self.idx[0] == 1:
    #         images = self.han_images

    #     self.c.create_image(30,660,image=images[1]) # 초 차
    #     self.c.create_image(130,660,image=images[3]) # 초 마
    #     self.c.create_image(230,660,image=images[6]) # 초 상
    #     self.c.create_image(330,660,image=images[5]) # 초 사
    #     self.c.create_image(530,660,image=images[5]) # 초 사
    #     self.c.create_image(630,660,image=images[3]) # 초 마
    #     self.c.create_image(730,660,image=images[6]) # 초 상
    #     self.c.create_image(830,660,image=images[1]) # 초 차
    #     self.c.create_image(430,590,image=images[7]) # 초 왕
    #     self.c.create_image(130,520,image=images[4]) # 초 포
    #     self.c.create_image(730,520,image=images[4]) # 초 포

    #     for i in range(5):
    #         self.c.create_image(i*200+30,450,image=images[2]) # 초 졸


    

        
        
# f = GameUI(idx=1)
# f.pack()
# f.mainloop()

