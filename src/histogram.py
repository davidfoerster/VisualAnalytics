from PyQt4.QtGui import QWidget
import histogram_ui
import numpy as np


class HistogramWidget(QWidget, histogram_ui.Ui_Form):
	def __init__(self, btnHistogram):
		super(HistogramWidget, self).__init__()
		self.btnHistogram = btnHistogram


	def closeEvent(self, event):
		self.btnHistogram.setEnabled(True)
		self.hide()


	def show(self):
		self.btnHistogram.setEnabled(False)
		super(HistogramWidget, self).show()


	def paintHistogram(self, *args):
		self.xs, self.ys = args[0].values().transpose()  # xs:small, ys:large
		self.dates = args[0].get_dates()
		if self.isVisible():
			self.update()


	def paintEvent(self, event):
		self.resize(800, 350)
		plt1 = self.graphicsView.addPlot()

		## make interesting distribution of values
		vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])

		## compute standard histogram
		y, x = np.histogram(vals, bins=np.linspace(-3, 8, 40))

		## Using stepMode=True causes the plot to draw two lines for each sample.
		## notice that len(x) == len(y)+1
		plt1.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
