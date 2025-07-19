import requests,re,random,math
import tkinter as tk
from tkinter import messagebox
from PIL import Image,ImageTk
import os,asyncio
import pandas as pd
import sqlite3 as sql
import matplotlib.pyplot as plt
from funcs.keyword_func.my_hanspell import main
from funcs_on_channel.draw_고시정보 import draw_고시정보
from funcs.sqlFuncs import dbtoDataframe
from funcs.df_ser_toTkinter import dataframe_to_TABLE,chekbox_Interpreter,table_infoInterpreter
from funcs.sqlFuncs import queryCreator
from colorama import Fore
import numpy as np
HEIGHT,WIDTH=960,1600

def frameHeritancemaker(geneologydict:dict):
    """
    Frame안에 또 다른 Frame이 계속 생길 수 있다. 깊어질 수록 그 구조가 복잡해지기 때문에 자동으로 생성해주는 함수가 필요하다
    - 구조 
    {"Frame1":{"obj":tk.Frame(),"Frame1-1":tk.Frame,
                                "Frame1-2":{"obj":tk.Frame(),"Frame1-2-1:tk.Frame()}},
    "Frame2":tk.Frame(),
    "Frame3":tk.Frame()
    }
    - 구조설명
        1. "Frame":tk.Frame() 일 경우 해당 Frame은 내부에 포함하는 다른 Frame이 없다. isinstance로 tk.Frame으로 구별하면 된다
        2. "Frame":{} , 값이 dict일 경우 Frame이 포함하는 다른 tk.Frame()이 있다는 것이다
            1. "obj" : 상위 Frame의 tk.Frame()객체이다. 즉 다른 tk.Frame()을 포함하는 부모 Frame이 "obj" key로 저장되어 있다.

    """
def frameObtainer(self):
    """
    """
def DB_CREATOR(DBNAME,PATH,COLNAMES:list):
    """
    DBNAME : 생성할 DB의 TABLE 이름
    PATH : DB 생성할 경로 ,
    COLNAMES : TABLE이 갖고있는 COLUMN NAME들, [[columname1,DATATYPE(DATETIME,TEXT,etc..)],[columname2,DATATYPE(DATETIME,TEXT,etc..)],...]
    """
    import os
    if os.path.splitext(DBNAME)[-1]!=".db":
        print("DBNAME의 확장자가 .db로 고쳐주세요")
        return 0
    conn=sql.connect(os.path.join(PATH,DBNAME)) # connect만 해도 지가 알아서 경로끝에 있으면 연결하고 없으면 만듦.
    cur=conn.cursor()
    col="("
    for name in COLNAMES:
        col+="'{}' {} ,".format(name[0],name[1])

    col=col[:-1] +")"
    print(f"CREATE TABLE IF NOT EXISTS {os.path.splitext(os.path.basename(DBNAME))[0]} {col}")
    cur.execute(f"CREATE TABLE IF NOT EXISTS {os.path.splitext(os.path.basename(DBNAME))[0]} {col}")
    return (conn,cur)
