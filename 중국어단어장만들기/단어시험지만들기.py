import os,pinyin,random
import re
import pandas as pd
import sqlite3 as sql
def insert(dbname:str,cursor,data):
    """
    data : queried data by 단어
    """
    strs="INSERT INTO {} (".format(dbname)
    values="VALUES ("
    for key in data.columns:
        strs+=key+"," # ,을 굳이 안 앲어도 되었음
        v=data[key].iloc[0]
        
        if isinstance(v,str):
            v="'"+v+"'" # 여기서 넘어온 데이터는 따옴표가 없어서 직접 지정해줘야함.
        else:
            v="'"+str(v)+"'"
        values+=v+","
    strs=strs[:-1]
    values=values[:-1]
    strs+=")"
    values+=");"
    print(strs+" "+values)
    cursor.execute(strs+" "+values)

def saveOndb(conn:sql.connect,cursor:sql.Cursor):
    data=pd.read_excel(중국어단어지)
    for word in data["단어"].unique():
        dd=data.query(f"단어==@word")
        cursor.execute(f"SELECT * FROM chinesewords WHERE 단어='{word}'")
        isthere=cursor.fetchall()
        if not isthere and dd.shape[0]>0:
            insert("chinesewords",cursor,dd)
        # else:
        #     print(word," is exist")
        # print(isthere)
    conn.commit()
def makeTestBook(cursor:sql.Cursor,dbname,difficulty:int=1):
    """
    difficulty : 난이도 ,1은 쉬움모드 2는 어려움 모드
    """
    def dbtodataframe(cur,dbname):
        cur.execute(f"SELECT * FROM {dbname}")
        colnames=[col[0] for col in cur.description]
        data=cur.fetchall()
        data=pd.DataFrame(data,columns=colnames)
        import numpy as np
        
        data=data.iloc[np.random.choice(range(data.shape[0]),[총문제개수 if data.shape[0]>(총문제개수-1) else data.shape[0]-1][0],False)]
        data.reset_index(inplace=True,drop=True)        
        numoftextphrase=[]
        for colname in data.columns:
            if re.search("예문",colname):
                numoftextphrase.append(colname)
        phrasedf=data[numoftextphrase].copy()
        numofindex=phrasedf.shape[0]
        concatingdf=pd.DataFrame(index=range(numofindex),columns=[colname+"_pinyin" for colname in phrasedf.columns])
        for colname in phrasedf.columns:
            for i in range(numofindex):
                if phrasedf[colname].iloc[i]!="nan": # nan 값이 아닐 경우
                   concatingdf[colname+"_pinyin"].iloc[i]=pinyin.get(phrasedf[colname].iloc[i],delimiter="")
        return (pd.concat([data,concatingdf],axis=1),numoftextphrase)
    총문제개수 = 28
    출제지,예문list=dbtodataframe(cursor,dbname)
    if difficulty==1:
        시험지=pd.DataFrame(index=range(출제지.shape[0]),columns=["단어","뜻","발음","예문","예문발음"])
        정답지=pd.DataFrame(index=range(출제지.shape[0]),columns=["단어","뜻","발음","예문","예문발음"])
    else:
        시험지=pd.DataFrame(index=range(출제지.shape[0]),columns=["발음","단어","뜻","예문발음","예문"])
        정답지=pd.DataFrame(index=range(출제지.shape[0]),columns=["발음","단어","뜻","예문발음","예문"])
    
    for i in range(출제지.shape[0]):
        try:
            d=출제지.iloc[i].T
            사용가능한예문=[]
            for examphrase in 예문list:
                if d[examphrase]!="nan" or d[examphrase]!=None:
                    사용가능한예문.append(examphrase)
            if 사용가능한예문:
                예문=random.choice(사용가능한예문)
                넣을예문 = d[예문]
                넣을예문발음 = d[예문+"_pinyin"]
            else:
                넣을예문 = "没有 题"
                넣을예문발음 = "没有 题"
            if difficulty==1:
                시험지["단어"].iloc[i]=d["단어"]
                시험지["예문"].iloc[i]=넣을예문
            else:
                시험지["발음"].iloc[i]=pinyin.get(d["단어"],delimiter="")
                시험지["예문발음"].iloc[i]=pinyin.get(넣을예문)
            정답지["단어"].iloc[i]=d["단어"]
            정답지["뜻"].iloc[i]=d["뜻"]
            정답지["발음"].iloc[i]=pinyin.get(d["단어"],delimiter=" ")
            정답지["예문"].iloc[i]=넣을예문
            정답지["예문발음"].iloc[i]=넣을예문발음
        except Exception as e:
            with open("./errorcase.txt","wt") as txt:
                    """
                    예문이 아예 없으면 에러가 남.
                    """
                    txt.write(str(e))
                    print(d)
        # 시험지[예문+"_pinyin"]=d[예문] # 이건 있으면 안 됨. 예문을 직접 쓰게 해야지.
    시험지.fillna("",inplace=True)
    시험지.to_csv(os.path.join(os.path.dirname(__file__),"(시험지)중국어단어지.csv"),index=False,encoding='utf-8-sig')
    정답지.fillna("",inplace=True)
    
    정답지.to_csv(os.path.join(os.path.dirname(__file__),"(정답지)중국어단어지.csv"),index=False,encoding='utf-8-sig')


conn=sql.connect(os.path.join(os.path.dirname(__file__),"chinese_words_db.db"))
cur=conn.cursor()
# 테이블이 있으면 삭제 
cur.execute("DROP TABLE IF EXISTS chinesewords")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
if "chinesewords" not in [table[0] for table in cur.fetchall()]:
    cur.execute("CREATE TABLE chinesewords (단어 TEXT PRIMARY KEY,뜻 TEXT, 발음 TEXT, 예문1 TEXT,예문2 TEXT,예문3 TEXT,출처 TEXT,유사단어 TEXT)") # primary key는 없앰. 왜냐면 중국어 한 단어에서 뜻이 여러개 이기 때문임. 나중에 같은 단어인데 다른 뜻이 나오면 db에 저장오류가 뜨기때문에 삭제!

# cur.execute("CREATE TABLE chinesewords (단어 TEXT,뜻 TEXT, 발음 TEXT, 예문1 TEXT,예문2 TEXT,예문3 TEXT)")
# cur.execute(f"SELECT * FROM chinesewords WHERE 단어='光滑'")
# isthere=cur.fetchall()
# print(isthere)

if __name__=="__main__":
    instruction="""
    1 : save 중국어단어지.xlsx to db
    2 : making 중국어시험지 from chinese_words_db.db
    3 : first let 1 word and let 2
    """
    중국어단어지=os.path.join(os.path.dirname(__file__),"중국어단어지.xlsx")
    typeoffunc=input(instruction)
    difficulty=2 # 1은 단어를 시험으로, 2는 pinyin으로 시험지 만듦.
    while True:
        if typeoffunc=="1":
            saveOndb(conn,cur)
        elif typeoffunc=="2":
            makeTestBook(cur,"chinesewords",difficulty)
        elif typeoffunc=="3":
            saveOndb(conn,cur)
            makeTestBook(cur,"chinesewords",difficulty)
        else:
            continue
        break

