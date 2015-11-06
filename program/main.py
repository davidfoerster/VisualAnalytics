import window_ui
from PyQt4.QtGui import *
import pyqtgraph as pg
import numpy
import sys

data = numpy.genfromtxt('dust-2014.dat', delimiter=';')[:, 1:]


class MainWindow(QMainWindow, window_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


class Plot:
    def __init__(self):
        self.form = MainWindow()
        self.scatterpoints = pg.ScatterPlotItem(data[:, 0], data[:, 1], pen=None, symbol='o')
        self.form.graphicsView.addItem(self.scatterpoints)
        self.form.graphicsView.setLabel(axis='left', text='small')
        self.form.graphicsView.setLabel(axis='bottom', text='large')
        self.form.show()
        self.tooltip = pg.TextItem(text='', color=(176, 127, 255), anchor=(1, 1))
        self.form.graphicsView.addItem(self.tooltip)
        self.tooltip.hide()
        self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)

    def onMove(self, pos):
        act_pos = self.scatterpoints.mapFromScene(pos)
        pts = self.scatterpoints.pointsAt(act_pos)
        if len(pts) != 0:
            self.tooltip.setText('x=%d\ny=%d' % (pts[0].pos()[0], pts[0].pos()[1]))
            # anchor des Tooltips anpassen, sodass Tooltip nicht aus dem Graph faellt
            self.tooltip.setPos(pts[0].pos())
            self.tooltip.show()
        else:
            self.tooltip.hide()


app = QApplication(sys.argv)
myplot = Plot()
app.exec_()