class temp:
    def __init__(self,smartsotre_csvpath,datapath,pictureframename="frame1",informframename="frame0",inputframename="frame2",dbframename="frame3"):
        """
        
        구현완료 리스트
        1.  kwargs 종류
            1. 
        """
        self.root_frame={"tk_root":tk.Tk()}
        
        self.root_frame["tk_root"].geometry("{}x{}".format(1000,1000))
        self.root_frame["tk_root"].update() # geomery 값들을 얻으려면적용하려면 이게 필수네 ..
        
        self.pictureframename=pictureframename # frame생성후 어느 프레임이 사진용 frame인지 만든 후에 이 변수에다가 그 프레임의 이름을 꼭 적어야함. 나중에 사진에서 대표사진이 여러개일 때 키보드 좌우를 사용해서 사진변경할 때 사용함
        self.informframename=informframename # 제품의 원 이름, 제품코드 제품 키워드를 표현할 Frame
        self.inputframename=inputframename
        self.dbframename=dbframename # DB
        self.histogramfigure,self.histogramaxis=plt.subplots()
        self.혜택가격모음={"쿠폰할인값":{"0<=<=5000":500,"5000<<=10000":0.01},# 쿠폰할인의 value값이 1보다 작은건 %이고 크면 원 값임. key이름은 re.search("[\D]*")로 구해서 <=,= 인 경우처럼 if문으로 작성하기.
        "네이버포인트값":{"상품구매시지급":0.2,
                   "상품리뷰_텍스트리뷰지급":0.2,"상품리뷰_포토동영상리뷰지급":0.4,# 텍스트 리뷰와 포토/동영상 리뷰 포인트는 중복지급되지 않습니다. 포토/동영상 리뷰가 필요하시다면, 포토/동영상 리뷰 작성에 더 많은 포인트를 설정해보세요.
                   "한달사용_텍스트리뷰지급":0.1,"한달사용_포토동영상리뷰시지급":0.1,
                   "알람받기동의고객리뷰지급":0.1}}# 일단 상품 구입하면 기본으로 20% 환급해주기, 텍스트 리뷰 작성하면 20%, 포토 동영상으로 작성하면 40%
        self.frameConstructor("",4,self.root_frame)
        if os.path.exists(r"C:\Users\dlrms\OneDrive\Desktop\mymarket\제품정보.db"):
            self.DB=sql.connect("제품정보.db")
            self.DBtableName="제품정보"
        else:
            self.DB,self.cursor=DB_CREATOR("제품정보.db","",[["제목","TEXT"],["제목설명", "TEXT"],["가격" ,"TEXT"],["제품코드", "TEXT"],["원상품명" ,"TEXT"]])
            # self.DB=sql.connect("제품정보.db")
            self.DBtableName="제품정보"
            # self.DB.execute("CREATE TABLE 제품정보 (제목 TEXT,제목설명 TEXT,가격 TEXT,제품코드 TEXT PRIMARY KEY,원상품명 TEXT)")
            
        self.cursor=self.DB.cursor()
        self.on_channel_data=pd.read_csv(datapath)
        self.smartsotre_crawling_data=pd.read_csv(smartsotre_csvpath)
        
        self.index=self.getIndex_notInDb(self.cursor,self.DBtableName,self.on_channel_data,"제품코드")
        while True:
            self.indexed_on_channel_data=self.on_channel_data.iloc[self.index].squeeze()
            self.queried_smartsotre_crawling_data=self.smartsotre_crawling_data.query('제품코드=="{}"'.format(self.indexed_on_channel_data['제품코드']))
            if self.queried_smartsotre_crawling_data.shape[0]>1:
                messagebox.showwarning("스마트스토어 제품코드 unique 위배 에러",f"제품코드 '{self.indexed_on_channel_data['제품코드']}' 가 스마트스토어 크롤링 파일에 두개 이상이 있습니다.")
                self.index+=1
                continue
            self.queried_smartsotre_crawling_data=self.queried_smartsotre_crawling_data.squeeze()
            if isinstance(self.queried_smartsotre_crawling_data,pd.DataFrame):
                self.queried_smartsotre_crawling_data=pd.Series(index=self.queried_smartsotre_crawling_data.columns,dtype=float)
            self.queried_smartsotre_crawling_data.fillna("",inplace=True)
            break
        self.cursor.execute("SELECT * FROM 제품정보")
        self.numofdata=len(self.cursor.fetchall())
        self.cursor.execute("SELECT * FROM 제품정보")
        # initial_contents=self.cursor.fetchall()[:20]
        self.dbcolumnName=[i[0] for i in self.cursor.description]
        self.numoffeature=len(self.dbcolumnName)
        self.numofshowdata=15
        # self.maxpage=self.numofdata//self.numofshowdata+1 if self.numofdata%self.numofshowdata!=0 else self.numofdata//self.numofshowdata # 나중에 insert할때는 얘도 update시켜줘야 함 .
        self.maxpage=self.numofdata//self.numofshowdata+1
        self.pagemove_currentpage=1
        self.current_framename=None
        self.contents_grid_box={}
        self.trashbox=[]
        self.root_MoveData(True)
        self.root_frame[self.inputframename]["widgets"]=self.createinputframe(self.root_frame[self.inputframename]["obj"],self.inputframename,"insert")
        self.createdbframe()
        self.createInformationframe()
        self.optionPriceWindow=tk.Tk() # 가격대 만드는 윈도우임.
        self.optionPriceWindow.geometry("700x500")
        self.update_기타window(usage="create")
        self.finalInitialization() # 더 이상, 함수를 만들지마, 변경할 게 있으면 지금 여기 있는 함수들 안에서 싹 바꿔. 차라리 기능화해서 하나하나 모듈화
        
    def getIndex_notInDb(self,cursor,dbname,등록할제품data,등록할제품SearchingColname):
        for i,제품코드 in enumerate(등록할제품data[등록할제품SearchingColname]):
            cursor.execute(f"SELECT * FROM {dbname} WHERE 제품코드='{제품코드}'")
            if cursor.fetchall():
                continue
            else:
                return i
    def update_기타window(self,고시정보tkobj=None,옵션정보tkobj=None,usage="renew"):
        """
        pricehistogram, 고시정보, 옵션선택 을 위한 window 생성을 하기 위해 존재하는 함수.

        - params
            1. usage : price histogram 생성에 필요한 인자."create","renew" 가 있는데 create는 init할때만 사용하고 이후로는 "renew"임
        """
        self.priceHistogram_handler(usage)
        self.createPricesettingwindow()
        if 고시정보tkobj:
            self.고시정보=draw_고시정보(self.indexed_on_channel_data["고시정보"],self.indexed_on_channel_data["rank_title"]+" 의 고시정보",(2100,350),tkobj=고시정보tkobj)
        else:
            self.고시정보=draw_고시정보(self.indexed_on_channel_data["고시정보"],self.indexed_on_channel_data["rank_title"]+" 의 고시정보",(2100,350))
        self.고시정보[0].update()
        
        if os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__),"상품별가격_상품의타이틀로 저장됨"),self.indexed_on_channel_data["rank_title"]+".csv")):
            optionData=pd.read_csv(os.path.join(os.path.dirname(__file__,"상품별가격_상품의타이틀로 저장됨"),self.indexed_on_channel_data["rank_title"]+".csv"))
            optionData.fillna(value={"판매자가":0},inplace=True)
            optionData.replace({"판매자가":"[\s\n,.']"},"",regex=True,inplace=True)
            optionData=optionData.astype({"판매자가":"float64"})
            
            # 스마트스토어의 에러중 "옵션의 옵션값 항목에 등록불가인 특수문자가 포함되어 있습니다. \ * ? " < >" 라서 이 특수문자는 제거해야함
            # 단 , *는 X(곱하기)의 의미로 쓰이기 때문에 제거하지 않기
            # 단 , \ 는 무언가 칸을 나누는 것이기 때문에 _ 로 대체
            for index in range(optionData.shape[0]):

                if re.search('[*]',optionData.iloc[index]["옵션명"]):
                    optionData.at[index,"옵션명"]=re.sub('[*]','X',optionData.iloc[index]["옵션명"])
                elif re.search(r'\\',optionData.iloc[index]["옵션명"]):
                    optionData.at[index,"옵션명"]=re.sub('[\]','_',optionData.iloc[index]["옵션명"])
                elif re.search('[? " < >,\']',optionData.iloc[index]["옵션명"]):
                    optionData.at[index,"옵션명"]=re.sub('[\ ? " < >,\']','',optionData.iloc[index]["옵션명"])


            if isinstance(self.indexed_on_channel_data["판매사가"],str):
                
                optionData["판매자가"]-=int(re.sub("[\s',.]","",self.indexed_on_channel_data["판매사가"]))
            else:
                optionData["판매자가"]-=self.indexed_on_channel_data["판매사가"]
            if optionData.shape[0]>10:
                if 옵션정보tkobj:
                    self.옵션정보=dataframe_to_TABLE(optionData,self.indexed_on_channel_data["rank_title"]+"의 옵션 테이블",(2450,350),checkbtn=True,tkobj=옵션정보tkobj)
                    self.옵션정보["root"].update()
                else:
                    self.옵션정보=dataframe_to_TABLE(optionData,self.indexed_on_channel_data["rank_title"]+"의 옵션 테이블",(2450,350),checkbtn=True)
                    self.옵션정보["root"].update()
            else:
                if 옵션정보tkobj:
                    self.옵션정보=dataframe_to_TABLE(optionData,self.indexed_on_channel_data["rank_title"]+"의 옵션 테이블",(2450,350),tkobj=옵션정보tkobj)
                    self.옵션정보["root"].update()
                else:
                    self.옵션정보=dataframe_to_TABLE(optionData,self.indexed_on_channel_data["rank_title"]+"의 옵션 테이블",(2450,350))
                    self.옵션정보["root"].update()
    def finalInitialization(self):
        """
        submot을 모두 마친 뒤, 모든 사전 변경작업이 완료된 후 window에서 entry 또는 text box등에 변경사항을 적용시켜야할 때 사용함
        """
        temp_t=""
        for i in self.indexed_on_channel_data["keyword"].split("#"):
            if i != "":
                temp_t+=i+","
        self.root_frame[self.inputframename]["widgets"]["product_tag"].delete("1.0","end")
        self.root_frame[self.inputframename]["widgets"]["product_tag"].insert(tk.END,temp_t[:-1])
        # self.root_frame[framename]["widgets"]["product_tag"].delete("1.0","end")
        # return {"producttitlearea":producttitlearea,"producttitle_description_area":producttitle_description_area,"product_price":productprice,"product_tag":producttags}

    def createInformationframe(self):
        def calculator(event,purpose):
            key=event.keysym
            # if not key.isnumeric():
            #     return True
            if marginpercent_entry.get() and default_revenue_entry.get():
                if purpose=="percent":
                    percent=float(marginpercent_entry.get())/100
                    산정액=판매사가+판매사가*percent+기본배송비
                    recom_price.configure(text=f"{산정액} 원")
                    
                elif purpose=="revenue":
                    revenue=float(default_revenue_entry.get())
                    산정액=판매사가+판매사가*marginpersent+revenue
                    recom_price.configure(text=f"{산정액} 원")
        
        판매사가=self.indexed_on_channel_data["판매사가"]
        t="""Rank_title : {}\n\n 제품코드 : {}\n\n 제품 키워드 : {}\n\n가격정책:{}(가격준수:소비자가절대지키기,가격자율:소비자가무시)\n\n판매사가:{}\t소비자가:{}\n\n""".format(self.indexed_on_channel_data["rank_title"],self.indexed_on_channel_data["제품코드"],self.indexed_on_channel_data["keyword"],self.indexed_on_channel_data["가격정책"],판매사가,self.indexed_on_channel_data["소비자가"])
        text=tk.Text(self.root_frame[self.informframename]["obj"],name="productinform")
        text.insert(tk.END,t)
        # 단어 산포도 만드려고 했는데 시간이 없어서 pass
        # numberrange=[]
        # for keyword in re.findall("\([^)]+\)",self.queried_smartsotre_crawling_data["키워드"]):
        #     numberrange.append(int(re.search("\d+",keyword)))
        # maxv,minv=np.max(numberrange),np.min(numberrange)
        # if maxv-minv>=5:
        #     dividerange=np.linspace(minv,maxv,5)
        # else:
        #     dividerange=np.linspace(minv,maxv,maxv-minv)
        # dividerange_dict={}
        # for div_i in range(len(dividerange),2):
        #     dividerange_dict[str(dividerange[div_i]+"~"+dividerange[div_i+1])]=[]
        # for keyword in re.findall("\([^)]+\)",self.queried_smartsotre_crawling_data["키워드"]):
        #     numofshow=int(re.search("\d+",keyword))
        #     for i in range(0,len(dividerange),2):
        #         if dividerange[i]<= keyword and keyword<=dividerange[i+1]
        #         if i==0
        키워드매칭=[]
        print(self.queried_smartsotre_crawling_data["키워드"])
        if self.queried_smartsotre_crawling_data["키워드"]:
            for keyword in re.findall("\([^)]+\)",self.queried_smartsotre_crawling_data["키워드"]):
                word=re.search("'[^']+'",keyword)
                if word==None:
                    word=""
                else:
                    word=word.group(0)
                num=re.search("\d+",keyword)
                if num==None:
                    num=str(0)
                else:
                    num=num.group(0)
                키워드매칭.append(word+":"+num)
        else:
            키워드매칭.append("No keyword")
        text.insert(tk.END,키워드매칭)
        text.insert(tk.END,"\n\n")
        text.insert(tk.END,"일반배송비 :{} , 제주도배송비 : {} , 도서산간 : {}".format(self.indexed_on_channel_data["일반배송"],self.indexed_on_channel_data["제주도배송"],self.indexed_on_channel_data["도서산간"]))
        text.config(state="disabled")
        text.place(relx=0,rely=0,relwidth=1,relheight=0.7)
        calculation_frame=tk.Frame(self.root_frame[self.informframename]["obj"],name="calculation",bg="#7db6a3")
        calculation_frame.place(relx=0,rely=0.7,relheight=0.3,relwidth=1)
        # 판매가격정하는 곳------------------
        tk.Label(calculation_frame,text="margin persent % : ",bg="#7db6a3").place(relx=0.05,rely=0.05)
        marginpercent_entry=tk.Entry(calculation_frame,validate="key",validatecommand=(calculation_frame.register(lambda x: x.isnumeric()),"%S"))
        marginpercent_entry.place(relx=0.28,rely=0.05,relwidth=0.05)
        tk.Label(calculation_frame,text="%",bg="#7db6a3").place(relx=0.32,rely=0.05,relwidth=0.02) # "% 쓰는 녀석"
        
        tk.Label(calculation_frame,text="Default revenue 원 : ",bg="#7db6a3").place(relx=0.05,rely=0.2)
        default_revenue_entry=tk.Entry(calculation_frame,validate="key",validatecommand=(calculation_frame.register(lambda x: x.isnumeric()),"%S"))
        default_revenue_entry.place(relx=0.28,rely=0.2,relwidth=0.1)
        tk.Label(calculation_frame,text="원",bg="#7db6a3").place(relx=0.4,rely=0.2,relwidth=0.02) # "% 쓰는 녀석"
        
        
        if 판매사가<15000:
            marginpersent=0
            # 기본배송비=3000
            기본배송비=1000
            marginpercent_entry.delete(0,tk.END)
            marginpercent_entry.insert(0,marginpersent) # 초기값
            marginpercent_entry.configure(state="disabled")
            default_revenue_entry.bind("<KeyPress>",lambda event,purpose="revenue":calculator(event,purpose))
            default_revenue_entry.delete(0,tk.END)
            default_revenue_entry.insert(0,기본배송비) # 초기값
        else:
            marginpersent=10
            기본배송비=0
            marginpercent_entry.bind("<KeyPress>",lambda event,purpose="percent":calculator(event,purpose))
            marginpercent_entry.delete(0,tk.END)
            marginpercent_entry.insert(0,marginpersent) # 초기값
            default_revenue_entry.delete(0,tk.END)
            default_revenue_entry.insert(0,기본배송비) # 초기값
            default_revenue_entry.configure(state="disabled")
        
        # ------------------------------------
        
        initial산정액=판매사가+판매사가*(marginpersent/100)+기본배송비
        tk.Label(calculation_frame,text="최종 산정액 : 원",bg="#7db6a3").place(relx=0.05,rely=0.65)
        recom_price=tk.Label(calculation_frame,text=f"{initial산정액} 원")
        recom_price.place(relx=0.28,rely=0.65,relwidth=0.15)
        


        명심칸=tk.Text(calculation_frame,bg="#7db6a3",fg="red")
        명심칸.insert(tk.INSERT,"24-03-12협의, 1천원의 마진을 남기고 2천원을 할인 또는 아예 포인트로 주는 방법으로 하기로 함. 이율도 10%로 조정\n24-02-15 협의, 20% 이율 적용시 3천원의 마진이 남아야 한다. 판매사가 15,000원 이상은 20% 적용,이하는 +3000원 적용")
        명심칸.place(relx=0,rely=0.8,relwidth=1,relheight=0.2)
        
        

    def createinputframe(self,frame:tk.Frame,framename:str,order:str):
        """
        특징\n
        1. self.submit 함수와 밀접한 관계에 있음. 생성된 frame에 "제출하기"버튼을 누르면 submit함수가 실행된다.\n
        - parameter\n
        frame : inputframe을 만들 Frame. Frame만 넘기면 해당 Frame에 같은 Format을 만들 수 있기 때문에 frame을 넣음.\n
        order: 'insert'가 default, 삭제명령은 "remove" , 수정명령은 "modify"\n
        """
        tk.Label(frame,text="Product Title name",name="ptn").place(relx=0.05,rely=0.2)
        tk.Label(frame,text="Product Price",name="pp").place(relx=0.05,rely=0.25)
        producttitlearea=tk.Entry(frame)
        producttitlearea.place(relx=0.4,rely=0.2)
        productprice=tk.Entry(frame)
        productprice.place(relx=0.4,rely=0.25)
        tk.Label(frame,text="Product recommand tags",name="prt").place(relx=0.05,rely=0.3)
        producttags=tk.Text(frame)
        producttags.place(relx=0.4,rely=0.3,relheight=0.15,relwidth=0.4)
        tk.Label(frame,text="Product title description").place(relx=0.05,rely=0.5)
        producttitle_description_area=tk.Text(frame,wrap="word") # 해당 제품명 이름으로 정한 이유를 적는 공간
        producttitle_description_area.place(relx=0.05,rely=0.6,relwidth=0.9,relheight=0.45)
        submit=tk.Button(frame,text="제출하기",command=lambda m=framename:self.submit(m,order))
        submit.place(relx=0.4,rely=0.8)
        return {"producttitlearea":producttitlearea,"producttitle_description_area":producttitle_description_area,"product_price":productprice,"product_tag":producttags}
    def createimageframe(self,picturebox):
        def 상세페이지croping():
            """
            상세페이지 사진을 잘라내고\n
            1000x1000 사진으로 재구성해서 저장함
            """
            상세페이지box=[]
            path=os.path.join(root_path상품이미지,self.indexed_on_channel_data["rank_title"])
            if not os.path.exists(path):
                messagebox.showwarning("상세페이지 경로 없음",f"{path}는 없는 경로입니다")
                return 0
            for picture in os.listdir(path):
                if re.search("상품설명사진|상세",picture):
                    상세페이지box.append(picture)
            if not os.path.exists(os.path.join(path,"croping")):
                os.mkdir(os.path.join(path,"croping"))
            croprootpath=os.path.join(path,"croping")
            picturenumber=0
            for 상세페이지 in 상세페이지box:
                img=Image.open(os.path.join(path,상세페이지))
                imgwidth,imgheight=img.size
                borderOfheight=0
                while True:
                    if (borderOfheight+1)*1000<imgheight:
                        croped=img.crop((0,borderOfheight*1000,imgwidth,(borderOfheight+1)*1000))
                        croped=croped.resize((1000,1000))
                        borderOfheight+=1
                        picturenumber+=1
                        croped.save(os.path.join(croprootpath,f"{picturenumber}.jpg"))
                    else:
                        croped=img.crop((0,borderOfheight*1000,imgwidth,imgheight))
                        croped=croped.resize((1000,1000))
                        picturenumber+=1
                        try:
                            croped.save(os.path.join(croprootpath,f"{picturenumber}.jpg"))
                        except:
                            croped.convert("RGB").save(os.path.join(croprootpath,f"{picturenumber}.jpg"))
                        break
        self.imageindex=0
        self.total_images=len(picturebox)-1
        self.picturebox=picturebox
        original_img=Image.open(self.picturebox[self.imageindex]) # PIL로 읽으면
        original_img=original_img.resize((int(self.root_frame[self.pictureframename]["obj"].place_info()["width"]),int(self.root_frame[self.pictureframename]["obj"].place_info()["height"])))
        상세페이지croping()
        self.img=ImageTk.PhotoImage(original_img) # 이유는 모르겠지만 네.. ImageTk는 self 로 해야 접근 이 되나 보네요
        # self.root_frame[frame]["widgets"]["lab1"]=tk.Label(self.root_frame[frame]["obj"],image=img,name="lab1")
        self.picturedescription=tk.Label(self.root_frame[self.pictureframename]["obj"],text="({} / {})".format(self.imageindex+1,self.total_images+1),anchor="se",bg="red",name="picturedescription")
        self.picturedescription.pack(side="bottom",fill=None)
        lab=tk.Label(self.root_frame[self.pictureframename]["obj"],image=self.img,name="lab1")
        lab.pack()
        
    def createdbframe(self):
        dbframe=self.root_frame[self.dbframename]["obj"]
        columnname=tk.Frame(dbframe)
        columnname.grid(row=0,column=0,sticky="nw")
        contents=tk.Canvas(dbframe)
        contents.grid(row=1,column=0)
        self.contents_frame=tk.Frame(contents)
        contents.create_window((1,0),window=self.contents_frame,anchor="nw")
        contents_scrollbar=tk.Scrollbar(dbframe,command=contents.yview)
        self.root_frame["obj"].bind("<MouseWheel>",lambda x:contents.yview_scroll(-1,"units") if x.delta>0 else contents.yview_scroll(1,"units"))
        contents_scrollbar.grid(row=1,column=1,sticky="ns")
        contents.configure(yscrollcommand=contents_scrollbar.set)
        self.cursor.execute("SELECT * FROM 제품정보")
        tk.Label(columnname,text=" ",width=5).grid(row=0,column=0)
        for i,v in enumerate([col[0] for col in self.cursor.description],1):
            tk.Label(columnname,text=v,width=8).grid(row=0,column=i)
        self.DB_updateContents(1)
        contents.config(width=self.cellwidth-self.cellwidth*0.1,height=self.cellheight-self.cellheight*0.2)
        self.contents_frame.config(width=self.cellwidth,height=self.cellheight)
        self.contents_frame.update_idletasks()
        contents.config(scrollregion=contents.bbox("all"))
        movebtn=tk.Frame(dbframe,bg="black")
        movebtn.grid(row=2,column=0)
        tk.Label(movebtn,text="Move to : ").grid(row=0,column=0)
        self.movebtn_pagemove=tk.Entry(movebtn)
        self.movebtn_pagemove.grid(row=0,column=1,columnspan=2)
        self.movebtn_pagemove.bind("<KeyPress-Return>",self.DB_pagemove)
        self.movebtn_showcurrentpage=tk.Label(movebtn,text=f"Page 1/{self.maxpage}")
        self.movebtn_showcurrentpage.grid(row=0,column=4)
        # tk.Label(movebtn,text="여기는 Text를 넣는 곳",bg="aqua").grid(row=0,column=0,rowspan=10)
    def createPricesettingwindow(self):
        def 할인율calculator(event,purpose,variableEntry:tk.Entry,defaultvariable={}):
            """
            purpose : "스마트판매가"
            """
            
            if purpose=="스마트판매가":
                    if variableEntry.get():
                            defaultvariable["스마트판매가"]=int(variableEntry.get())
                    
            elif purpose=="목표할인가":
                    if variableEntry.get():
                            defaultvariable["목표할인가"]=int(variableEntry.get())
                            for name in self.혜택가격모음["네이버포인트값"]:
                                    defaultVariable["option_widgets"][name+"_price"].config(state="normal")
                                    defaultVariable["option_widgets"][name+"_price"].delete(0,tk.END)
                                    defaultVariable["option_widgets"][name+"_price"].insert(0,defaultVariable["목표할인가"]*float(defaultVariable["option_widgets"][name+"_percent"].get()))
                                    defaultVariable["option_widgets"][name+"_price"].config(state="readonly")
            elif purpose=="옵션가":
                    # 옵션가는 쿠폰 , 네이버포인트 혜택에 대한 내용이 적힌 곳에서 오는 것인데
                    # _price, _percent 박스가 있음. _price는 readonly 처리되어서 오직 _percent Entrybox에만 키보드 변화가 생기면 넘어오게 됨.
                    optionwidgets=defaultVariable["option_widgets"]
                    widgetname=event.widget._name
                    optionname=""
                    for i in widgetname.split("_")[:-1]:
                            optionname+=i+"_"
                    optionname=optionname[:-1] # 옵션이름_price/percent 이렇게 적혀있음
                    
                    if optionwidgets[optionname+"_percent"].get():
                            percent=float(optionwidgets[optionname+"_percent"].get())
                    else:
                            percent=0

                    optionwidgets[optionname+"_price"].config(state="normal")
                    optionwidgets[optionname+"_price"].delete(0,tk.END)
                    optionwidgets[optionname+"_price"].insert(0,defaultVariable["목표할인가"]*percent)
                    optionwidgets[optionname+"_price"].config(state="readonly")
                            
            
            # 상품리뷰는 는 둘 중에 percent값이 큰 걸 가져오고 , 한달사용도 내 생각엔 둘 중 하나라서 값이 큰거 하나만 가져와
            옵션리뷰percent=0
            prime옵션리뷰=""
            한달사용percent=0
            prime한달사용=""
            for name in self.혜택가격모음["네이버포인트값"]:
                    if re.search("상품리뷰",name):
                            if float(defaultVariable["option_widgets"][name+"_percent"].get())>옵션리뷰percent:
                                    옵션리뷰percent=float(defaultVariable["option_widgets"][name+"_percent"].get())
                                    prime옵션리뷰=name+"_price"
                    elif re.search("한달사용",name):
                            if float(defaultVariable["option_widgets"][name+"_percent"].get())>한달사용percent:
                                    한달사용percent=float(defaultVariable["option_widgets"][name+"_percent"].get())
                                    prime한달사용=name+"_price"
            defaultVariable["스마트판매가"]=defaultvariable["목표할인가"]+defaultvariable["쿠폰할인값"]+defaultvariable["배송비"]+float(defaultVariable["option_widgets"][prime옵션리뷰].get())+float(defaultVariable["option_widgets"][prime한달사용].get())
            for name in self.혜택가격모음["네이버포인트값"]:
                    if re.search(r"\s?상품리뷰\s?|\s?한달사용\s?",name)==None:
                            defaultVariable["스마트판매가"]+=float(defaultVariable["option_widgets"][name+"_price"].get())
            defaultVariable["스마트판매가entry"].config(state="normal")
            defaultVariable["스마트판매가entry"].delete(0,tk.END)
            defaultVariable["스마트판매가entry"].insert(0,defaultVariable["스마트판매가"])
            defaultVariable["스마트판매가entry"].config(state="readonly")
            할인율=(defaultvariable["목표할인가"]-defaultvariable["스마트판매가"])/(-defaultvariable["스마트판매가"]) # 공식 : 
            할인율entry.config(state="normal")
            defaultvariable["할인율"]=int(round(할인율*100,0))
            defaultvariable["할인율entry"].delete(0,tk.END)
            defaultvariable["할인율entry"].insert(0,str(int(round(할인율*100,0))))
            defaultvariable["할인율entry"].config(state="readonly")
            defaultvariable["window"].update_idletasks()
        
        menubar=tk.Menu(self.optionPriceWindow,name="menu_bar",tearoff=0) # menubar.place(x=0,y=0,relheight=0.1) 은 필요 없음.
        
        menu1=tk.Menu(menubar)
        menu1.add_command(label="New File")
        menu1.add_separator()
        menubar.add_cascade(label="File",menu=menu1)
        maincontents=tk.Frame(self.optionPriceWindow,name="main_contents",bg="green")
        maincontents.place(relwidth=1,relheight=1)

        # 배송비label=tk.Label(maincontents)
        # 배송비입력=tk.Entry(maincontents)
        # print(type(self.indexed_on_channel_data["판매사가"]),self.indexed_on_channel_data["판매사가"])
        # input("dasd")
        실판매가=self.indexed_on_channel_data["판매사가"]
        목표할인가=0
        일반배송비=self.indexed_on_channel_data["일반배송"]

        # 일단 할인가 % 칸도 만들어야 하는데, 내가 원하는 목표 금액이 적고, 제품판매가 기준으로 원하는 목표 금액(가격 분포도를 보고 거기서 가장 최저의 값)이 되려면 몇 % 할인 이 들어가야 하는 지 나오게 하는 알고리즘으로 시각화 하면 됨. 할인 %는 최대 99%만 됨.\
        defaultVariable={"window":self.optionPriceWindow,"목표할인가":목표할인가,"실판매가":실판매가,"할인율":0,"배송비":일반배송비}
        tk.Label(maincontents,text="목표할인가격(원) : ").place(relx=0.05,rely=0.1)
        목표할인가격entry=tk.Entry(maincontents,validate="key",validatecommand=(maincontents.register(lambda x: x.isnumeric()),"%S"))
        목표할인가격entry.place(relx=0.3,rely=0.1,relwidth=0.15)
        tk.Label(maincontents,text="목표할인가격은 스마트스토어에 올릴 가격에다가\n할인을 붙여서 판매할 금액입니다. 가격분포도를참고해서\n그 중 가장 낮은 가격을 골라서 작성합니다").place(relx=0.5,rely=0.1)
        목표할인가격entry.bind("<KeyPress>",lambda event,purpose="목표할인가",variable=목표할인가격entry,defaultVariable=defaultVariable:할인율calculator(event,purpose,variable,defaultVariable))

        tk.Label(maincontents,text="최종 스토어 판매가(원) : ").place(relx=0.05,rely=0.2)
        스마트판매가entry=tk.Entry(maincontents)
        스마트판매가entry.place(relx=0.3,rely=0.2,relwidth=0.15)
        defaultVariable["스마트판매가entry"]=스마트판매가entry
        tk.Label(maincontents,text="스마트스토어에 올릴 판매금액입니다.\n목표할인가격 + 상품리뷰(percent높은것 1개가격)+\n한달사용(percent높은것 1개가격)옵션+나머지옵션가격+쿠폰할인값 + \n일반배송비 + 기본수익값(1000원) 값입니다.").place(relx=0.5,rely=0.2)
        

        tk.Label(maincontents,text="할인율(%) : ").place(relx=0.05,rely=0.3)
        할인율entry=tk.Entry(maincontents,state="readonly") # ,validate="key",validatecommand=(maincontents.register(lambda x: x.isnumeric()),"%S")
        할인율entry.place(relx=0.3,rely=0.3,relwidth=0.15)
        defaultVariable["할인율entry"]=할인율entry
        tk.Label(maincontents,text="할인율은 스마트스토어 판매가에서\n목표할인 판매가가 되기위한 %입니다.").place(relx=0.5,rely=0.3)
        
        tk.Label(maincontents,text="-----------옵션-----------").place(rely=0.4,relwidth=1)
        # self.혜택가격모음={"쿠폰할인값":{"0<=<=5000":500,"5000<<=10000":0.01},# 쿠폰할인의 value값이 1보다 작은건 %이고 크면 원 값임. key이름은 re.search("[\D]*")로 구해서 <=,= 인 경우처럼 if문으로 작성하기.
        # "네이버포인트값":{"상품구매시지급":0.2,
        for v in self.혜택가격모음["쿠폰할인값"]:
            leftNum,rightNum=re.findall("\d{1,10}",v)
            leftNum=int(leftNum)
            rightNum=int(rightNum)
            condition=re.search("\D+",v).group(0)
            if condition=="<=<=":
                    if leftNum<=defaultVariable["목표할인가"]<=rightNum:
                            if self.혜택가격모음["쿠폰할인값"][v]<=1:
                                    defaultVariable["쿠폰할인값"]=defaultVariable["목표할인가"]*self.혜택가격모음["쿠폰할인값"][v]        
                            else:
                                    defaultVariable["쿠폰할인값"]=self.혜택가격모음["쿠폰할인값"][v]
                            break
            elif condition=="<<=":
                    if leftNum<defaultVariable["목표할인가"]<=rightNum:
                            if self.혜택가격모음["쿠폰할인값"][v]<=1:
                                    defaultVariable["쿠폰할인값"]=defaultVariable["목표할인가"]*self.혜택가격모음["쿠폰할인값"][v]        
                            else:
                                    defaultVariable["쿠폰할인값"]=self.혜택가격모음["쿠폰할인값"][v]
                            break
            elif condition=="<<":
                    if leftNum<defaultVariable["목표할인가"]<rightNum:
                            if self.혜택가격모음["쿠폰할인값"][v]<=1:
                                    defaultVariable["쿠폰할인값"]=defaultVariable["목표할인가"]*self.혜택가격모음["쿠폰할인값"][v]        
                            else:
                                    defaultVariable["쿠폰할인값"]=self.혜택가격모음["쿠폰할인값"][v]
                            break
            elif condition=="<=<":
                    if leftNum<=defaultVariable["목표할인가"]<rightNum:
                            if self.혜택가격모음["쿠폰할인값"][v]<=1:
                                    defaultVariable["쿠폰할인값"]=defaultVariable["목표할인가"]*self.혜택가격모음["쿠폰할인값"][v]        
                            else:
                                    defaultVariable["쿠폰할인값"]=self.혜택가격모음["쿠폰할인값"][v]
                            break
            else:
                    defaultVariable["쿠폰할인값"]=0

        tk.Label(maincontents,text="쿠폰할인값 (원) : ").place(relx=0.05,rely=0.45)
        쿠폰할인값entry=tk.Entry(maincontents)
        쿠폰할인값entry.insert(0,defaultVariable["쿠폰할인값"])
        쿠폰할인값entry.config(state="readonly")
        쿠폰할인값entry.place(relx=0.6,rely=0.45)
        spaceBtwwidget_height=0.3/len(self.혜택가격모음["네이버포인트값"])
        widgets={}
        defaultVariable["option_widgets"]=widgets
        for dex,name in enumerate(self.혜택가격모음["네이버포인트값"]):
                tk.Label(maincontents,text=name,name=name).place(relx=0.05,rely=0.5+spaceBtwwidget_height*dex)
                widgets[name+"_percent"]=tk.Entry(maincontents,name=name+"_percent")
                widgets[name+"_percent"].insert(0,self.혜택가격모음["네이버포인트값"][name])
                widgets[name+"_percent"].config(validate="key",validatecommand=(maincontents.register(lambda x: x.isnumeric()),"%S")) # 
                widgets[name+"_percent"].place(relx=0.35,rely=0.5+spaceBtwwidget_height*dex,relwidth=0.15)
                widgets[name+"_percent"].bind("<KeyPress>",lambda event,purpose="옵션가",variable=목표할인가격entry,defaultVariable=defaultVariable:할인율calculator(event,purpose,variable,defaultVariable))
                widgets[name+"_price"]=tk.Entry(maincontents,name=name+"_price")
                widgets[name+"_price"].insert(0,self.혜택가격모음["네이버포인트값"][name]*defaultVariable["목표할인가"])
                widgets[name+"_price"].place(relx=0.6,rely=0.5+spaceBtwwidget_height*dex,relwidth=0.15)
                widgets[name+"_price"].config(state="readonly")
        tk.Label(maincontents,text="배송비").place(relx=0.05,rely=0.5+spaceBtwwidget_height*(dex+1))
        배송비entry=tk.Entry(maincontents)
        배송비entry.insert(0,일반배송비)
        배송비entry.config(state="readonly")
        배송비entry.place(relx=0.6,rely=0.5+spaceBtwwidget_height*(dex+1),relwidth=0.15)

        defaultVariable["스마트판매가"]=목표할인가+float(쿠폰할인값entry.get())+1000
        for name in self.혜택가격모음["네이버포인트값"]:
                defaultVariable["스마트판매가"]+=float(defaultVariable["option_widgets"][name+"_price"].get())
        스마트판매가entry.insert(0,defaultVariable["스마트판매가"])
        스마트판매가entry.config(state="readonly")
        할인율calculator("","","",defaultVariable) # 할인율 초기화를 위하여
        self.optionPriceWindow.config(menu=menubar)
        self.optionPriceWindow.update()
    def priceHistogram_handler(self,usage):
        """
        특징
        1. 히스토그램에 사용되는 price는 이상치 제거 알고리즘 z-score(threshold=1)이 사용됨.
        """
        def 가격히스토그램생성(전체가격,historgram_axis:plt):
            temp가격대=[]
            for price in re.findall("'{1}[\w\d,]*'{1}",전체가격):
                temp가격대.append(int(re.sub(",","",re.search("[\d,]+",price).group(0)))) # 휴 ... 힘들다 힘들어 ㅋ
            # 가격 이상치 제거
            mean=np.mean(temp가격대)
            std=np.sqrt(sum([(i-mean)**2 for i in temp가격대])/len(temp가격대))
            z_score=[np.abs((i-mean))/std for i in temp가격대]
            for dex,value in enumerate(z_score):
                if value>1.0:
                    temp가격대[dex]=0
            가격대=[]
            for value in temp가격대:
                if value!=0:
                    가격대.append(value)
            # 이상치 제거 완료
                    
            minpricedex=np.argmin(가격대)
            maxpricedex=np.argmax(가격대)
            minprice=가격대[minpricedex]
            maxprice=가격대[maxpricedex]
            divicdnum=np.arange(0,maxprice,(maxprice-minprice)//30)
            historgram_axis.set_xticks(ticks=divicdnum)
            historgram_axis.tick_params(axis="x",rotation=-90)
            print(divicdnum)
            numofpoint,xranges,_=historgram_axis.hist(가격대,divicdnum,ec="yellow")
            
        def 가격히스토그램지우고다시생성(historgram_axis:plt):
            historgram_axis.clear()
            plt.draw()
        # 제품코드=self.productdata.iloc[self.index].squeeze()["제품코드"]
        # data=self.smartsotre_crawling_data.query("제품코드==@제품코드").squeeze().copy()
        if self.queried_smartsotre_crawling_data["키워드"]:
            if usage=="create":
                가격히스토그램생성(self.queried_smartsotre_crawling_data["전체가격"],self.histogramaxis)
                self.histogramfigure.show()
            elif usage=="renew":
                가격히스토그램지우고다시생성(self.histogramaxis)
                가격히스토그램생성(self.queried_smartsotre_crawling_data["전체가격"],self.histogramaxis)
                self.histogramfigure.show()
        else:
            pass
            
    def gosiinform_handler(self,tkobj):
        self.고시정보=draw_고시정보(self.indexed_on_channel_data["고시정보"],self.indexed_on_channel_data["rank_title"]+" 의 고시정보",(2100,350),tkobj=tkobj)
        self.고시정보[0].update()
    
    def submit(self,framename:str,order:str="insert"):
        """
        framename: submit에서 lambda로 넘어오는 값. createinputframe에서 생성된 frame을 분류하기 위해 등장\n\n
        order: 'insert'가 default, 삭제명령은 "remove" , 수정명령은 "modify"\n
        modifiedDbinfo : order가 "modify"일때 수정할 데이터의 값들을 넣은 dict
        """
        def 제목규칙체크(name:str):
            """
            주의사항 1. 이름안에 단어 중복이 없어야 함. v
            주의사항 2. 혜택/수식 등 .. 문구 없어야 한다? x
            주의사항 3. 특수문자 없어야 한다 v
            주의사항 4. 너무 긴(32자) 이름은 안 된다. 상품명에 못 들어간 키워드는 태그로 넣어준다. v
            주의사항 5. 상품명 / 카테고리 / 브랜드|제조사 / 속성 등에서 상품과 관련 없는 정보가 포함되면 " 등장 랭킹 " 에 불이익 발생하니 주의. x
            주의사항 6. 어순이 자연스럽게 배치해야 추가 점수를 받는다. x
            주의사항 7. 상품명에 넣고 남은 몇 개의 키워드는 태그로 넣으면 된다. x
            이름만들기 전략 : 결합형 키워드 전략, 즉 띄어쓰기를 통해 많은 키워드가 결합되도록 하는 전략.\n
                - e.g) 소음방지패드->소음 방지 패드\n
            """
            result=main.check(name).as_dict()
            for word,index in result["words"].items():
                if name.count(word)>1:
                    messagebox.showwarning("상품 제목 에러",f"'{name} has duplicated word '{word}'")
                    return "duplication"
            if len(name)>32:
                messagebox.showwarning("상품명 에러",f"'{name}' has over length limited 32 spelling, the length : {len(name)}")
                return "Over length"
            if re.search("[!@#$%^&*()_+-=`~/?'\"/\;:[{}]<>,.]",name):
                messagebox.showwarning("상품명 에러","'{}' 안에 특수문자 '{}'".format(name,re.search("[!@#$%^&*()_+-=`~/?'\"/\;:[{}]<>,.]".group(0))))
                return "특수문자 포함"
            return None
        def 스마트스토어태그명규칙체크(tags:str):
            for tag in tags.split(","):
                if re.search(r"[!@#$%^&*\(\)-_=+-:;'\"\?/\\]",tag):
                    messagebox.showwarning("태그명 에러",f"'{tag}' 안에 특수문자가 있으니 제거해주세요.")
                    return "특수문자 포함"
                elif len(tag)>10:
                    messagebox.showwarning("상품명 에러",f"'{tag}' 가 글 10가 넘었습니다. 10개 이하로 줄여주세요, 현재 길이 : {len(tag)}")
                    return "Over length"
        pdtitle=re.sub("[\n]","",self.root_frame[framename]["widgets"]["producttitlearea"].get())
        if isinstance(제목규칙체크(pdtitle),str):
            return 0
        title설명란=re.sub("[\n]","",self.root_frame[framename]["widgets"]["producttitle_description_area"].get("1.0",tk.END))
        price=re.sub("[\n]","",self.root_frame[framename]["widgets"]["product_price"].get())
        tags=self.root_frame[framename]["widgets"]["product_tag"].get("1.0",tk.END)
        if isinstance(스마트스토어태그명규칙체크(tags),str) :
            return 0
        # 네이버 태그는 한 태그 이름이 10 자이하여야하고 영어는 30자임. --------------------

        # ------------------------------------------------------------------------------

        order=order.lower()
        if order=="modify": # main프레임에서 하는 건 다 insert라서 그 외는 그냥 다 Update라고 할.. 아근데 삭제도 있잖아
            try:
                # self.DB_checkedDatainfo 는 수정하기로 넘어온 기능이기때문에 수정할 db의 정보를 "수정하기" 함수쪽에서 만들어서 사용한 것임.
                
                self.cursor.execute("UPDATE 제품정보 SET 제목='{}',제목설명='{}',가격='{}',제품코드='{}',원상품명='{}' WHERE 제품코드='{}'".format(pdtitle,title설명란,price,self.DB_checkedDatainfo["제품코드"],self.DB_checkedDatainfo["원상품명"],self.DB_checkedDatainfo["제품코드"]))# self.product는 createinformation할때 생성한 녀석임
            except Exception as e:                    
                messagebox.showwarning("DB 입력 에러 ",f"{str(e)}")
                return 0
            self.DB_updateContents(self.pagemove_currentpage)
            self.root_frame[framename]["obj"].destroy()
            self.root_frame.pop(framename)
            self.DB.commit()
        elif order=="remove":
            pass
        elif order=="insert":
            try:
                # self.product : self.index, 즉 현재 타이틀링 중인 데이터의 인덱스를 가르키는 pd.Series 객체
                q=queryCreator({"제목":pdtitle,"제목설명":title설명란,"가격":price,"제품코드":self.indexed_on_channel_data["제품코드"],"원상품명":self.indexed_on_channel_data["rank_title"],"태그":tags},"insert")
                # self.cursor.execute("INSERT INTO 제품정보 (제목,제목설명,가격,제품코드,원상품명) VALUES ('{}','{}','{}','{}','{}')".format(pdtitle,title설명란,price,self.indexed_on_channel_data["제품코드"],self.indexed_on_channel_data["rank_title"]))# self.product는 createinformation할때 생성한 녀석임
                self.cursor.execute(f"INSERT INTO 제품정보 {q}")# self.product는 createinformation할때 생성한 녀석임
            except Exception as e:
                print(e)
                messagebox.showwarning("DB 입력 에러 ",f"{str(e)}")
                return 0
            print(self.cursor.execute("SELECT * FROM 제품정보").fetchall())
            self.root_frame[framename]["widgets"]["producttitlearea"].delete(0,"end")
            self.root_frame[framename]["widgets"]["producttitle_description_area"].delete("1.0","end")
            self.root_frame[framename]["widgets"]["product_price"].delete(0,"end")
            self.root_frame[framename]["widgets"]["product_tag"].delete("1.0","end")
            self.cursor.execute("SELECT * FROM 제품정보")
            self.numofdata=len(self.cursor.fetchall())
            self.maxpage=self.numofdata//self.numofshowdata+1
            self.movebtn_showcurrentpage.config(text=f"Page {self.pagemove_currentpage}/{self.maxpage}")
            # 이게 아랫 것보다 먼저 나와야함. 아랫걸 실행하면 현재 update가 자동으로 다음걸로 넘어가서 정보가 사라지기 때문임 ------------------

            # ------------------
            if "check_box" in self.옵션정보.keys():
                
                chekbox_Interpreter(self.옵션정보["table_info"],self.옵션정보["check_box"]).to_csv(os.path.join(os.path.dirname(__file__,"상품별가격_상품의타이틀로 저장됨"),self.indexed_on_channel_data["rank_title"]+"_등록할옵션정보.csv"),index=False,encoding="UTF-8-SIG")
            else:
                
                table_infoInterpreter(os.path.join(os.path.dirname(__file__,"상품별가격_상품의타이틀로 저장됨"),self.indexed_on_channel_data["rank_title"]+"_등록할옵션정보.csv"),self.옵션정보["table_info"])

            self.DB.commit() # DB에 먼저 적용한 다음에 self.index로 변화 시키기
            dbtoDataframe(self.cursor,"제품정보").to_csv("(제목생성기통과)등록할제품.csv",index=False,encoding="UTF-8-sig")
            self.root_MoveData()
            self.DB_updateContents(self.pagemove_currentpage)
            self.update_기타window(고시정보tkobj=self.고시정보[0],옵션정보tkobj=self.옵션정보["root"])
            self.finalInitialization()
            
            
    def root_MoveData(self,initial=False):
        """
        역할\n
            1. 업데이트할 데이터 변경\n
                - 현재 보이는 사진과 정보를 변경하는 알고리즘\n
        """
        # MoveData to Next data
        if not initial:
            while True:
                self.index=self.getIndex_notInDb(self.cursor,self.DBtableName,self.on_channel_data,"제품코드")
                # self.index+=1 # 2024-03-05 위에getIndex의 등장으로 더 이상 이렇게 사용하지 않게 됨. !매우 중요한 변수.. 다른 create~함수 실행되기 전 가장 먼저 실행되어야함. 이 녀석을 통해 다른 create 함수들이 새로 변경할 정보를 가져오기 때문임.
                self.indexed_on_channel_data=self.on_channel_data.iloc[self.index].squeeze()
                self.queried_smartsotre_crawling_data=self.smartsotre_crawling_data.query('제품코드=="{}"'.format(self.indexed_on_channel_data['제품코드']))
                if self.queried_smartsotre_crawling_data.shape[0]>1:
                    messagebox.showwarning("스마트스토어 제품코드 unique 위배 에러",f"제품코드 '{self.indexed_on_channel_data['제품코드']}' 가 스마트스토어 크롤링 파일에 두개 이상이 있습니다.")
                    continue
                self.queried_smartsotre_crawling_data=self.queried_smartsotre_crawling_data.squeeze()
                break
        # ----------------------------
        picturepath=os.path.join(root_path상품이미지,self.indexed_on_channel_data["rank_title"])
        대표사진들=[]
        for picture_name in os.listdir(picturepath):
            if re.search("대표사진",picture_name):
                대표사진들.append(picture_name)
        self.createimageframe([os.path.join(picturepath,대표사진) for 대표사진 in 대표사진들]) # 여기에다가 대표사진 list만 넣어주면 ㅇㅋ, 그리고 나중에 키의 좌우만 누르면 사진이 알아서 바 뀔꺼임.
        self.createInformationframe()
    def DB_pagemove(self,event):
            page_text=self.movebtn_pagemove.get()
            r=re.search("[\d]+",page_text)
            if r:
                try:
                    page=int(r.group())
                except:
                    messagebox.showwarning("Error",f"'{r.group()}' 은 잘못된 페이지 번호입니다")
                    return 0
                
                # movebtn_pagemove.delete(1.0,tk.END) # Entry는 이렇게 안함. ㅣ건 Text에서 먹히는거임
                if page>self.maxpage: # +1은 해준 이유는 정확히 40이면 이게 맞지만 45이면 나머지 5개를 표현하기 위해 총 3개 페이지가 나오기 때문에 3페이지 까지 허용임
                    messagebox.showwarning("Error",f"Page No '{page}' has over of total page '{self.numofdata//self.numofshowdata+1}'")
                    self.movebtn_pagemove.delete(0,"end")
                    return 0
                elif page<1 or self.pagemove_currentpage==page: # 페이지 음수이거나 현재 페이지랑 같은 건 걍 무시하자
                    self.movebtn_pagemove.delete(0,"end")
                    return 0
                else:
                    self.pagemove_currentpage=page
                    self.movebtn_showcurrentpage.config(text=f"Page {page}/{self.maxpage}")
                    self.DB_updateContents(page)
                self.movebtn_pagemove.delete(0,tk.END)
    def DB_updateContents(self,page):
            self.pagemove_currentpage=page
            self.cursor.execute("SELECT * FROM 제품정보")
            showcontents=self.cursor.fetchall()[(self.pagemove_currentpage-1)*self.numofshowdata-1 if page>1 else 0:(self.pagemove_currentpage-1)*self.numofshowdata+self.numofshowdata-1]
            if self.contents_grid_box:
                for dex in self.contents_grid_box:
                    for grid in self.contents_grid_box[dex]:
                        grid.destroy()
  
            for i,v in enumerate(showcontents):
                checkbox=tk.Checkbutton(self.contents_frame,name=f"checkbtn {i}",command=lambda btndex=i: self.DB_checkbtn_option(btndex))
                self.contents_grid_box[i]=[checkbox]
                checkbox.grid(row=i,column=0)
                for j in range(self.numoffeature):
                    btn=tk.Button(self.contents_frame,text=v[j],width=8,name=f"content {i},{j}")
                    self.contents_grid_box[i].append(btn)
                    btn.grid(row=i,column=j+1) # name지정해도 안 변함  grid처리 해줘야함.
                # if self.numofshowdata-len(showcontents)>0:
                #     for v in self.contents_grid_box[len(showcontents)*self.numoffeature:]:
                #         v.config(text="")
    def DB_checkbtn_option(self,index):
        def 수정하기():
            # self.root_frame={"tk_root":tk.Tk()}
            # self.root_frame["tk_root"].geometry("{}x{}".format(800,800))
            # self.root_frame["tk_root"].update() # geomery 값들을 얻으려면적용하려면 이게 필수네 ..
            if "subframe" in self.root_frame:
                self.root_frame["subframe"]["obj"].destroy()
            option_window.destroy()
            수정하기window=tk.Toplevel(name="subframe",bg="#595150")
            수정하기window.geometry(f"{self.cellwidth}x{self.cellheight}")
            self.root_frame["subframe"]={"obj":수정하기window,"widgets":{}}
            self.root_frame["subframe"]["widgets"]=self.createinputframe(수정하기window,"subframe","modify")
        def 삭제하기():
            que_sel="SELECT * FROM 제품정보 WHERE 제품코드='{}' AND 원상품명='{}'".format(self.DB_checkedDatainfo["제품코드"],self.DB_checkedDatainfo["원상품명"])
            self.cursor.execute(que_sel)
            if len(self.cursor.fetchall())==1:
                que="DELETE FROM 제품정보 WHERE 제품코드='{}' AND 원상품명='{}'".format(self.DB_checkedDatainfo["제품코드"],self.DB_checkedDatainfo["원상품명"])
                self.cursor.execute(que)
            else:
                messagebox.showinfo("중복 제품코드 발생,!","현재 선택한 삭제 내용이 DB에 중복된 제품코드와 내용입니다")
            self.DB_updateContents(self.pagemove_currentpage)
            option_window.destroy()
            self.DB.commit()
        option_window=tk.Toplevel()
        option_window.geometry("200x100")
        # self.DB_checkedDatainfo={colname:dbinfo.cget("text") for colname,dbinfo in zip(self.dbcolumnName,self.contents_grid_box[index][1:])} # [1:] 은 인덱스 0 은 checkbutton 객체인데, 이 객체에는 text가 없기 때문이다
        
        self.DB_checkedDatainfo={colname:dbinfo.cget("text") for colname,dbinfo in zip(self.dbcolumnName,self.contents_grid_box[index][1:])} # [1:] 은 인덱스 0 은 checkbutton 객체인데, 이 객체에는 text가 없기 때문이다
        수정버튼=tk.Button(option_window,text="수정하기",command=수정하기)
        수정버튼.place(relx=0.2,rely=0.2,relwidth=0.2,relheight=0.2)
        삭제버튼=tk.Button(option_window,text="삭제하기",command=삭제하기)
        삭제버튼.place(relx=0.4,rely=0.2,relwidth=0.2,relheight=0.2)
    def frameNavigator(self,frameName:str):
        if re.search("['~./\\\!@#$%^&*,\(\)\[\]]",frameName):
            return "오직 특수문자 '-' 만 사용가능합니다."
        frame_heritance=self.root_frame_name.split("-")
        heritance_frames=[]
        parent_frame=self.root_frame["tk_root"]
        for framename in frame_heritance:
            parent_frame=parent_frame[framename]
            heritance_frames.append(parent_frame.copy())
        return heritance_frames.copy()
    def mouseOnframe(self,event):
        # print("on --------------------")
        # print(self.root_frame)
        # print(self.root_frame[event.widget._name])
        self.root_frame[event.widget._name]["obj"].config(highlightthickness=5,highlightbackground="black")
        # self.current_pagename=
        # print(dir(event.widget._name))
    def mouseOffframe(self,event):
        # print("off --------------------")
        # print(event.widget.name)
        self.root_frame[event.widget._name]["obj"].config(highlightthickness=0)
        # print(dir(event.widget._name))
    
    
    
    def changepicture(self,imageindex:int):
        if imageindex>self.total_images or imageindex<0:
            return 0
        self.imageindex=imageindex
        original_img=Image.open(self.picturebox[imageindex]) # PIL로 읽으면
        original_img=original_img.resize((int(self.root_frame[self.pictureframename]["obj"].place_info()["width"]),int(self.root_frame[self.pictureframename]["obj"].place_info()["height"])))
        self.img=ImageTk.PhotoImage(original_img) # 이유는 모르겠지만 네.. ImageTk는 self 로 해야 접근 이 되나 보네요
        # self.root_frame[frame]["widgets"]["lab1"]=tk.Label(self.root_frame[frame]["obj"],image=img,name="lab1")
        self.picturedescription=tk.Label(self.root_frame[self.pictureframename]["obj"],text="({} / {})".format(self.imageindex+1,self.total_images+1),anchor="se",bg="red",name="picturedescription")
        self.picturedescription.pack(side="bottom",fill=None)
        lab=tk.Label(self.root_frame[self.pictureframename]["obj"],image=self.img,name="lab1") # name이 중요하네요,
        lab.pack()
    def keypress(self,event):
        key=event.keysym
        
        if key=="Right":
            print(key)
            self.changepicture(self.imageindex+1)
            # self.root_frame[self.pictureframename]
        elif key=="Left":
            print(key)
            self.changepicture(self.imageindex-1)
    def frameConstructor(self,root_frame_name:str,numOfframe:int,tkframeData:dict):
        """
        frame은 .place()로 배치된 것이 precondition.\n
        root_frame_name : frameDatabase의 key 값. frameDatabase의 자세한 것은 설명서 참고\n
        frameStructure : .Frame 객체의 inheritance를 저장한 데이터. 
        """
        if re.search("['~./\\\!@#$%^&*,\(\)\[\]]",root_frame_name):
            return "오직 특수문자 '-' 만 사용가능합니다."
        
        if not isinstance(self.root_frame["tk_root"],tk.Tk):
            # frame_heritance=root_frame_name.split("-")
            # heritance_frames=[]
            # parent_frame=self.root_frame["tk_root"]
            # for framename in frame_heritance:
            #     parent_frame=parent_frame[framename]
            #     heritance_frames.append(parent_frame.copy())
            # 어차피 여기까진 안 쓸 것 같아서 .. 수정이 정말 필요하긴 한데, 그냥 안하고 pass
            heritance_frames=self.frameNavigator(root_frame_name)
            parent_frame_info=heritance_frames[-1].place_info()
            parent_frame.destroy() # 어차피 이때 만들 당시엔 이 프레임 하위에 아무것도 없겠지만 메모리 낭비 생길까봐 없애기

            parent_frame={"obj":tk.Frame(heritance_frames[-2]["obj"])}
            parent_frame["obj"].place(x=int(parent_frame_info["x"]),y=int(parent_frame_info["y"]),width=int(parent_frame_info["width"]),height=int(parent_frame_info["height"]))

            framewidth,frameheight=int(parent_frame_info["width"]),int(parent_frame_info["height"])
            
            cellwidth,cellheight=framewidth//numOfframe,frameheight//numOfframe
            numOfFrameRow,numOfFrameCol=framewidth//cellwidth,frameheight//cellheight
            # background_rand=["#ff4dff","#3385ff","#4dff4d","#ff8c1a","#99bbff"]
            background_rand=['white']
            cursur_rand=["based_arrow_down","based_arrow_up","boat","bogosity", "bottom_left_corner", "bottom_right_corner", "bottom_side","bottom_tee","box_spiral","center_ptr","circle","clock"]
            for col_index in range(numOfFrameCol):
                for row_index in range(numOfFrameRow): # 행 기준으로 1번 2번 이 되기 때문에 행 이 다 끝나고 열이 실행되어야 함.
                    framename=self.root_frame_name+"-{}".format(numOfFrameRow*row_index+col_index)
                    bgrand=random.choice(background_rand)
                    currand=random.choice(cursur_rand)
                    parent_frame[framename]=tk.Frame(parent_frame["obj"],bg=bgrand,cursor=currand)
                    parent_frame[framename].place(x=cellwidth*row_index+parent_frame_info["x"],y=cellheight*col_index+parent_frame_info["y"],width=cellwidth,height=cellheight) # 좌표는 x= "부모 frame의 x,y위치"+frame의넓이*index순서" , y도 같은 개념
                    # 완성인듯 ??
        else:
            parent_frame_info={"width":tkframeData["tk_root"].winfo_width(),"height":tkframeData["tk_root"].winfo_height()}
            tkframeData["tk_root"].destroy()
            tkframeData={"obj":tk.Tk()}
            tkframeData["obj"].geometry("{}x{}".format(parent_frame_info["width"],parent_frame_info["height"]))
            tkframeData["obj"].bind("<KeyPress>",self.keypress)

            framewidth,frameheight=int(parent_frame_info["width"]),int(parent_frame_info["height"])
            print(parent_frame_info)
            # 배치 알고리즘 , 우선 sqrt씌움, 자연수부분만 가져옴. 만약 3.001 값이나와도 자연수부분 +1 해서 4를하고. 이렇게해서 가로 4 세로 4의 Frame을 만들 것임
            if math.sqrt(numOfframe)>float(math.trunc(math.sqrt(numOfframe)))+.000001: # .000001에는 아무 의미 없음, 그냥 2.0 > 2.000001 인 경우를 분류하려고 만 듦
                numberofFramebox=math.trunc(math.sqrt(numOfframe))+1 # root2 씌워서 해당 값들의 1/2배 를 가져오고 거기 정수에서 만약 0.6 나오면 0을가져오고 +1해서 가로/세로1개의 프레임을 만드는 것임 만약 2.6이면 3이 되서 3x3 Frame 만드는 거임
            else:
                numberofFramebox=math.trunc(math.sqrt(numOfframe))

            self.cellwidth,self.cellheight=framewidth//numberofFramebox,frameheight//numberofFramebox
            numOfFrameRow,numOfFrameCol=framewidth//self.cellwidth,frameheight//self.cellheight # 이건 있으면 안 됨, 이렇게 사용하면 가로 세로 box개수 맞추기가 더 어려움
            frameratio=1.0/numOfframe
            background_rand=["#ff4dff","#3385ff","#4dff4d","#ff8c1a","#99bbff"]
            background_rand=["white"]
            cursur_rand=["based_arrow_down","based_arrow_up","boat","bogosity", "bottom_left_corner", "bottom_right_corner", "bottom_side","bottom_tee","box_spiral","center_ptr","circle","clock"]
            for boxnumber in range(numOfframe):
                framename="frame{}".format(boxnumber)
                bgrand=random.choice(background_rand)
                currand=random.choice(cursur_rand)
                tkframeData[framename]={"obj":tk.Frame(tkframeData['obj'],bg="#595150",cursor=currand,name=framename),"widgets":{}}
                tkframeData[framename]["obj"].place(x=(boxnumber%(numberofFramebox))*self.cellwidth,y=(boxnumber//(numberofFramebox))*self.cellheight,width=self.cellwidth,height=self.cellheight)
                tkframeData[framename]["obj"].bind("<Enter>",self.mouseOnframe)
                tkframeData[framename]["obj"].bind("<Leave>",self.mouseOffframe)

            self.root_frame=tkframeData.copy()
            return self.root_frame

    def start(self):
        self.root_frame["obj"].mainloop()



if __name__=="__main__":
    root_path상품이미지=os.path.join(os.path.dirname(__file__),"상품이미지")
    oo=temp(datapath=os.path.join(os.path.dirname(__file__),"등록할제품.csv"),
            smartsotre_csvpath=os.path.join(os.path.dirname(__file__),"스마트스토어크롤링결과_0.csv")
            ,pictureframename="frame1",informframename="frame0",inputframename="frame2",dbframename="frame3")
                        
    oo.start()
