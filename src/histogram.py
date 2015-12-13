import histogram_ui
from PyQt4.QtCore import *
from PyQt4.QtGui import QWidget


class HistogramWidget(QWidget):
	def __init__(self):
		super(HistogramWidget, self).__init__()
		self.move(110, 300)
		self.hist = histogram_ui.Ui_Form()
		self.hist.setupUi(self)


	def closeEvent(self, event):
		print('Closing Histogram')


	def show(self):
		super().show()
