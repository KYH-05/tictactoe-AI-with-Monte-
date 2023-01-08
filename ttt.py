#--------------------------------------------------------------------------
#ai_win이 0인 이유 찾기(사람이 먼저 선택하고 ai가 simul할때)
#승률이 높아도 선택을 안함(방문 횟수가 이상한 곳에서 커짐)
#--------------------------------------------------------------------------
import pygame
import sys
import random
from pygame.locals import *
import numpy as np
#import pyautogui
import math
import copy
from numpy import log as ln
import time
#--------------------------------------------------------------------------
pygame.init()
screenWidth=640
screenHeight=640
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('tic-tac-toe AI')
clock = pygame.time.Clock()
pygame.key.set_repeat(1, 1)
BLACK=(0,0,0)
WHITE=(225,225,225)
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
#--------------------------------------------------------------------------
#변수설정
tictactoe_list=[[1,2,3],[4,5,6],[7,8,9]]
first_or_second=random.choice(['ai','human'])
select_location1=-1
select_location2=-1
myFont = pygame.font.SysFont( "arial", 15, True, False)
node_list=[]
n=0#부모 노드의 방문 횟수
breaksignal=False#맨 밑에 ai의 선택 과정 반복 중지
roop=True# simulation 누군가의 승리가 일찍이 결정나면 더이상 sim하지 말고 종류
early_human_win= []
early_ai_win= []
end_signal=False
#--------------------------------------------------------------------------
stick1s=[]
stick1_w=10
stick1_h=640
for i in range(0,4):
  stick1=pygame.Rect((stick1_w+(screenWidth-stick1_w*4)/3)*i,0,stick1_w,stick1_h)
  stick1s.append(stick1)
#--------------------------------------------------------------------------
stick2s=[]
stick2_w=640
stick2_h=10
for i in range(0,4):
  stick2=pygame.Rect(0,(stick2_h+(screenHeight-stick2_h*4)/3)*i,stick2_w,stick2_h)
  stick2s.append(stick2)
#--------------------------------------------------------------------------
def drawstick():
  for stick1 in stick1s:
    pygame.draw.rect(screen,(0,0,0),stick1)
  for stick2 in stick2s:
    pygame.draw.rect(screen,(0,0,0),stick2)
#--------------------------------------------------------------------------
def draw():
  screen.fill(WHITE)
  #drawstick()
#--------------------------------------------------------------------------
def drawOX():
  global tictactoe1
  sysfont = pygame.font.SysFont(None, 72)
  for i in range(0,3):
    for k in range(0,3):
      if tictactoe_list[i][k]=="human":
        text = sysfont.render("O", True,(0,0,0))
        screen.blit(text, (((k+1)*90+120*k,(i+1)*90+120*i)))#추후 글자크기까지 고려해서 일반화
      elif tictactoe_list[i][k]=="ai":
        text = sysfont.render("X", True,(0,0,0))
        screen.blit(text, (((k+1)*90+120*k,(i+1)*90+120*i)))
