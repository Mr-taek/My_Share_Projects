from .all_libraries import *

def queryCreator(keyAndvalue:dict|tuple,order:str):
    """
    sql문을 사용할 때 항상 어떤 format의 형태로 pass해야 한다.

    - keyAndvalue의 형태
        1. dict형태 : {colname:string|int|...} : INSERT 전용. COLNAME1='string' , COLNAME1=int 형태로 query생성
        
        2. tuple형태 : (colname,value) : 보통 CREATE 전용. 아직 미구현
    - order의 종류
        1. "insert" : insert의 형식으로 값을 최종 리턴 , self.cursor.execute("INSERT INTO 온채널_모니터링DB (제품코드,내용,날짜,코멘트내용,수정반영) VALUES ('{}','{}','{}','{}',0)".format(제품코드,내용,날짜,코멘트내용))
    - return 종류
        1. order="insert" , "(colname1,colnam2,...) VALUES (VALUE1,VALUE2,...)"
    """

    if isinstance(keyAndvalue,dict):
        order=order.lower()
        if order=="insert":
            v="("
            for colname in keyAndvalue:
                v+=str(colname)+","
            v=v[:-1]+") VALUES ("
            for colname in keyAndvalue:
                v+=f"'{keyAndvalue[colname]}',"
            v=v[:-1]+")"
            return v
def dbtoDataframe(cursor:sql.Cursor,dbname:str,query:str=None)->pd.DataFrame:
    if query:
        cursor.execute(query)
    else:
        cursor.execute(f"SELECT * FROM {dbname}")
    colnames=[col[0] for col in cursor.description]
    data=cursor.fetchall()
    return pd.DataFrame(data,columns=colnames)