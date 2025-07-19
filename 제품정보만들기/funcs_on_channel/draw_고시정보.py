import pandas as pd
import tkinter as tk


def series_고시정보(고시정보:str)->pd.Series:
    """
    고시정보 string을 format에 맞게 분류하여 pd.Series 객체로 return합니다.
    """
    고시내용들=고시정보.split("||")[:-1]# 제일 마지막은 빈칸이라서.
    고시={}
    for words in 고시내용들:
        고시제목,고시내용=words.split(":")
        고시[고시제목]=고시내용
    return pd.Series(고시)

def draw_고시정보(고시정보:str,title,windowInitialpos,toplevel=False,tkobj:tk.Tk=None):
    """
    parameters\n
    1. 고시정보 format : f"{고시제목}:{고시정보}||" (고시정보 있음) or "" (고시정보 없음)\n
    2. toplevel : bool, Default : False.  기존에 사용하는 tk.Tk()객체가 있을 경우 유지시키고 새로운 window를 생성.\n
    3. tkobj : 기존에 갖고 있는 tk.Tk()객체가 있을 때 여기에 덮어 씌우기 위함.\n
    return : (tk.Tk()객체,tk.Text()객체). .mainloop()하면 blocking되니까 .update()로 객체를 보이게하고 나중에 destroy하면 됨. Text객체는 수시로 내용을 변경해야할 때 사용하라고 return\n
    """
    if not 고시정보:
        # 고시정보가 아예 없을 수도 있으면 빈 string임
        return 0
    고시내용들=고시정보.split("||")[:-1]# 제일 마지막은 빈칸이라서.
    고시={}
    for words in 고시내용들:
        고시제목,고시내용=words.split(":")
        고시[고시제목]=고시내용
    고시word=""
    for key in 고시:
        고시word+=f"{key} : {고시[key]}\n\n"
    if toplevel:
        고시tk=tk.Toplevel()
        고시tk.geometry(f"500x500+{windowInitialpos[0]}+{windowInitialpos[1]}")
    elif tkobj:
        고시tk=tkobj
    else:
        고시tk=tk.Tk()
        고시tk.geometry(f"500x500+{windowInitialpos[0]}+{windowInitialpos[1]}")
    고시tk.title(f"{title} , 고시정보 decoding 결과")
    고시text=tk.Text(고시tk,wrap="word",name="고시Text") # 해당 제품명 이름으로 정한 이유를 적는 공간
    고시text.insert(tk.END,고시word)
    고시text.config(state="disabled")
    고시text.place(x=0,y=0,relwidth=1,relheight=1)
    return (고시tk,고시text)