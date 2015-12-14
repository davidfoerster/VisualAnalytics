import histogram_ui
from PyQt4.QtGui import *
from data_selection import DataSelection


class HistogramWidget(QWidget, histogram_ui.Ui_Form):
	def __init__(self, btnHistogram, parent = None):
		super(HistogramWidget, self).__init__(parent)
		self.setupUi(self)
		self.btnHistogram = btnHistogram
		self.xs = None
		self.ys = None


	def closeEvent(self, event):
		self.btnHistogram.setEnabled(True)
		self.hide()


	def show(self):
		self.btnHistogram.setEnabled(False)
		super(HistogramWidget, self).show()


	def paintHistogram(self, *args):
		self.xs, self.ys = args[0].values().transpose() # xs:small, ys:large
		if self.isVisible():
			self.update()


	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.fillRect(10, 10, 100, 50, QBrush(QColor(0, 0, 255)))
		painter.end()
