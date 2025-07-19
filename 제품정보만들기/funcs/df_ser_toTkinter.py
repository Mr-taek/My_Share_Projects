from .all_libraries import *
def dataframe_to_TABLE(data:pd.DataFrame,title,windowpos:tuple,checkbtn:bool=False,emphasize:list|int=None,eventfunc:dict=None,tkobj=None):
    """
    기능 : 데이터프레임의 column과 row를 tk 화면으로 만들어서 tk 객체를 return시켜 언제든 mainloop 돌릴 수 있게 한다
    data : dataframe\n
    title : Frame의 제목.\n
    windowpos : 윈도우가 배치될 위치\n
    checkbtn : bool(False), 체크버튼으로 특정 행을 선택할 수 있게 하는 기능. True일 시 return할 때 선택된 행의 index를 return.\n
    emphasize : 특정 행을 강조하고 싶을 때 넘어온 행을 빨간색으로 강조. list일시 복수개의 행을 강조하고 int면 단일행만 강조.\n
    eventfunc : \n
    tkobj : None, 기존에 사용하던 tk.Tk()나 Frame 객체가 있을 경우 거기에 생성해서 덮어 씌우게 됨.\n
    return 
        1. checkbtn=False, {"root":tk.Tk(),"root_frame":tk.Frame(tk.Tk()),"table_info":dict}\n
        2. checkbtn=True, {"root":tk.Tk(),"root_frame":tk.Frame(tk.Tk()),"table_info":dict,"check_box":checkVariableBox}\n
            - 체크한 행의 넘버를 알고 싶다면 chekbox_Interpreter() 을 import 해서 사용할 것.
    ! 만약 추가 기능을 사용하고 싶다면 필독 ! \n
    - root_frame은 .place(relwidth=1,relheight=1)로 상대위치로 배치 되어 있기 때문에 이 객체를 다시 .place()를 선언해서 relwidth,relheight 등을 바꾸어 여백을 만들어서 frame을 root에 배치하면 됨.\n
    - table_info는 화면에 나타난 window의 객체들을 reference하는 tk 객체들이 담긴 dict이다. 구조는 {"columnName"(열이름이담긴 list):[],행번호1(int임):[entry객체1-1,...],행번호2:[entry객체2-1,...],...행번호N:[]}
    """
    def scrollmove(event):
        if event.delta>0:
            상품옵션canvas.yview_scroll(-1,"units")
        else:
            상품옵션canvas.yview_scroll(1,"units")
    
        
    if tkobj:
        root=tkobj
    else:
        root=tk.Tk()
    rootwidth,rootheight=1000,500
    root.geometry(f"{rootwidth}x{rootheight}+{windowpos[0]}+{windowpos[1]}")
    root.title(title)
    상품옵션frame=tk.Frame(root)
    # 상품옵션frame.place(x=0,y=0,relwidth=1,relheight=0.8)
    상품옵션frame.place(relwidth=1,relheight=1)
    상품옵션frame.grid_rowconfigure(0,weight=1) # 열이름이랑 내용 모두 weight할 수 있게 ..

    root.bind("<MouseWheel>",scrollmove)

    상품옵션canvas=tk.Canvas(상품옵션frame)
    상품옵션canvas.grid(row=0,column=0)
    scrollbar=tk.Scrollbar(상품옵션frame,command=상품옵션canvas.yview)
    scrollbar.grid(row=0,column=1,sticky="ns")
    scrollbar_horizontal=tk.Scrollbar(상품옵션frame,command=상품옵션canvas.xview,orient="horizontal")
    scrollbar_horizontal.grid(row=1,column=0,sticky="ew")
    상품옵션canvas.configure(yscrollcommand=scrollbar.set,xscrollcommand=scrollbar_horizontal.set)
    상품옵션table=tk.Frame(상품옵션canvas)
    상품옵션canvas.create_window(0,0,window=상품옵션table,anchor="nw")

    colwidth=rootwidth/data.shape[1]
    colheight=rootheight/data.shape[0]
    cols=list(data.columns)
    cols.insert(0,"no")
    table_info={"columnName":cols.copy()}
    for dex,colname in enumerate(cols):
        colname=colname.lower()
        if colname=="no":
            ent=tk.Entry(상품옵션table,name=colname,width=5)
            ent.insert(0,colname)
            ent.config(state="readonly")
            ent.grid(row=0,column=dex)
        else:

            ent=tk.Entry(상품옵션table,name=colname)
            ent.insert(0,colname)
            ent.config(state="readonly")
            ent.grid(row=0,column=dex)
 
    checkVariableBox=[]
    for position,i in enumerate(range(data.shape[0]),1):
        if checkbtn:
            ckb=tk.Checkbutton(상품옵션table,name=f"{position}_0",variable=tk.IntVar())
            checkVariableBox.append(ckb)
            table_info[position]=[]
            ckb.grid(row=position,column=0,padx=0.01,pady=.01)
        else:
            ent=tk.Entry(상품옵션table,name=f"{position}_0")
            ent.insert(0,str(position))
            table_info[position]=[]
            # ent.place(x=0,y=(position*colheight),width=colwidth,height=colheight)
            ent.grid(row=position,column=0)
        # ent.place(x=0,y=(position*colheight),width=colwidth,height=colheight)
        for position_col,v in enumerate(data.iloc[i].values,1):
            ent=tk.Entry(상품옵션table,name=f"{position}_{position_col}")
            table_info[position].append(ent)
            ent.insert(0,v)
            ent.grid(row=position,column=position_col)
    if isinstance(emphasize,list):
        for row in emphasize:
            for col in range(len(cols)):
                상품옵션table.nametowidget(f"{row+1}_{col}").configure(fg="red")
    elif isinstance(emphasize,int):
        for col in range(len(cols)):
                상품옵션table.nametowidget(f"{emphasize+1}_{col}").configure(fg="red")
    상품옵션canvas.config(width=rootwidth-20,height=rootheight)
    상품옵션frame.config(width=rootwidth,height=rootheight)
    상품옵션frame.update_idletasks()
    상품옵션canvas.config(scrollregion=상품옵션canvas.bbox("all"))
    if checkbtn:
        return {"root":root,"root_frame":상품옵션frame,"table_info":table_info,"check_box":checkVariableBox}
    else:
        return {"root":root,"root_frame":상품옵션frame,"table_info":table_info}

