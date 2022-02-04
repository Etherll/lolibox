import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QWidget
from PyQt5.QtGui import QPainter,QBrush,QColor
import json
import io
import requests
import keyboard
from PyQt5.QtCore import Qt,QPoint,QRect,QThread,pyqtSignal
from PIL import ImageQt,ImageGrab ,ImageEnhance

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog )
        self.showFullScreen()
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(widget)
        self.begin = QPoint()
        self.end = QPoint()
        self.show()
        self.screenshot = ImageGrab.grab().convert("RGBA")
        self.image = ImageEnhance.Brightness(self.screenshot).enhance(0.7)
        self.first = QPoint()
        self.second = QPoint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def paintEvent(self, event):
        qpixmap= ImageQt.toqpixmap(self.image)
        qp = QPainter(self)
        qp.drawPixmap(self.rect(), qpixmap)
        br = QBrush(QColor(100, 10, 10, 40))  
        qp.setBrush(br)   
        qp.drawRect(QRect(self.begin, self.end)) 

    def mousePressEvent(self, event):
        self.first = event.pos()
        self.second = event.pos()
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        
        area = (self.first.x(),self.second.y() ,self.begin.x(),self.end.y())
        if self.first.x() > self.begin.x():
            area = (self.begin.x(),self.second.y(),self.first.x(),self.end.y())
        if self.second.y() > self.begin.y():
            area = (self.first.x(),self.begin.y(),self.end.x(),self.second.y())
        if self.first.x() > self.begin.x() and self.second.y() > self.begin.y():
            area = (self.begin.x(),self.begin.y(),self.first.x(),self.second.y())
        self.screenshot = self.screenshot.crop(area)
        output = io.BytesIO()
        self.screenshot.convert("RGB").save(output, "jpeg")
        files= {'photo': ('61f597c8bcef3a0032d37c1c.jpg',output.getvalue(),'image/jpeg')}
        self.worker = GetData()
        self.worker.files = files
        self.worker.start()
        self.worker.clean_text.connect(self.copy_text)
    def copy_text(self, text):
        cb = QApplication.clipboard()
        cb.clear()
        cb.setText(text)
        self.close()

class GetData(QThread):
    files = {}
    clean_text = pyqtSignal(str)
    def senddata(self):
        req = requests.post('https://blackboxapp.co/getsingleimage',files=self.files).json()
        if req !='Error':
            return self.clean_text.emit(req['text'].replace('%3D',''))
        elif req == 'Error':
            self.senddata()
        else:
            print('error',req)
    def run(self):
        self.senddata()

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
hot_key = json.loads(open("config.json","r").read())

keyboard.add_hotkey(hot_key['key'], run) 
  
keyboard.wait()
