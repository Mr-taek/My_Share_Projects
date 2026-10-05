from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,QPushButton,
    QScrollArea,QVBoxLayout,QLabel,QMessageBox,QHBoxLayout,QGroupBox,QLineEdit
)
from PySide6.QtGui import (QIntValidator)

from PySide6.QtCore import Qt
import json
from escpos.printer import Serial
import datetime,sys,os,re
stockFilePath = os.path.join("stock.json")
orderFolder = os.path.join("주문일자")
errorlog = open("errorLogSotkcManage.txt","wt")
if not os.path.exists(stockFilePath):
  abc = open(stockFilePath,"w")
  abc.write("{\n}")
  abc.close()
  
with open(stockFilePath,"rb") as f:
  stockFile = json.load(f)
def writeErrorlog(내용):
  nowTime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
  내용 = "{} _ {}\n".format(nowTime,내용)
  errorlog.write(내용)

# class stockManagement(QMainWindow):
class stockManagement(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("ScrollArea 테스트")
    self.setGeometry(100, 100, 1080, 600)
    # left_top_widget.setLayout(grid)
    # left_top_widget.setMinimumSize(350, 400)
    self.area = QScrollArea()
    self.area.setWidgetResizable(True)
    self.canWidget = QWidget()
    self.canLayout = QVBoxLayout()
    
    for metarialCate in stockFile:
      self.makeStockBar(metarialCate)
    
    self.canWidget.setLayout(self.canLayout)
    self.area.setWidget(self.canWidget)
    # self.setCentralWidget(self.area) # 더이상 QMainWindow가 아니라서 주석처리
    window = QVBoxLayout()
    window.addWidget(self.area)
    self.setLayout(window)
    self.stockBarSaveBox = []
  def makeStockBar(self,stockTarget,reload=False):
    """
    stockTarget : stock.json 에서 가져온. "염소고기": [{ "입고날자":_기입하는 날자에 대한 년월일 시분초_, "입고량":_기입내용_, "단위":"그램"}, ... ] 형태에서
    "염소고기" key 값이 넘어옴. key를 넘서 해당 내용에 대해서 변경시키는 것이 순서에 맞기 때문임
    reload : reload 시 이미 초기화작업이 넘어갔기에 ui에 특정 자리에 남은 내용들만 다시 만들어 주는 작업
    """
    def clearLayout(layout):
      if layout is not None:
          while layout.count():
              item = layout.takeAt(0)
              widget = item.widget()
              child_layout = item.layout()
              if widget is not None:
                  widget.deleteLater()  # 위젯 제거
              elif child_layout is not None:
                  clearLayout(child_layout)  # 하위 레이아웃 재귀적으로 비우기
                  child_layout.deleteLater()
    try : 
      if stockTarget in stockFile:
        stock = stockFile[stockTarget]
        총입고량 = 0 # 그램
        총개수_인분 = 0 # 개수 , 인분
        errorOccur = False
        errorContext = ""
        표시단위 = "-"
        # for stock in stocks:
        입고일 = stock["입고날자"]
        입고량 = stock["입고량"]
        단위개수 = float(stock["단위개수"])
        단위 = stock["단위"]
        총개수_인분 += int(입고량)
        # 원래는 그램수 입력해서 이것저것 하려고 했는데, 그냥 그램수 들어오면 저게 몇 인분인지는 알아서 적게하고
        # 간단하게 새로 들어오면 숫자만 바꾸게 하도록 하기로 함
        if 단위 =="인분":
          # 총입고량 +=round(float(입고량),2)
          # 총개수_인분 += int(float(입고량) / 단위개수) # 100 gram 단위로 인분을 나누기 때문
          표시단위 = "인분"
        elif 단위 =="킬로그램":
          # 총입고량 +=round(float(입고량)*1000,2) # 킬로그램 단위로 입고가 되면 일단 그램으로 변환해야함
          # 총개수_인분 += int(float(입고량)*1000 / 단위개수) # 100 gran 단위로 인분을 나누기 때문
          표시단위 = "인분"
        elif 단위 == "개":
          # 총개수_인분 += int(입고량)
          표시단위 = "개"
        else:
          errorOccur=True
          errorContext = f"internalError, 단위 '{stockTarget}'의 단위 : '{단위}'는 if문에 없는 case입니다. 내용을 수정해주세요"
            # break
        if errorOccur:
          writeErrorlog(errorContext)
        else:
          box = None
          boxPosition = None
          if reload:
            for i in range(self.canLayout.count()):
                widget = self.canLayout.itemAt(i).widget()
                if widget and widget.objectName() == stockTarget:
                  boxPosition = i
                  widget.setLayout(None)
                  widget.deleteLater()# 이렇게 해야 결국에는 되는구만.
                  break
          # else:
          box = QGroupBox()
          box.setObjectName(stockTarget) # box가 모든 내용을 담고있음. 그리고 self.canLayout에서도 box를 추가했기에 이걸로 reload하면 될 듯. stockTarget 은 재료 이름이니 일관성을 위해서 지정
          stockBar = QVBoxLayout()
          firstRow = QHBoxLayout()
          label = QLabel("재료 : {}\t\t 남은 재고 : {} {}".format(stockTarget,총개수_인분,표시단위))
          label.setStyleSheet("font-size: 25px;")
          # label.setAlignment(Qt.AlignCenter)
          firstRow.addWidget(label)
          firstRow.addStretch()
          secondRow = QHBoxLayout()
          # addStockbtn = QPushButton("추가하기") # 굳이 추가 말고 수정만 하면 될듯
          editStockbtn = QPushButton("추가하기")
          editStockbtn.clicked.connect(lambda _,reload=reload : self._editNumofStock(stockBar,stockTarget))
          editStockbtn.setStyleSheet("font-size: 16px;")
          # secondRow.addWidget(addStockbtn)
          secondRow.addWidget(editStockbtn)
          stockBar.addLayout(firstRow)
          stockBar.addLayout(secondRow)
          box.setLayout(stockBar)
          if reload:
            # 이렇게하니 성공이구만.
            self.canLayout.insertWidget(boxPosition,box)
          else:
            self.canLayout.addWidget(box)

      else:
        writeErrorlog(f"internalError, '{stockTarget}'은 stock.json에 없는 재고 이름입니다")
    except Exception as e:
       writeErrorlog(f"에러 발생\n{e}")
  def _editNumofStock(self,targetLatyout,targetCategory):
    """
    targetLatyout : 수정하기 버튼을 누르면 해당 레이아웃 아래에 입력을 하는 행을 하나 추가해줘야하기 때문에 넘겨 받음. stockBar 가 전체를 포함해서 stockBar 인스턴스를 넘겨주면 됨
    targetCategory : stockFile 에서 category를 찾아가기 위해 필요함
    """
    def clearLayout(layout):
      if layout is not None:
          while layout.count():
              item = layout.takeAt(0)
              widget = item.widget()
              child_layout = item.layout()
              if widget is not None:
                  widget.deleteLater()  # 위젯 제거
              elif child_layout is not None:
                  clearLayout(child_layout)  # 하위 레이아웃 재귀적으로 비우기
                  child_layout.deleteLater()
    def completeEdit(qLineWidget):
      """
      개수 추가 수정을 완료했을 경우, stocFiles에 해당 개수를 설정하고 수정 을 중지
      targetLatyout: editRow가 추가된 레이아웃, 여기서 editrow 오브젝트를 삭제할 것임
      qLineWidget: 해당 칸에 적힌 숫자로 업데이트 할 것임
      """
      stockFile[targetCategory]["입고량"] = int(stockFile[targetCategory]["입고량"])+int(qLineWidget.text())
      with open(stockFilePath,"w",encoding="utf-8") as f:
        json.dump(stockFile,f,ensure_ascii=False,indent=4)
      for i in range(targetLatyout.count()):
          layout = targetLatyout.itemAt(i).layout()
          # print(layout,layout.objectName()) # <PySide6.QtWidgets.QHBoxLayout(0x18df1aa2580, name = "editrow") at 0x0000018DF2454880> editrow
          if layout and layout.objectName() == "editrow":
            clearLayout(layout)
            self.reload(targetCategory)
            break
    # 수정하기 버튼을 중복해서 누를 경우를 방지하기 위함
    # 앞으로 위젯 이름을 아예 지정하도록 코딩하면 더 편하겠는걸 ?
    for i in range(targetLatyout.count()):
      item = targetLatyout.itemAt(i).layout()
      if item and item.objectName() == "editrow":
        return 
    editRow = QHBoxLayout()
    editRow.setObjectName("editrow")
    numberInpyt = QLineEdit()
    numberInpyt.setValidator(QIntValidator(0, 9999))
    numberInpyt.setPlaceholderText("여기에 숫자 입력")
    
    editBtn = QPushButton("수정하기")

    editRow.addWidget(numberInpyt,stretch=2)# layout.addWidget(widget, stretch=N) → N 값에 따라 공간을 나눔
    editRow.addWidget(editBtn,stretch=1) # 위 예제에서는 전체 공간을 1:2:3 비율로 나눠서 버튼 크기가 달라집니다
    editBtn.clicked.connect(lambda _:completeEdit(numberInpyt))
    targetLatyout.addLayout(editRow)
  def reload(self,stockTarget):
    """
    특정 재고만 골라서 reload하기.
    """
    def clearLayout(layout):
      if layout is not None:
          while layout.count():
              item = layout.takeAt(0)
              widget = item.widget()
              child_layout = item.layout()
              if widget is not None:
                  widget.deleteLater()  # 위젯 제거
              elif child_layout is not None:
                  clearLayout(child_layout)  # 하위 레이아웃 재귀적으로 비우기
                  child_layout.deleteLater()
    try:
      for i in range(self.canLayout.count()):
        widget = self.canLayout.itemAt(i).widget()
        # print(layout,layout.objectName()) # <PySide6.QtWidgets.QHBoxLayout(0x18df1aa2580, name = "editrow") at 0x0000018DF2454880> editrow
        if widget and widget.objectName() == stockTarget:
          clearLayout(widget.layout()) # widget이 setLayout으로 달라 붙었기 때문에 위젯을 지우는 것이 아닌 그 안에 layout 내용을 지워야함
          # widget.deleteLater() # 내용 다 지웠으면 이제 껍대기 지워야 함 지우지 말고 안 에 내부만 채우도록 합시다
          self.makeStockBar(stockTarget,"reload")
          break
    except Exception as e:
       writeErrorlog(f"-------------reload 함수에러 발생-------------\n{e}")
  def posMachine_afterOrderFinish(self,receipt):
    """
    orderRst : 주문지 결과
      - {'경복루 염소탕': {'category': '염소류', 'amount': 2, 'price': 12000}, '염소 전골': {'category': '염소류', 'amount': 2, 'price': 20000}}
    """
    # 일다 ㄴ원산지고 뭐, 음식 영양표 이런걸 만들 시간은 없으니
    # 일단 하드코딩으로 조절합시다
    # 260418
    try:
      for menuName in receipt:
        if receipt[menuName]["category"]=="소주":
          for stockName in stockFile:
            if re.match(re.escape(menuName),stockName):
              stockFile[menuName]["입고량"]=int(stockFile[menuName]["입고량"]) - int(receipt[menuName]["amount"])
        else:
            if re.search("염소",menuName):
              stockFile["염소고기"]["입고량"]=int(stockFile["염소고기"]["입고량"]) - int(receipt[menuName]["amount"])
            elif re.search("맥주",menuName):
              stockFile["맥주"]["입고량"]=int(stockFile["맥주"]["입고량"]) - int(receipt[menuName]["amount"])
            elif re.search("돼지",menuName):
              pass
            elif re.search("콜라",menuName):
              stockFile["콜라"]["입고량"]=int(stockFile["콜라"]["입고량"]) - int(receipt[menuName]["amount"])
            elif re.search("사이다",menuName):
              stockFile["사이다"]["입고량"]=int(stockFile["사이다"]["입고량"]) - int(receipt[menuName]["amount"])
            elif re.search("돼지",menuName):
              pass
            elif re.search("돼지",menuName):
              pass
        #  stockFile["염소고기"]["입고량"]=int(stockFile["염소고기"]["입고량"]) - int(receipt[menuName]["amount"])
        # elif re.search("소",menuName):
      with open(stockFilePath,"w",encoding="utf-8") as f:
        json.dump(stockFile,f,ensure_ascii=False,indent=4)
      for category in stockFile:
        # 모든 메뉴 초기화
        self.reload(category)
    except Exception as e:
        writeErrorlog(f"------------ posMachine_afterOrderFinish 에러 발생 ------------\n{e}")


     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = stockManagement()
    demo.show()
    sys.exit(app.exec_())
# 흠 재고관리 이거 어떻게 해야할까나 ..

# 어느 기준으로 해야하지 ?

# 이렇게 합시다, 어차피 술,음료는 개수로 나가고 음식은 "인분"으로 나가니까, 

# 고기는 100g 으로 나가니까, 1인분에 100g 이니 재고를 넣을 대는 몇 g,kg 을 적게하고 재고에서는 _g(x인분) 이렇게 적어두자고, 수정못하게 하고
# 수정하고 싶으면 그 아래 재고 추가 버튼을 눌러서 100g/kg 인지 적게 하자고 인분은 알아서 계산하게 하고 ㅇㅇ 이러면 될 듯

# 술 음료는 개수인데 제일 간단함

# - 결론 ui 
#   재료이름 : _ _  , 남은재고량 : g(_ _인분)
#     추가하기  수정하기
#   재료이름 : 소주 , 남은 재고량 : _ _ 개
#     추가하기  수정하기
#   _재료추가버튼_ -> 이걸 누르면 새로 추가가 가능, json에서 알아서 수정도 가능

# + g 계산법 , 테이블 마감하면 x 인분이니까 x인분 x 해당고기의 단위 g 곱해서 재고json에서 빼면 되겄네.


# 염소탕 : 100 g, 전골 ,수육무침 : 200g -> 염소고기 , 1kg 
# 돼지뼈 -> kg

# json 형태

# # 음 ,이렇게 해서 입고날자 기준으로 만약 해당 입고량이 0이 되면 해당 내용 자동 삭제 시켜서 관리하면되것네, 
# # 알고리즘은 염소고기 안에서 입고날이 제일 오래된 거에서 빼서 최신꺼 남기면 되것네. 어차피 버려도 돼, 뭐 따로 저장하지 맙시다
