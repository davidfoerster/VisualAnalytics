import functools

from PyQt4.QtGui import QWidget
import histogram_ui
import numpy as np
import matplotlib.pyplot as plt


class HistogramWidget(QWidget, histogram_ui.Ui_Form):
	def __init__(self, btnHistogram):
		super(HistogramWidget, self).__init__()
		self.btnHistogram = btnHistogram

	def closeEvent(self, event):
		self.btnHistogram.setEnabled(True)
		self.hide()

	def onHistogram(self, interval, selectedPoints):
		self.btnHistogram.setEnabled(False)
		self.widForm = QWidget()
		self.wid = histogram_ui.Ui_Form()
		self.wid.setupUi(self.widForm)

		if interval == "month":
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")
		else:
			self.wid.sliderMonth.setEnabled(False)
			self.wid.cbMonth.setEnabled(False)
			self.wid.labHistogram.setText("Interval: 6 hours (1460 intervals)")
		self.wid.sliderMonth.valueChanged.connect(self.setMonthValue)
		self.widForm.show()

		self.wid.btnPaint.clicked.connect(functools.partial(self.paintHistogram, selectedPoints))
		self.wid.btnCancel.clicked.connect(self.closeEvent)
		print(self.wid.cbMonth.currentIndex())

	def setMonthValue(self):
		self.value = self.wid.sliderMonth.value()
		if (self.value == 2):
			self.wid.labHistogram.setText("Interval: 3 Day (10 intervals)")
		elif (self.value == 1):
			self.wid.labHistogram.setText("Interval: 1 Day (30 intervals)")
		else:
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")

	def paintHistogram(self, *args):
		self.xs, self.ys = args[0].values().transpose()  # xs:small, ys:large
		self.dates = args[0].get_dates()
		if self.isVisible():
			self.update()

		self.small_hours = [0 for i in range(0, 25)]  # Liste mit 24 0-Werten, einen für jede Stunde pro Tag
		self.large_hours = [0 for i in range(0, 25)]

		self.sum_xs = []  # Summe der small Partikel
		self.sum_xs.append(0)
		self.sum_ys = []  # Summe der large Partikel
		self.sum_ys.append(0)
		for i in range(0, len(self.xs)):
			# self.sum_xs[0] = self.sum_xs[0] + self.xs[i]
			self.small_hours[self.dates[i][3]] = self.small_hours[self.dates[i][3]] + self.xs[i]  # Die small Partikel werde auf die jeweilige Stunde addiert
			self.large_hours[self.dates[i][3]] = self.large_hours[self.dates[i][3]] + self.ys[i] + 1000  # Die large Partikel werde auf die jeweilige Stunde addiert (+1000 damit bar zusehen ist)
		# self.sum_ys[0] = self.sum_ys[0] + self.ys[i]

		# print("sum_xs: ",self.sum_xs)
		print("small_hours: ", self.small_hours)
		print("large_hours: ", self.large_hours)
		# print(self.sum_ys[0])
		self.sum_particle = []  # Summe aller Partikel
		self.sum_particle.append(self.sum_xs[0] + self.sum_ys[0])

		fig = plt.figure()
		ax = fig.add_subplot(111)
		width = 0.35
		ind = np.arange(len(self.small_hours))
		small = ax.bar(ind, self.small_hours, width, color='green')
		large = ax.bar(ind + width, self.large_hours, width,color='red')  # ax.bar(Position, Datensatz, Breite der Bar, Farbe=

		# axes and labels
		ax.set_xlim(-width, len(ind) + width)
		ax.set_ylim(0, max(self.small_hours))
		ax.set_ylabel('Small Particle')
		ax.set_title('Dust Data')
		xTickMarks = [i for i in range(0, 25)]
		ax.set_xticks(ind + width)
		xtickNames = ax.set_xticklabels(xTickMarks)
		plt.setp(xtickNames, rotation=45, fontsize=10)

		## add a legend
		ax.legend((small[0], large[0]), ('small', 'large'))

		plt.show()
