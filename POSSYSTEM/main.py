import sys
from PySide6.QtWidgets import (
  QMainWindow,QStackedWidget,QPushButton,QHBoxLayout,QVBoxLayout,QWidget,QApplication
)

from stockManagement import stockManagement
from posMachine import posMachine

class main(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Let's Pos")
    self.setGeometry(100, 100, 1500, 900)

    self.stack = QStackedWidget()
    self.win2 = stockManagement()
    self.win1 = posMachine(self.win2)
    

    self.stack.addWidget(self.win1)
    self.stack.addWidget(self.win2)

    btn1 = QPushButton("포스기계")
    btn2 = QPushButton("재고관리")
    btn1.clicked.connect(lambda _ : self.stack.setCurrentIndex(0))
    btn2.clicked.connect(lambda _ : self.stack.setCurrentIndex(1))

    topBar = QHBoxLayout()
    topBar.addStretch()
    topBar.addWidget(btn1)
    topBar.addWidget(btn2)

    mainLayout = QVBoxLayout()
    mainLayout.addLayout(topBar)
    mainLayout.addWidget(self.stack)

    container = QWidget()
    container.setLayout(mainLayout)
    self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = main()
    win.show()
    sys.exit(app.exec())