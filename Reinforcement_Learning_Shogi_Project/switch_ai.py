import tkinter as tk 
# from shogi_batch import GameUI
from shogi_batch_ai import GameUI
from PIL import Image, ImageTk

# tteasy 동작 방식

# 1. switch frame 에서 먼저 startPage 구동

# - idx 가 없으므로 new_Frame= StartPage(self) 실행
# - self._frmae 가 NOne값이므로
# - self._frame = new_frame 
# - self._frame.pack() 실행

# 2. StratPage 에서 선 수 or 후 수를 실행했을경우
# - lambda: master.switch_frame() 실행
# 여기서 master는 부모 클래스의 switch_frame() 
# 함수를 쓴다는 일종의 선언입니다. 
# - 

# 3. switch_frame 함수를 통하여 PageOne(선수의)클래스로
# 갔을 때 마상마상을 클릭했을 경우

# - Pageone 으로가면서(앞과정과 동일) 해당 idx를 가져간다.
# - if idx != None: 의 조건이 충족
# - idx는 if len(idx_list) == 1: 구문에 걸리므로
# - self.idx_list.append(idx) # 값이 리스트에 저장되고
# - idx_list = self.idx_list # idx_list에 저장이 되고
# - newframe = frame_class(idx = idx_list) 에 저장이 된다
# 그니까 결국 idx 값이 있을때(돌 배치를 했을경우) new_frame에 들어가는
# 값을 idx를 넣어주기 위해 만들어진 구문이다 이런뜻임

class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None # 지금 화면이 출력되는 것
        self.idx_list = [] # 인덱스  0번 선후결정,1번 초 돌 배치, 인덱스 2번 한 돌 배치
        self.switch_frame(StartPage)
        self.batch = None
        
        

    def switch_frame(self, frame_class, idx = None):
        idx_list = self.idx_list # idx 의 변수를 넣어주기 위해 선언

        if idx != None:  # idx가 있을 경우 (장기판을 띄우는 경우)
    
            if len(idx_list) == 2: # 두개이상 세팅이 되었을 경우(말배치가) + 선 수인지 후 수 인지
                self.idx_list.append(idx)
                idx_list = self.idx_list
                new_frame = GameUI(idx = idx_list) #GameUI 부분이 실행된다.
            else:
                self.idx_list.append(idx)
                new_frame = frame_class(self)
        else:            # idx가 없을 경우인데 (장기판을 띄우지 않는 모든 경우)
            self.idx_list = []
            new_frame = frame_class(self)
            

        if self._frame is not None: ## 기존에 켜진창이 있다면
            self._frame.destroy() ## 기존창 파괴
            
        self._frame = new_frame ## 새창을 self._frame에 넣어주고
        self._frame.pack() ## pack으로 실행
        

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="AI_shogi", font=('Helvetica', 32, "bold")).pack(side="top", fill="x", pady=5)
        tk.Button(self, text="선 수",font=('Helvetica', 18, "bold"),
                  command=lambda: master.switch_frame(PageOne, 0)).pack()
        tk.Button(self, text="후 수",font=('Helvetica', 18, "bold"),
                  command=lambda: master.switch_frame(PageOne, 1)).pack()

#(마상마상:0, 마상상마:1, 상마상마:2,상마마상,3)
class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self,bg='blue')
        tk.Label(self, text="선 수 말배치 결정", font=('Helvetica', 32, "bold")).pack(side="top", fill="x", pady=5)
        tk.Button(self, text="Go back to start page",
                  command=lambda: master.switch_frame(StartPage)).pack()
        tk.Button(self, text="마상마상",
                  command=lambda: master.switch_frame(PageTwo, 0)).pack()
        tk.Button(self, text="마상상마",
                  command=lambda: master.switch_frame(PageTwo, 1)).pack()
        tk.Button(self, text="상마상마",
                  command=lambda: master.switch_frame(PageTwo, 2)).pack()
        tk.Button(self, text="상마마상",
                  command=lambda: master.switch_frame(PageTwo, 3)).pack()

#(마상마상:0, 마상상마:1, 상마상마:2,상마마상,3)
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self,bg='red')
        tk.Label(self, text="후 수 말배치 결정", font=('Helvetica', 32, "bold")).pack(side="top", fill="x", pady=5)
        tk.Button(self, text="Go back to start page",
                  command=lambda: master.switch_frame(StartPage)).pack()
        tk.Button(self, text="마상마상",
                  command=lambda: master.switch_frame(PageOne, 0)).pack()
        tk.Button(self, text="마상상마",
                  command=lambda: master.switch_frame(PageOne, 1)).pack()
        tk.Button(self, text="상마상마",
                  command=lambda: master.switch_frame(PageOne, 2)).pack()
        tk.Button(self, text="상마마상",
                  command=lambda: master.switch_frame(PageOne, 3)).pack()

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()