def series_to_TABLE(data:pd.Series,title,windowInitialpos,eventfunc:dict=None):
    """
    기능 : 데이터프레임의 column과 row를 tk 화면으로 만들어서 tk 객체를 return시켜 언제든 mainloop 돌릴 수 있게 한다
    data : dataframe\n
    eventfunc : \n
    title : window 제목\n
    windowInitialpos : tuple (x,y), window가 초기에 나타날 위치
    return {"root":tk.Tk(),"root_frame":tk.Frame(tk.Tk())}\n\n
    ! 만약 추가 기능을 사용하고 싶다면 필독 ! \n
    - root_frame은 .place(relwidth=1,relheight=1)로 상대위치로 배치 되어 있기 때문에 이 객체를 다시 .place()를 선언해서 relwidth,relheight 등을 바꾸어 여백을 만들어서 frame을 root에 배치하면 됨.\n
    """
    def scrollmove(event):
        if event.delta>0:
            상품옵션canvas.yview_scroll(-1,"units")
        else:
            상품옵션canvas.yview_scroll(1,"units")
    
    root=tk.Tk()
    root.title(title)
    rootwidth,rootheight=1000,500
    root.geometry(f"{rootwidth}x{rootheight}+{windowInitialpos[0]}+{windowInitialpos[1]}")
    root.title()
    상품옵션frame=tk.Frame(root)
    # 상품옵션frame.place(x=0,y=0,relwidth=1,relheight=0.8)
    상품옵션frame.place(relwidth=1,relheight=1)
    상품옵션frame.grid_rowconfigure(0,weight=1) # 열이름이랑 내용 모두 weight할 수 있게 ..

    root.bind("<MouseWheel>",scrollmove)

    상품옵션canvas=tk.Canvas(상품옵션frame)
    상품옵션canvas.grid(row=0,column=0)
    scrollbar=tk.Scrollbar(상품옵션frame,command=상품옵션canvas.yview)
    scrollbar.grid(row=0,column=1,sticky="ns")
    scrollbar_horizontal=tk.Scrollbar(상품옵션frame,command=상품옵션canvas.xview,orient="horizontal")
    scrollbar_horizontal.grid(row=1,column=0,sticky="ew")
    상품옵션canvas.configure(yscrollcommand=scrollbar.set,xscrollcommand=scrollbar_horizontal.set)
    상품옵션table=tk.Frame(상품옵션canvas)
    상품옵션canvas.create_window(0,0,window=상품옵션table,anchor="nw")

    cols=list(data.index)

    for position_col,v in enumerate(data.index):
        colname=cols[position_col].lower()
        colent=tk.Label(상품옵션table,text=colname,name=colname)
        # colent.config(state="readonly")
        colent.grid(row=position_col*2,column=0,padx=50,pady=50)
        ent=tk.Entry(상품옵션table,name=colname+f"_{position_col}")
        ent.insert(0,data[v])
        ent.grid(row=position_col*2,column=4,sticky="wens")
    상품옵션canvas.config(width=rootwidth-20,height=rootheight)
    상품옵션frame.config(width=rootwidth,height=rootheight)
    상품옵션frame.update_idletasks()
    상품옵션canvas.config(scrollregion=상품옵션canvas.bbox("all"))
    return {"root":root,"root_frame":상품옵션frame}

