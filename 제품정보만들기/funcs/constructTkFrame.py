from all_libraries import *
import math,random
def mouseOnframe(event,framedict:dict):

        framedict[event.widget._name]["obj"].config(highlightthickness=5,highlightbackground="black")

def mouseOffframe(event,framedict:dict):

    framedict[event.widget._name]["obj"].config(highlightthickness=0)
def frameConstructor(root_frame_name:str,numOfframe:int,windowsize:tuple):
    """
    frame은 .place()로 배치된 것이 precondition.\n
    root_frame_name : frameDatabase의 key 값. frameDatabase의 자세한 것은 설명서 참고\n
    frameStructure : .Frame 객체의 inheritance를 저장한 데이터. \n\n
    return dict , {"obj":tk.Tk(),"frame0":{"obj":tk.frame,"widgets":{}},"frame1":{"obj":tk.frame,"widgets":{}} , ...}\n
    \t- 제일처음 나오는 "obj"가 main roop임. 이걸로 update/mainloop 돌리면 됨
    """
    if re.search("['~./\\\!@#$%^&*,\(\)\[\]]",root_frame_name):
        return "오직 특수문자 '-' 만 사용가능합니다."
    
    tkframeData={"obj":tk.Tk()}
    tkframeData["obj"].geometry("{}x{}".format(windowsize[0],windowsize[1]))
    # tkframeData["obj"].bind("<KeyPress>",self.keypress) # 이건 제목생성기에서 사진 이동시킬때 필요했던 녀석임.

    framewidth,frameheight=int(windowsize[0]),int(windowsize[1])
    # 배치 알고리즘 , 우선 sqrt씌움, 자연수부분만 가져옴. 만약 3.001 값이나와도 자연수부분 +1 해서 4를하고. 이렇게해서 가로 4 세로 4의 Frame을 만들 것임
    if math.sqrt(numOfframe)>float(math.trunc(math.sqrt(numOfframe)))+.000001: # trunc는 실수에서 정수부분만 가져오는 함수. .000001에는 아무 의미 없음, 그냥 2.0 > 2.000001 인 경우를 분류하려고 만 듦
        numberofFramebox=math.trunc(math.sqrt(numOfframe))+1 # root2 씌워서 해당 값들의 1/2배 를 가져오고 거기 정수에서 만약 0.6 나오면 0을가져오고 +1해서 가로/세로 1개의 프레임을 만드는 것임 만약 2.6이면 3이 되서 3x3 Frame 만드는 거임
        # e.g ) numofframe이 6이다. 6의 루트값은 2.4보다 크다, 2.000001보다 크다는 건 가로세로 2개를 하면 6개를 못 채운다는 것. 즉 가로세로 3개 로 하면 6개를 모두 채울 수 있게 된다.
    else:
        numberofFramebox=math.trunc(math.sqrt(numOfframe)) # 정확하게 루트해도 정수값이 나오면 ㄱㄱ

    cellwidth,cellheight=framewidth//numberofFramebox,frameheight//numberofFramebox
    # numOfFrameRow,numOfFrameCol=framewidth//cellwidth,frameheight//cellheight # 이건 있으면 안 됨, 이렇게 사용하면 가로 세로 box개수 맞추기가 더 어려움
    # frameratio=1.0/numOfframe
    background_rand=["#ff4dff","#3385ff","#4dff4d","#ff8c1a","#99bbff"]
    # background_rand=["white"]
    cursur_rand=["based_arrow_down","based_arrow_up","boat","bogosity", "bottom_left_corner", "bottom_right_corner", "bottom_side","bottom_tee","box_spiral","center_ptr","circle","clock"]
    for boxnumber in range(numOfframe):
        framename="frame{}".format(boxnumber)
        bgrand=random.choice(background_rand)
        currand=random.choice(cursur_rand)
        tkframeData[framename]={"obj":tk.Frame(tkframeData['obj'],bg=bgrand,cursor=currand,name=framename),"widgets":{}}#"#595150"
        # tkframeData[framename]["obj"].place(x=(boxnumber%(numberofFramebox))*cellwidth,y=(boxnumber//(numberofFramebox))*cellheight,width=cellwidth,height=cellheight)
        
        tkframeData[framename]["obj"].place(relx=(boxnumber%numberofFramebox)*(cellwidth/windowsize[0]),rely=(boxnumber//numberofFramebox)*(cellheight/windowsize[1]),relwidth=cellwidth/windowsize[0],relheight=cellheight/windowsize[1])
        # tkframeData[framename]["obj"].place() # 스읍 비율로 하는 것도 조금 고민이 필요하네요 , 일단 급하게 빨리 완성해야하니 .. pass
        tkframeData[framename]["obj"].bind("<Enter>",lambda event,framedict=tkframeData:mouseOnframe(event,framedict))
        tkframeData[framename]["obj"].bind("<Leave>",lambda event,framedict=tkframeData:mouseOffframe(event,framedict))
    root_frame=tkframeData.copy()
    return root_frame


print(frameConstructor("",8,(1000,1000)))