#--------------------------------------------------------------------------
#node_list에 현 상황,방문횟수,ucb1값 실시간으로 갱신/몇수 앞까지 내다보는게 좋을까
#tictactoe_list=[["human","ai","ai"],["human",5,"ai"],["ai",8,"human"]]
def remain1():
  global node_list,tictactoe_list,remain
  list1=[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
  list2=[]
  for i in range(0,3):
    for k in range(0,3):
      if tictactoe_list[i][k]=="human":
        list2.append([i,k])
      if tictactoe_list[i][k]=="ai":
        list2.append([i,k])
  remain = [x for x in list1 if x not in list2]
#--------------------------------------------------------------------------
def nodelist(): #UCT값 추가
  global remain,node_list,floor,tictactoe_list,nj
  floor=9-len(remain)
  ts=[]
  for i in range(0,2*len(remain)+1):
    ts.append(copy.deepcopy(tictactoe_list))
  node_list=[[],[],[]]
  for i in range(0,1):
    node_list[0].append(ts[i])
  #print(node_list)
  for i in range(1,len(remain)+1):
    node_list[1].append(ts[i])
  for i in range(len(remain)+1,2*len(remain)+1):
    node_list[2].append(ts[i])
  for i in range(0,len(remain)):
    node_list[1][i][remain[i][0]][remain[i][1]]="ai"
  for i in range(0,len(remain)):
    node_list[2][i][remain[i][0]][remain[i][1]]="human"
  #print(node_list)
  who_win1()
#--------------------------------------------------------------------------
def UCB1list1():
  global UCB1list,nj,human_win,ai_win,tie,xj,early_ai_win,early_human_win
  UCB1list=[]
  for i in range(0,len(remain)):
    UCB1list.append(random.random())
  nj=[]#leaf node의 방문 횟수
  for i in range(0,len(remain)):
    nj.append((1/10)**5)
  human_win=[]
  for i in range(0,len(remain)):
    human_win.append(0)
  ai_win=[]
  for i in range(0,len(remain)):
    ai_win.append(0)
  tie=[]
  for i in range(0,len(remain)):
    tie.append(0)
  xj = []
  for i in range(0, len(remain)):
    xj.append(0)
  early_human_win=[]
  for i in range(0, len(remain)):
    early_human_win.append(False)
  early_ai_win=[]
  for i in range(0, len(remain)):
    early_ai_win.append(False)
#--------------------------------------------------------------------------
def selection():
  global node_list,tictactoe_list,node_index,UCB1list
  #uct 리스트 내에서 가장큰 uct값 선택,선택횟수 업데이트
  if len(UCB1list)!=0:
    node_index=UCB1list.index(max(UCB1list))
#--------------------------------------------------------------------------
#def expansion():#2차원 리스트에서 중복되지 않게 선택
  #1
#--------------------------------------------------------------------------
def simulation():#random하게,중복되지 않게 선택
  global node_index,node_list,remain2,q,n,nj,remain,real_node_list,roop
  #remain part
  real_node_list=copy.deepcopy(node_list[1])
  #print(node_list[1][node_index])
  n = n + 1
  nj[node_index] = nj[node_index] + 1
  for V in range(0,len(remain)-1):
    list1=[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
    list2=[]
    for i in range(0,3):
      for k in range(0,3):
        if node_list[1][node_index][i][k]=="human":
          list2.append([i,k])
        if node_list[1][node_index][i][k]=="ai":
          list2.append([i,k])
    remain2 = [x for x in list1 if x not in list2]
    #print(remain2)
    #leaf_node part
    a=len(remain2)
    b=random.randint(0,a-1)
    if V==0 or V==2 or V==4 or V==6 or V==8:
      node_list[1][node_index][remain2[b][0]][remain2[b][1]]="human" #여기서 턴에 따라서 선택해야 함
    if V==1 or V==3 or V==5 or V==7 or V==8:
      node_list[1][node_index][remain2[b][0]][remain2[b][1]]="ai"#여기서 턴에 따라서 선택해야 함
    who_win2()
    if roop==False:#누군가의 승리가 결정나면 더이상 sim하지 말고 종류
      break
#--------------------------------------------------------------------------
def backpropagation():#node_list에 ucb1 저장,다른 리스트도 생성
  #who_win의 결과값
  global UCB1list,n,nj,node_index,human_win,ai_win,tie,xj,early_human_win,early_ai_win
  #print()
  #print(node_list[1][node_index])
  #print(human_win,ai_win,tie)
  #print()
  for i in range(0,len(remain)):
    if ai_win[i]+human_win[i]+tie[i]==0:
      xj[i]=0
    else:
      xj[i]=(ai_win[i]+tie[i]*0.8)/(ai_win[i]+human_win[i]+tie[i])#승리 조건에 tie 추가#####################################################
    cp=10#####################################################################
    if len(remain)!=1:
      UCB1list[i]=xj[i]+cp*((2*ln(n)/nj[i])**(1/2))
    else:UCB1list[i]=1
  #print(early_ai_win,early_human_win)
  #print(early_human_win,early_ai_win)
  for i in range(0,len(remain)):
    if early_ai_win[i]==True:#무조건 공격->승리
      xj[i]=2
    if early_human_win[i]==True:#무조건 수비->패배 면함
      xj[i]=1



  #UCB1list[node_index]=xj+cp*((2*ln(n)/nj[node_index])**(1/2))
#--------------------------------------------------------------------------
def ai_select_location():
  global n,node_list, tictactoe_list,breaksignal,remain,ai_win,human_win,tie,nj
  if len(remain)==1:
    #print(node_list[1])
    tictactoe_list=node_list[1][0]
    breaksignal=True
  passsing=[1 for i in range(len(nj))]
  for i in range(len(nj)):
    if nj[i]>=1000:
      passsing[i]=0
  if sum(passsing)==0:
    tictactoe_list=node_list[1][xj.index(max(xj))]
    print(ai_win)
    print(human_win)
    print(tie)
    print(xj)
    print(nj)
    print(UCB1list)
    #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    breaksignal=True
  #각 child 노드에서 선택 횟수가 일정 횟수 초과하였을떄 ai_select_location(), 변수 초기화
#--------------------------------------------------------------------------
def human_select_location():#다른 위치 선택할떄까지 반복, 마우스로 선택, ai선택중 선택하지 못하게
  global tictactoe_list,select_location1,select_location2
  select_location1=-1
  select_location2=-1
  position = 0
  while position == 0:
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        position = pygame.mouse.get_pos()
        #print(position)
  x=(position[0])
  y=(position[1])
  if 10<=x<=210:
    select_location2=0
  elif 220<=x<=420:
    select_location2=1
  elif 430<=x<=630:
    select_location2=2
  if 10 <= y <= 210:
    select_location1 = 0
  elif 220 <= y <= 420:
    select_location1 = 1
  elif 430 <= y <= 630:
    select_location1 = 2
  #print(select_location1,select_location2)
  tictactoe_list[select_location1][select_location2] = "human"
#-------------------------------------------------------------------------------------------------------------------------------
def  who_win():#실제 게임에서
  global tictactoe_list,end_signal
  #가로----------------------------------------------------------------------
  if tictactoe_list[0][0]==tictactoe_list[0][1]==tictactoe_list[0][2]:
    if tictactoe_list[0][0]=="human":
      print("human win")
      end_signal=True
    elif tictactoe_list[0][0]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[1][0]==tictactoe_list[1][1]==tictactoe_list[1][2]:
    if tictactoe_list[1][0]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[1][0]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[2][0]==tictactoe_list[2][1]==tictactoe_list[2][2]:
    if tictactoe_list[2][0]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[2][0]=="ai":
      print("ai win")
      end_signal = True
#세로---------------------------
  elif tictactoe_list[0][0]==tictactoe_list[1][0]==tictactoe_list[2][0]:
    if tictactoe_list[0][0]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[0][0]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[0][1]==tictactoe_list[1][1]==tictactoe_list[2][1]:
    if tictactoe_list[0][1]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[0][1]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[0][2]==tictactoe_list[1][2]==tictactoe_list[2][2]:
    if tictactoe_list[0][2]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[0][2]=="ai":
      print("ai win")
      end_signal = True
  #대각선---------------------------
  elif tictactoe_list[0][0]==tictactoe_list[1][1]==tictactoe_list[2][2]:
    if tictactoe_list[0][0]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[0][0]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[0][2]==tictactoe_list[1][1]==tictactoe_list[2][0]:
    if tictactoe_list[0][2]=="human":
      print("human win")
      end_signal = True
    elif tictactoe_list[0][2]=="ai":
      print("ai win")
      end_signal = True
  elif tictactoe_list[0][0]!=1 and tictactoe_list[0][1]!=2 and tictactoe_list[0][2]!=3 and tictactoe_list[1][0]!=4 and tictactoe_list[1][1]!=5 and tictactoe_list[1][2]!=6 and tictactoe_list[2][0]!=7 and tictactoe_list[2][1]!=8 and tictactoe_list[2][2]!=9:
    print("draw")
    end_signal = True
#------------------------------------------------------------------------------------------------------------------------------------------------------
def who_win1():
  global node_list,early_ai_win,early_human_win
  for k in range(1,3):
    for i in range(0,len(remain)):
     # 가로-------------------------------------------------------------------------------
      if node_list[k][i][0][0] == node_list[k][i][0][1] == node_list[k][i][0][2]:
        if node_list[k][i][0][0] == "human":
          early_human_win[i]=True
        elif node_list[k][i][0][0] == "ai":
          early_ai_win[i] = True
      elif node_list[k][i][1][0] == node_list[k][i][1][1] == node_list[k][i][1][2]:
        if node_list[k][i][1][0] == "human":
          early_human_win[i] = True
        elif node_list[k][i][1][0] == "ai":
          early_ai_win[i]= True
      elif node_list[k][i][2][0] == node_list[k][i][2][1] == node_list[k][i][2][2]:
        #print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        if node_list[k][i][2][0] == "human":
          early_human_win[i] = True
         # if i==3:
            #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        elif node_list[k][i][2][0] == "ai":
          early_ai_win[i]= True
      # 세로---------------------------
      elif node_list[k][i][0][0] == node_list[k][i][1][0] == node_list[k][i][2][0]:
        if node_list[k][i][0][0] == "human":
          early_human_win[i] = True
        elif node_list[k][i][0][0] == "ai":
          early_ai_win[i]= True
      elif node_list[k][i][0][1] == node_list[k][i][1][1] == node_list[k][i][2][1]:
        if node_list[k][i][0][1] == "human":
          early_human_win[i] = True
        elif node_list[k][i][0][1] == "ai":
          early_ai_win[i]= True
      elif node_list[k][i][0][2] == node_list[k][i][1][2] == node_list[k][i][2][2]:
        if node_list[k][i][0][2] == "human":
          early_human_win[i] = True
        elif node_list[k][i][0][2] == "ai":
          early_ai_win[i]= True
      # 대각선---------------------------
      elif node_list[k][i][0][0] == node_list[k][i][1][1] == node_list[k][i][2][2]:
        if node_list[k][i][0][0] == "human":
          early_human_win[i] = True
        elif node_list[k][i][0][0] == "ai":
          early_ai_win[i]= True
      elif node_list[k][i][0][2] == node_list[1][i][1][1] == node_list[1][i][2][0]:
        if node_list[k][i][0][2] == "human":
          early_human_win[i] = True
        elif node_list[k][i][0][2] == "ai":
          early_ai_win[i]= True


  # ---------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------
def  who_win2():#-remain2에서 승리 확인
  global node_list, human_win, ai_win,node_index,roop
#가로-------------------------------------------------------------------------------
  if node_list[1][node_index][0][0]==node_list[1][node_index][0][1]==node_list[1][node_index][0][2]:
    roop = False
    if node_list[1][node_index][0][0]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][0]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][1][0]==node_list[1][node_index][1][1]==node_list[1][node_index][1][2]:
    roop = False
    if node_list[1][node_index][1][0]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][1][0]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][2][0]==node_list[1][node_index][2][1]==node_list[1][node_index][2][2]:
    roop = False
    if node_list[1][node_index][2][0]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][2][0]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
