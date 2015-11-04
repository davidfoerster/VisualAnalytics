import window_ui
from PyQt4.QtGui import *
import numpy
import pyqtgraph as pg
import sys

data = numpy.genfromtxt('dust-2014.dat',delimiter=';')[:,1:]

class MainWindow(QMainWindow,window_ui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)

app = QApplication(sys.argv)
form = MainWindow()

form.graphicsView.plot(data[:,0],data[:,1],pen=None,symbol='o')

form.show()
app.exec_()
