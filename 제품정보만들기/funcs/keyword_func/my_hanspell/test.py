from collections import namedtuple
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),"funcs" ))
from keyword_func.my_hanspell.main import check
_checked = namedtuple('Checked',
    ['result', 'original'])

class kbs(_checked):
    def __new__(cls,result="",original=0):
        obj=super().__new__(cls,result,original)
        return obj
    def printing(self):
        print(self.result,self.original)
        

# c=kbs(result="아니다다를까")
k=check("안녕하세요 저는 이미리 입니다")
print(k)