#세로---------------------------
  elif node_list[1][node_index][0][0]==node_list[1][node_index][1][0]==node_list[1][node_index][2][0]:
    roop = False
    if node_list[1][node_index][0][0]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][0]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][0][1]==node_list[1][node_index][1][1]==node_list[1][node_index][2][1]:
    roop = False
    if node_list[1][node_index][0][1]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][1]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][0][2]==node_list[1][node_index][1][2]==node_list[1][node_index][2][2]:
    roop = False
    if node_list[1][node_index][0][2]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][2]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
#대각선---------------------------
  elif node_list[1][node_index][0][0]==node_list[1][node_index][1][1]==node_list[1][node_index][2][2]:
    roop = False
    if node_list[1][node_index][0][0]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][0]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][0][2]==node_list[1][node_index][1][1]==node_list[1][node_index][2][0]:
    roop = False
    if node_list[1][node_index][0][2]=="human":
      human_win[node_index]=human_win[node_index]+1
    elif node_list[1][node_index][0][2]=="ai":
      ai_win[node_index]=ai_win[node_index]+1
  elif node_list[1][node_index][0][0]!=1 and node_list[1][node_index][0][1]!=2 and node_list[1][node_index][0][2]!=3 and node_list[1][node_index][1][0]!=4 and node_list[1][node_index][1][1]!=5 and node_list[1][node_index][1][2]!=6 and node_list[1][node_index][2][0]!=7 and node_list[1][node_index][2][1]!=8 and node_list[1][node_index][2][2]!=0:
    roop = False
    tie[node_index]=tie[node_index]+1
  else:
    roop=True
  #print()
  #print(node_list[1][node_index])
  #print(human_win,ai_win,tie)
  #print()