def table_infoInterpreter(datapath:str,table_info:dict,use_return=False)->pd.DataFrame:
    """
    dataframe_to_TABLE을 통해 return 된 "table_info"의 정보를 해석하여 dataframe으로 반환.\n

    dataframe_to_TABLE으로 반환된 root tkinter 객체의 특정 cell의 Text 정보가 변경되고 해당 변경된 정보를 가져올때 사용한다.
    - params 
        1. datapath : 수정한 정보를 덮어씌우거나 만들어낼 datapath
        2. table_info : dataframe_to_TABLE에서 return된 "table_info" dict 객체
        3. use_return : bool(False), 데이터를 생성하지않고 return(True)
    """
    data={col:[] for col in table_info["columnName"]}
    data.pop("no")
    valuekeyname=[] # 1,2,3,4 .. 와같이 행의 index가 담김
    keyname=[] # no을 제외한 행의 이름이 담김 .
    for key in data:
        if key!="no":
            keyname.append(key)
    for key in table_info:
        if key!="columnName":
            valuekeyname.append(key)
    for key in valuekeyname: # table_info는 행의 번호대로 행의 값(entry객체)가 있기 때문에 먼저 1,2,3.. 을 for문으로 작성.
        for colname,value in zip(keyname,table_info[key]): #keyname은 위 data객체에 들어갈 실제 column이름이 있음. no는 사전에 제외돼서 걱정 ㄴ
            data[colname].append(value.get())
    if use_return:
        return pd.DataFrame(data)
    pd.DataFrame(data).to_csv(datapath,index=False,encoding="UTF-8-sig")


def chekbox_Interpreter(table_info:dict,checkVariableBox:list):
    """
    기능 : 체크버튼으로 선택한 행의 값들만 뽑아서 저장하기
    - parameters
        1. datapath : 수정한 정보를 덮어씌우거나 만들어낼 datapath
        2. table_info : dataframe_to_TABLE에서 return된 "table_info" dict 객체
        3. checkVariableBox : dataframe_to_TABLE에서 return된 "checkVariableBox" list 객체

    return : pd.dataframe().iloc[선택한행의인덱스].copy()
    """
    d=table_infoInterpreter("",table_info,True)
    checked=[]
    # print(checked)
    for dex,v in enumerate([cktBox.getvar(cktBox.cget("variable")) for cktBox in checkVariableBox]):
        if v=="1":
            checked.append(dex)
    return d.iloc[checked].copy()

    