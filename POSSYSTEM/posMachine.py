import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,QPushButton,
    QSplitter, QTextEdit,QGridLayout,QScrollArea,QVBoxLayout,QLabel,QMessageBox,QHBoxLayout,QGroupBox,QStackedWidget
)
from PySide6.QtCore import Qt
import json
from escpos.printer import Serial
import datetime,sys,os
from stockManagement import stockManagement
#  print(sys.executable) # C:\Users\dlrms\OneDrive\Desktop\business\POSSYSTEM\dist\MyApp\MyApp.exe -> .exe로 만들어서 실행시 경로
if os.path.basename(sys.executable) == "python.exe":
    dirPath =os.getcwd()
else:
    dirPath = os.path.dirname(sys.executable)

orderFolder = os.path.join(dirPath, "주문일자")
os.makedirs(orderFolder,exist_ok=True)
# class MainWindow(QMainWindow):
errorlog = open("errorLogPosMachone.txt","wt+")
def writeErrorlog(내용):
  nowTime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
  내용 = "{} _ {}\n".format(nowTime,내용)
  errorlog.write(내용)
class posMachine(QWidget):
    def __init__(self,stockManagementInstance:stockManagement):
        """
        stockManagementInstance : stockManagement 랑 연락해야해서 필요하게됨
        """
        self.stockManagementInstance :stockManagement = stockManagementInstance
        def makeButton(self,buttonText,buttonConnectFunc,buttinName:str):
            """
            self : 메인 윈도우 인스턴스
            buttonText : 버튼에 삽입할 iterable 값
            buttonConnectFunc : 버튼을 누를시 연결할 함수 주소
            return -> left_top_scroll, 스클롤링이 가능한 table widget
            """
            left_top_widget =  QGroupBox(buttinName)
            grid = QGridLayout()
            grid.setRowStretch(10, 1) # # 이게 훨 나은듯.grid.setAlignment(Qt.AlignTop)
            for i,text in enumerate(buttonText):
                btn = QPushButton(str(text))
                btn.setFixedSize(80, 25)
                btn.clicked.connect(lambda _,t = text:buttonConnectFunc(t)) # _,t clicked는 기본적으로 첫번째에 bool을 넘기기에 에러 발생해서 _ 처리 해야함
                # 타원형 스타일
                btn.setStyleSheet("""
                    QPushButton{
                        border-radius:25px;
                        background-color:#87CEFA;
                        font-size:16px;
                        font-weight:bold;
                    }
                    QPushButton:hover{
                        background-color:#5DADE2;
                    }
                """)
                # grid 배치 (4개씩)
                row = (i) // 4
                col = (i) % 4
                grid.addWidget(btn, row, col)
                self.tableButtonBox[str(text)]= btn
            left_top_widget.setLayout(grid)
            left_top_widget.setMinimumSize(350, 400)
            left_top_scroll = QScrollArea()
            left_top_scroll.setWidgetResizable(True)
            left_top_scroll.setWidget(left_top_widget) # 이제보니 이걸 하는 순간 left_top_widget은 사라지고 left_top_scroll이 위젯이 되어버리는 느낌이네, 에러뜸 
            #     left_bottom_splitter.addWidget(makeButton(self,self.menuData.keys(),self.renderFoodButton))
            #     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # RuntimeError: Internal C++ object (PySide6.QtWidgets.QGroupBox) already deleted.
            return left_top_scroll
        super().__init__()
        sysInfoPath = os.path.join(dirPath,"systemInfo.json")
        if os.path.exists(sysInfoPath):
            with open(sysInfoPath,"r",encoding="utf-8") as f:
                self.systemInfo =  json.load(f)
        else:
            QMessageBox.warning(self,"경로없음","'{}' 에 systemInfo.json 파일이 없습니다, 배치해주세요".format(dirPath))
            sys.exit(1)
        menuPath = os.path.join(dirPath,"menu.json")
        if os.path.exists(menuPath):
            with open(menuPath,"r",encoding="utf-8") as f:
                self.menuData = json.load(f)
        else:
            QMessageBox.warning(self,"경로없음","'{}' 에 menu.json 파일이 없습니다, 배치해주세요".format(dirPath))
            sys.exit(1)

        self.orderPrinter = Serial(
        devfile=self.systemInfo["receiptPort"], # 현재 연결된 포트에서 COM4인지 COM5인지 확인해서 넣기
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1
        )
        self.orderPrinter.set()
        self.currentSelectedTable = None # 1~13 테이블 중 선택시 변경
        self.currentSelectedFoodCategory = None # 탕, 밥 , 음료 선택시 변경
        
        
        self.tableButtonBox = {}
        self.tableOrderbox = {} # key : table번호 , 
                                # value : {
                                # 음식1:{"category":해당메뉴의카테고리,"amount":주문개수(int)},
                                # 음식2:{"category":해당메뉴의카테고리,"amount":주문개수(int)}}
        self.tableInfo = {} # key : table번호 ,  value : {"orderStart":"260101 16:45:32", "getPaper":False -> 최초에 주문지 출력했는지 여부. 주문지 최초 출력시 True로 변경}
        self.todayorderNumber = 1 # 테이블 계산 시작지, 오늘 주문 시작번호를 의미
        # --------------- 왼쪽 상단 분할 ---------------
        self.tableButtonWidget = makeButton(self,range(1,14),self.renderTableButton,"테이블")
        self.tableLayoyt = [self.tableButtonWidget.widget().layout().itemAt(i) for i in range(self.tableButtonWidget.widget().layout().count())]

        # ------------------------------------------------------------

        # --------------- 왼쪽 하단 분할 ---------------
        left_bottom_splitter = QSplitter(Qt.Vertical)
        self.menuListContainer = QWidget()
        self.menuLayout = QVBoxLayout() # 중요 1, 여기 안에 있는 내용들이 flush되고 다시 채워지고 할 것임
        self.menuListContainer.setLayout(self.menuLayout)   # 중요 2 , 빈깡통인 foodListContainer 에다가 menuLayout을 추적하도록 하기. 이렇게 하면 Layout만 바꾸면 모든 것이 해결 됨
        left_bottom_splitter.addWidget(makeButton(self,self.menuData.keys(),self.renderFoodButton,"메뉴"))
        # self.left_bottom_bottom = QWidget() # 결론적으로 필요가 없는 녀석 ..
        left_bottom_splitter.addWidget(self.menuListContainer)
        left_bottom_splitter.setSizes([150,400])
        # ---------------------------------------------

        # --------------- 오른쪽 화면 ---------------

        # 해당 테이블이 주문한 음식 보여주는 container
        self.tableMenuListContainer = QGroupBox("") # 이걸 실제 포함시켜야함. 이건 절대 변하면 안 됨
        self.tableMenuLayout = QVBoxLayout()
        self.tableMenuListContainer.setLayout(self.tableMenuLayout)

        # 총 계산금액 계산하는 container
        self.totalPrice = 0
        self.totalPriceContainer = QGroupBox("")
        self.totalPriceLayout = QHBoxLayout()
        self.totalPriceContainer.setLayout(self.totalPriceLayout)
        self.totalPriceLayout.addWidget(QLabel("총 금액 : "))
        

        # 모든 커맨드를 표출하는 곳
        # self.cmdButtonContainer = QWidget()
        self.getPaperbtn = QPushButton("주문지 출력")
        self.getPaperbtn.clicked.connect(lambda _:self.calculatorOrder())

        self.getAllOrderbtn = QPushButton("결제지 출력")
        self.getAllOrderbtn.clicked.connect(lambda _:self.getAllPaper())

        self.doneTable = QPushButton("테이블 마감")
        self.doneTable.clicked.connect(lambda _ :self.finishTable())
        # self.cmdButtonContainer = QWidget()
        self.cmdButtonContainer = QGroupBox("")

        self.cmdButtonLayout = QVBoxLayout()
        self.cmdButtonLayout.addWidget(self.getPaperbtn)
        self.cmdButtonLayout.addWidget(self.getAllOrderbtn)
        self.cmdButtonLayout.addWidget(self.doneTable)
        self.cmdButtonContainer.setLayout(self.cmdButtonLayout)
        
        # ---------------------------------------------

        # ------------- 최상단영역 설정 -------------
        top_area = QGroupBox("상단 영역")
        top_area.setFixedHeight(60)   # 원하는 높이 지정

        self.top_horizontal_boxLayout = QHBoxLayout()
        self.currentTableNumber = QLabel("선택한 테이블 : 없음")
        self.top_horizontal_boxLayout.addWidget(self.currentTableNumber)
        top_area.setLayout(self.top_horizontal_boxLayout)
        # -----------------------------------------
        # 최상위 수직 분할 (상단 / 하단)
        top_splitter = QSplitter(Qt.Vertical)


        # 메인 수직 분할 (왼쪽 / 오른쪽)
        main_splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 수평 분할 (위 / 아래)
        left_splitter = QSplitter(Qt.Vertical)
        # 왼쪽 구성
        left_splitter.addWidget(self.tableButtonWidget)
        left_splitter.addWidget(left_bottom_splitter)

        # 오른쪽 수평분할(위/아래)
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.tableMenuListContainer)
        right_splitter.addWidget(self.totalPriceContainer)
        right_splitter.addWidget(self.cmdButtonContainer)
        # 메인 구성
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)

        # 최상위 splitter에 상단 영역 + main_splitter 추가
        top_splitter.addWidget(top_area)
        top_splitter.addWidget(main_splitter)
        

        # 초기 비율
        top_splitter.setSizes([100, 800])   # 상단 100, 하단(main_splitter) 80
        main_splitter.setSizes([400, 400])
        left_splitter.setSizes([150, 300])
        right_splitter.setSizes([400,100,200])

        # self.setCentralWidget(top_splitter) # 더이상 QMainwindow가 아니라서 주석 처리
        window = QVBoxLayout()
        window.addWidget(top_splitter)
        self.setLayout(window) # QWidget을 상속받았으니 이렇게 해주면 된다고 함
        self.setStyleSheet("""
            QPushButton {
                font-size: 20px;
            }
            QLabel{
                font-size: 20px;
            }
            """)

        
        
    # def makebutton
    #     1. 주문지 인쇄 -> 현재 테이블에 담겨있는dict 정보와 price정보를 매칭시켜서 주문지에다가 넣고, 그걸 카운터보는
    #     사람은 주방에 토스하기
    #     2. 반드시 주문한 내용은 db에 저장해야함. 예기치 못한 상황에서 프로그램이 꺼져도 반드시 내용은 저장되어야 하기 때문임-> 즉 프로그램 로딩할 때
    #     해당 db 내용으로 시스템을 초기화 시켜야한다는 거임 !!
    def renderTableButton(self,value):
        self.currentSelectedTable = value
        self.renderTableOrder()
    def renderFoodButton(self,foodCategory):
        self.currentSelectedFoodCategory = foodCategory
        self.renderFoodListButton(self.currentSelectedFoodCategory)
    def renderFoodListButton(self,targetFoodCategory):
        """
        targetFoodCategory : 
        """
        def addMenu(self:posMachine,menuName,price):
            # self : parent 인스턴스의 주소
            if self.currentSelectedTable:   # 1. 반드시 테이블이 선택되어 있어야 함
                if self.currentSelectedTable not in self.tableOrderbox:
                    self.tableOrderbox[self.currentSelectedTable] = {}
                    self.tableInfo[self.currentSelectedTable] = {}
                if menuName in self.tableOrderbox[self.currentSelectedTable]:
                    self.tableOrderbox[self.currentSelectedTable][menuName]["amount"]+=1
                else:
                    starttime = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
                    self.tableInfo[self.currentSelectedTable]["orderStart"]= starttime
                    self.tableInfo[self.currentSelectedTable]["getPaper"]= False
                    self.tableOrderbox[self.currentSelectedTable][menuName]={"category":self.currentSelectedFoodCategory,"amount":1,"price":price}
                    self.todayorderNumber+=1
                self.renderTableOrder()
                # 주문 들어간거임 
                self.tableLayoyt[int(self.currentSelectedTable)-1].widget().setStyleSheet("""
                    QPushButton{
                        border-radius:25px;
                        background-color:#ff0000;
                        font-size:16px;
                        font-weight:bold;
                    }
                    QPushButton:hover{
                        background-color:#ff8a9a;
                    }
                """)
            else:
                QMessageBox.information(self,"테이블선택필요","음식을 추가할 테이블 번호를 선택해주세요.")
        # 기존 위젯 제거
        try: 
            while self.menuLayout.count():
                item = self.menuLayout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            if self.currentSelectedFoodCategory:
                menus:list = self.menuData[targetFoodCategory]
                menuWidget =QWidget() # 깡통
                menuLayout = QVBoxLayout() # 실제 내용물
                for menu in menus:
                    text = "{}  -  {:,}원".format(menu["name"],menu["price"])
                    btn = QPushButton(text)
                    # btn.setFixedHeight(40)
                    btn.clicked.connect(lambda _,menuname=menu["name"],price = menu["price"]: addMenu(self,menuname,price))
                    menuLayout.addWidget(btn)
                menuLayout.addStretch()
                menuWidget.setLayout(menuLayout)
                menu_scroll = QScrollArea()
                menu_scroll.setWidgetResizable(True)
                menu_scroll.setWidget(menuWidget)
                self.menuLayout.addWidget(menu_scroll)
                return menu_scroll
                # return menu_scroll
            else:
                # self.currentSelectedFoodCategory 가 None인 경우
                return QLabel("메뉴 카테고리를 선택해주세요")# 여기에다가 음식 카테고리를 선택해주세요 를 만들도록하기 
        except Exception as e:
            writeErrorlog(f"----------- renderFoodListButton 에러 발생 -----------\n{e}")
    def renderTableOrder(self):
        # 작동되는 곳
        # 1. 테이블 버튼이 무조건 클릭이 되어 있는 경우
        # 2. renderFoodListButton에서 메뉴 버튼을 눌럿을 경우 자동으로 해당 메뉴에 대한 정보가 올라감

        # 화면 상단에 선택한 테이블 숫자 변경시키기 위함
        try:
            while self.top_horizontal_boxLayout.count():
                item = self.top_horizontal_boxLayout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.top_horizontal_boxLayout.addWidget(QLabel(f"테이블 : {self.currentSelectedTable}"))

            while self.tableMenuLayout.count():
                item = self.tableMenuLayout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            self.doneTable.setText("{} 번 테이블 마감".format(self.currentSelectedTable))
            if self.currentSelectedTable in self.tableOrderbox and self.tableOrderbox[self.currentSelectedTable]:
                menuWidget =QWidget() # 깡통
                menuLayout = QVBoxLayout() # 실제 내용물
                for menuName in self.tableOrderbox[self.currentSelectedTable]:
                    numOfOrdered = self.tableOrderbox[self.currentSelectedTable][menuName]["amount"]
                    menuNameLabel = QLabel(str(menuName))
                    menuNumber = QLabel("{} 개 ".format(str(numOfOrdered)))
                    
                    menuPrice = QLabel("{:,} 원".format(self.tableOrderbox[self.currentSelectedTable][menuName]["amount"] * self.tableOrderbox[self.currentSelectedTable][menuName]["price"]))
                    addBtn = QPushButton("+")
                    addBtn.clicked.connect(lambda _,menu=menuName:self._renderTableOrder_addSubstractOrder("+",menu))
                    substractBtn = QPushButton("-")
                    substractBtn.clicked.connect(lambda _,menu=menuName:self._renderTableOrder_addSubstractOrder("-",menu))
                    box = QWidget()
                    boxLayout = QHBoxLayout()
                    boxLayout.addWidget(menuNameLabel)
                    boxLayout.addWidget(menuNumber)
                    boxLayout.addWidget(menuPrice)
                    boxLayout.addWidget(substractBtn)
                    boxLayout.addWidget(addBtn)
                    box.setLayout(boxLayout)
                    menuLayout.addWidget(box)
                menuLayout.addStretch()
                menuWidget.setLayout(menuLayout)
                menu_scroll = QScrollArea()
                menu_scroll.setWidgetResizable(True)
                menu_scroll.setWidget(menuWidget)
                self.tableMenuLayout.addWidget(menu_scroll)
                self._renderTableOrder_totalPrice()
            else:
                self.tableMenuLayout
        except Exception as e:
            writeErrorlog(f"-------------- renderTableOrder 에러 발생 --------------\n{e}")
    def _renderTableOrder_addSubstractOrder(self,calc,menuName):
        """
        calc : +,- 둘 중하나
        menuName : -,+ 대상의 메뉴이름
        """
        if calc == "+":
            self.tableOrderbox[self.currentSelectedTable][menuName]["amount"]+=1
        elif calc == "-":
            self.tableOrderbox[self.currentSelectedTable][menuName]["amount"]-=1
        self.renderTableOrder()
        self._renderTableOrder_totalPrice()
    def _renderTableOrder_totalPrice(self):
        """
        계산의 마무리 부분에 넣기.
        또는 +,- 코드 진행후 실행하기
        """
        # self.totalPriceContainer
            
        while self.totalPriceLayout.count()>1: # "총금액" QLabel은 나눠
            item = self.totalPriceLayout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        totalprice = 0
        for menuName in self.tableOrderbox[self.currentSelectedTable]:
            target  =self.tableOrderbox[self.currentSelectedTable][menuName]
            totalprice += target["amount"] * int(target["price"])
        
        self.totalPriceLayout.addWidget(QLabel(" {:,} 원".format(totalprice)))
        self.tableLayoyt[int(self.currentSelectedTable)-1].widget().setStyleSheet("""
                    QPushButton{
                        border-radius:25px;
                        background-color:#ff0000;
                        font-size:16px;
                        font-weight:bold;
                    }
                    QPushButton:hover{
                        background-color:#ff8a9a;
                    }   
                """)

    def calculatorOrder(self):
        # 껏다켜도 , 같은 port에 지속적으로 연결되어 있으면 포트는 변경안됨! - 260316 확인
        def getTablefilePath():
            today = datetime.datetime.now()
            yearmonthday = today.strftime("%Y%m%d")
            hourminsec = today.strftime("%H%M%S")
            filename = "{}번테이블_{}.json".format(self.currentSelectedTable,self.tableInfo[self.currentSelectedTable]["orderStart"])
            filepath = os.path.join(orderFolder,yearmonthday,filename)
            if not os.path.exists(os.path.join(orderFolder,yearmonthday)):
                os.makedirs(os.path.join(orderFolder,yearmonthday),exist_ok=True)
            return filepath
        try:
            if self.currentSelectedTable in self.tableOrderbox and self.tableOrderbox[self.currentSelectedTable]:
                if self.tableInfo[self.currentSelectedTable]["getPaper"] == False:
                    self.tableInfo[self.currentSelectedTable]["getPaper"] = True
                    filepath = getTablefilePath()
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(self.tableOrderbox[self.currentSelectedTable], f, ensure_ascii=False, indent=4)
                    self.getPaper(self.tableOrderbox[self.currentSelectedTable])
                else:
                    # 현재 메뉴 개수 - 과거 메뉴 개수 > 0 = True 일 경우만 새로 출력
                    filepath = getTablefilePath()
                    with open(filepath,"r",encoding="utf-8") as f:
                        beforeMenu = json.load(f)
                    judgeBox = {}
                    for menuName in self.tableOrderbox[self.currentSelectedTable]:
                        if menuName in beforeMenu.keys():
                            if self.tableOrderbox[self.currentSelectedTable][menuName]["amount"] - beforeMenu[menuName]["amount"] >=1:
                                judgeBox[menuName] = {"amount":self.tableOrderbox[self.currentSelectedTable][menuName]["amount"] - beforeMenu[menuName]["amount"]}
                        else:
                            # 새로운 음식이 들어옴
                            judgeBox[menuName] ={"amount":self.tableOrderbox[self.currentSelectedTable][menuName]["amount"]} 
                    if judgeBox.keys():
                        # 새 메뉴 있으면 gogo
                        self.getPaper(judgeBox)
                        # 새로 덮어 쓰기
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(self.tableOrderbox[self.currentSelectedTable], f, ensure_ascii=False, indent=4)
        except Exception as e:
            writeErrorlog(f"-------------- calculatorOrder 에러 발생 --------------\n{e}")

    def getPaper(self,orderReceipt:dict):
        """
        orderReceipt : self.tableOrderbox[self.currentSelectedTable] 와 똑같거나 {음식이름1:{"amount":개수}}형태
        """
        # 최초 출력 , 이 경우는 비교 없이 바로 주문지 제작
        try:
            self.orderPrinter._raw("\t---------- 주문 ----------\n\n".encode("cp949"))
            self.orderPrinter._raw(f"테이블 : {self.currentSelectedTable} 번\n\n".encode("cp949"))
            # 빈테이블에선 아무리 눌러도 적용이 되면 안 됨
            for menuName,amount in orderReceipt.items():
                self.orderPrinter._raw("메뉴 : {} -  {} 개\n\n".format(menuName,amount["amount"]).encode("cp949"))
            orderTime = datetime.datetime.now().strftime("%Y년 %m월 %d일- %H시 %M분%S초")
            self.orderPrinter._raw("주문시간: {}".format(orderTime).encode("cp949"))
            self.orderPrinter.cut()
        except Exception as e:
            QMessageBox.information(self,"영수증 기계 연결 실패","영수증 기계 연결이 불량합니다, 연결을 확인해주세요")
            writeErrorlog("------------- getPaper ---------------\n영수증 기계 연결 실패","영수증 기계 연결이 불량합니다, 연결을 확인해주세요")
    def getAllPaper(self):
        # 계산해보니 총 45칸 정도 되네
        #         self.tableOrderbox = {} # key : table번호 , 
        #                         # value : {
        #                         # 음식1:{"category":해당메뉴의카테고리,"amount":주문개수(int)},
        #                         # 음식2:{"category":해당메뉴의카테고리,"amount":주문개수(int)}}
        # self.tableInfo = {} # key : table번호 ,  value : {"orderStart":"260101 16:45:32", "getPaper":False -> 최초에 주문지 출력했는지 여부. 주문지 최초 출력시 True로 변경}
        try:
            if self.currentSelectedTable in self.tableOrderbox and self.tableOrderbox[self.currentSelectedTable]:
                self._drawReceipt_cutLine()
                self._drawReceipt_writeWord("사업자번호 : {}".format(self.systemInfo["ownerNumber"]))
                self._drawReceipt_writeWord("주소 : {}".format(self.systemInfo["adress"]))
                self._drawReceipt_writeWord("상호 : {}\t대표자 : {}".format(self.systemInfo["marketName"], self.systemInfo["owner"]))
                self._drawReceipt_writeWord("날짜 : {}".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
                self._drawReceipt_writeWord("전화번호(tel) : {}".format(self.systemInfo["tel"]))
                self._drawReceipt_category("주문 내역")
                totalPrice = 0
                for menuName,amount in self.tableOrderbox[self.currentSelectedTable].items():
                    nowPrice = amount["amount"]*amount["price"]
                    totalPrice+=nowPrice
                    self._drawReceipt_writeWord("{}  {} 개 : {:,}원\n".format(menuName,amount["amount"],nowPrice))
                self._drawReceipt_cutLine(line="-")
                self._drawReceipt_writeWord("총 금 액 : {:,}원".format(totalPrice))
                self._drawReceipt_cutLine(line="-")
                self._drawReceipt_cutLine()
                self.orderPrinter.cut()    
        except Exception as e:
            QMessageBox.information(self,"영수증 기계 연결 실패",f"영수증 기계 연결이 불량합니다, 연결을 확인해주세요\nerror:{e}")
    def _drawReceipt_category(self,word:str):
        self.orderPrinter._raw(("  "+f"============== {word} ==============  \n").encode("cp949"))
    def _drawReceipt_writeWord(self,word:str):
        self.orderPrinter._raw(("  "+word+"\n").encode("cp949"))
    def _drawReceipt_cutLine(self,line="="):
        # line : 기본은 = 인데 원하면 다른걸로 넣을 수도 있게 함
        self.orderPrinter._raw(("  "+line*39+"\n").encode("cp949"))
    def finishTable(self):
        def getTablefilePath():
            today = datetime.datetime.now()
            yearmonthday = today.strftime("%Y%m%d")
            hourminsec = today.strftime("%H%M%S")
            filename = "{}번테이블_{}.json".format(self.currentSelectedTable,self.tableInfo[self.currentSelectedTable]["orderStart"])
            filepath = os.path.join(orderFolder,yearmonthday,filename)
            if not os.path.exists(os.path.join(orderFolder,yearmonthday)):
                os.makedirs(os.path.join(orderFolder,yearmonthday),exist_ok=True)
            return filepath
        try:
            if self.currentSelectedTable in self.tableOrderbox and self.tableOrderbox[self.currentSelectedTable]: # 엉뚱한 곳 클릭해서 마감 버튼 눌러도 상관없도록하기 위함
                filepath = getTablefilePath()
                # 새로 덮어 쓰기
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(self.tableOrderbox[self.currentSelectedTable], f, ensure_ascii=False, indent=4)
                self.stockManagementInstance.posMachine_afterOrderFinish(self.tableOrderbox[self.currentSelectedTable])
                self.tableOrderbox.pop(self.currentSelectedTable)
                self.tableLayoyt[int(self.currentSelectedTable)-1].widget().setStyleSheet("""
                            QPushButton{
                                border-radius:25px;
                                background-color:#87CEFA;
                                font-size:16px;
                                font-weight:bold;
                            }
                            QPushButton:hover{
                                background-color:#5DADE2;
                            }
                        """)
                self.renderTableOrder()
        except Exception as e:
            writeErrorlog(f"------------ finishTable ------------\n{e}")
    def loadData(self):
        with open("menu.json","r",encoding="utf-8") as f:
            self.menuData = json.load(f)