#---------------------------------------------------------------------------------
def start_and_reset_game():
  global tictactoe_list
  tictactoe_list=[[1,2,3],[4,5,6],[7,8,9]]
#--------------------------------------------------------------------------
#초기화
start_and_reset_game()
draw()
drawstick()
pygame.display.update()
#--------------------------------------------------------------------------
#반복
while True:
#--------------------------------------------------------------------------
#종료
  for event in pygame.event.get():
      if event.type==pygame.QUIT:
          pygame.quit()
          sys.exit()
      elif event.type == pygame.MOUSEBUTTONDOWN:
        print(pygame.mouse.get_pos())
#--------------------------------------p------------------------------------
  if first_or_second=="ai": #이것도 함수로
    if end_signal==True:
      time.sleep(10000)
    print("ai turn")
    remain1()
    UCB1list1()
    nodelist()
    while True:
      selection()
      simulation()
      backpropagation()
      node_list[1] = copy.deepcopy(real_node_list)
      roop=True
      ai_select_location()
      if breaksignal==True:
        break
    breaksignal = False
    n=0
    first_or_second="human"
    print("-"*50)
  elif first_or_second=="human":
    if end_signal==True:
      time.sleep(10000)
    print("your turn")
    human_select_location()
    first_or_second="ai"
    print("-"*50)
#--------------------------------------------------------------------------
  drawOX()
  who_win()
#--------------------------------------------------------------------------
  pygame.display.update()
  clock.tick(60)
