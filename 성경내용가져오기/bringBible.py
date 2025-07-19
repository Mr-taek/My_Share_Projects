import json
from bs4 import BeautifulSoup as bea
import requests
try:
    with open("찬송가경로.json","r",encoding="UTF-8-SIG") as f:
        target_j=json.load(f)
    성경맵핑={'창세기': 'gen', '출애굽기': 'exo', '레위기': 'lev', '민수기': 'num', '신명기': 'deu', '여호수아': 'jos', '사사기': 'jdg', '룻기': 'rut', 
                    '사무엘상': '1sa', '사무엘하': '2sa', '열왕기상': '1ki', '열왕기하': '2ki', '역대상': '1ch', '역대하': '2ch', '에스라': 'ezr', '느헤미야': 'neh', 
                    '에스더': 'est', '욥기': 'job', '시편': 'psa', '잠언': 'pro', '전도서': 'ecc', '아가': 'sng', '이사야': 'isa', '예레미야': 'jer', '예레 미야애가': 'lam', 
                    '에스겔': 'ezk', '다니엘': 'dan', '호세아': 'hos', '요엘': 'jol', '아모스': 'amo', '오바댜': 'oba', '요나': 'jnh', '미가': 'mic', '나훔': 'nam', '하박국': 'hab', 
                    '스바냐': 'zep', '학개': 'hag', '스가랴': 'zec', '말라기': 'mal', '마태복음': 'mat', '마가복음': 'mrk', '누가복음': 'luk', '요한복음': 'jhn', '사도행전': 'act', 
                    '로마서': 'rom', '고린도전서': '1co', '고린도후서': '2co', '갈라디아서': 'gal', '에베소서': 'eph', '빌립보서': 'php', '골로새서': 'col', '데살로니가전서': '1th', 
                    '데살로니가후서': '2th', '디모데전서': '1ti', '디모데후서': '2ti', '디도서': 'tit', '빌레몬서': 'phm', '히브리서': 'heb', '야고보서': 'jas', '베드로전서': '1pe', 
                    '베드로후서': '2pe', '요한1서': '1jn', '요한2서': '2jn', '요한3서': '3jn', '유다서': 'jud', '요한계시록': 'rev'}
    성경구절={}
    for 성경구 in target_j["성경구절"]:
        편=성경구[0]
        몇장=성경구[1]
        몇절=성경구[2]
        # print(편,몇장,몇절)
        # print(편,type(몇장),type(몇절))
        
        query=f"https://www.bskorea.or.kr/bible/korbibReadpage.php?version=GAE&book={성경맵핑[편]}&chap={몇장}&sec={몇절}#focus"
        
        # myhtml=open("myhtml.txt","r",encoding="UTF-8")
        # soup=bea(myhtml,"html.parser")
        # myhtml.close()
        # soup=bea(myhtml,"html.parser")
        # with open("myhtml.txt","w",encoding="UTF-8") as f:
        #     f.write(req.get(query,verify=False).text)
        req=requests.Session()
        soup=bea(req.get(query,verify=False).text,"html.parser")

        
        if soup.find("div",{"class":"bible_read"}).find_all("span"):
            성경구절[편]={}
            for line in soup.find("div",{"class":"bible_read"}).find_all("span"): # recursive False하면 그 아래에 같은 이름의 태그들은 포함하지 않음.
                # re.sub()
                # [몇절]=
                # 내용=line.text.split("\xa0\xa0\xa0") # 하다보니 저렇게 띄어쓰더라고 .. 그래서 이걸로 분류하니 잘 됨.
                내용=line.text.replace("\xa0\xa0\xa0","")
                
                # 내용=re.sub("\n\s","",내용)
                
                성경구절[편][몇절]=내용
                몇절+=1

    for 편 in 성경구절:
        print(f"============= {편} =============")
        for i in 성경구절[편]:
            print(f"{i} : {성경구절[편][i]}")

    input("대기중 ...")
except Exception as e:
    print(e)
    input("error occur ....")