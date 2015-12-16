import functools

from PyQt4.QtGui import QWidget, QMessageBox
import histogram_ui
import numpy as np
import matplotlib.pyplot as plt
import math


class HistogramWidget(QWidget, histogram_ui.Ui_Form):
	def __init__(self, btnHistogram):
		super(HistogramWidget, self).__init__()
		self.btnHistogram = btnHistogram

	def closeEvent(self, event):
		self.btnHistogram.setEnabled(True)
		self.hide()
		self.widForm.close()

	def onHistogram(self, interval, selectedPoints):
		self.btnHistogram.setEnabled(False)
		self.widForm = QWidget()
		self.wid = histogram_ui.Ui_Form()
		self.wid.setupUi(self.widForm)
		self.isYear = True

		if interval == "month":
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")
			self.isYear = False
		else:
			self.wid.sliderMonth.setEnabled(False)
			self.wid.cbMonth.setEnabled(False)
			self.wid.labHistogram.setText("Interval: 6 hours (1460 intervals)")
		self.wid.sliderMonth.valueChanged.connect(self.setMonthValue)
		self.widForm.show()

		self.wid.btnPaint.clicked.connect(functools.partial(self.paintHistogram, selectedPoints, interval))



		self.wid.btnCancel.clicked.connect(self.closeEvent)


	def setMonthValue(self):
		self.value = self.wid.sliderMonth.value()
		if (self.value == 2):
			self.wid.labHistogram.setText("Interval: 3 Day (10 intervals)")
		elif (self.value == 1):
			self.wid.labHistogram.setText("Interval: 1 Day (30 intervals)")
		else:
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")

	def paintHistogram(self, *args):
		print("------------------")
		if self.wid.checkBoxSmall.isChecked() | self.wid.checkBoxLarge.isChecked() | self.isYear:
			self.month = self.wid.cbMonth.currentIndex()
			self.interval = self.wid.sliderMonth.value()
			self.xs, self.ys = args[0].values().transpose()  # xs:small, ys:large
			self.dates = args[0].get_dates()
			if self.isVisible():
				self.update()

			if self.isYear:
				self.tickWidth = 1460
				self.small_particle = [0 for i in range(0, self.tickWidth)]
				self.large_particle = [0 for i in range(0, self.tickWidth)]
				self.sum_particle = [0 for i in range(0, self.tickWidth)]
				self.timeIndex = 3
			elif self.interval==2:
				self.tickWidth = 10
				self.small_particle = [0 for i in range(0, self.tickWidth)]  # Liste mit 10 0-Werten, einen für alle 3 Tage pro Monat
				self.large_particle = [0 for i in range(0, self.tickWidth)]
				self.sum_particle = [0 for i in range(0, self.tickWidth)]
				self.timeIndex = 2
			elif self.interval==1:
				self.tickWidth = 30
				self.small_particle = [0 for i in range(0, self.tickWidth)]   # Liste mit 10 0-Werten, einen für jeden Tag pro Monat
				self.large_particle = [0 for i in range(0, self.tickWidth)]
				self.sum_particle = [0 for i in range(0, self.tickWidth)]
				self.timeIndex = 2
			else:
				self.tickWidth = 120
				self.small_particle = [0 for i in range(0, self.tickWidth)]    # Liste mit 10 0-Werten, einen für alle 6 Stunden pro Tag
				self.large_particle = [0 for i in range(0, self.tickWidth)]
				self.sum_particle = [0 for i in range(0, self.tickWidth)]
				self.timeIndex = 3


			#Durchlaufe alle ausgewählten Punkte
			for i in range(0, len(self.xs)):

				#Prüfe ob der Punkt im ausgewählten Monat liegt
				if (self.dates[i][1] == self.month+1):
					if self.isYear:
						self.listIndex = int((self.dates[i][self.timeIndex])/6)+(self.dates[i][2]-1)*4
						#print("index4: ", self.listIndex)
					elif(self.interval==2):
						self.listIndex = int((self.dates[i][self.timeIndex])/3)
						print("index1: ", self.listIndex)
					elif(self.interval==1):
						print(self.dates[i][self.timeIndex])
						self.listIndex = (self.dates[i][self.timeIndex])-1
						print("index2: ", self.listIndex)
					else:
						#Index = Stunde/6 + (Tag*4)
						#Pro Tag gibt es 4 Intervalle je 6 Stunden
						#Beispiel: 01.01.2014 06:30 Uhr -> 06:30 / 6 = 1 und (1-1)*4 = 0 -> Index: 1+4 = 1  (Tag-1, weil Index bei 0 beginnt)
						#Beispiel: 01.02.2014 06:30 Uhr -> 06:30 / 6 = 1 und (2-1)*4 = 4 -> Index: 1+4 = 5  (Tag-1, weil Index bei 0 beginnt)
						self.listIndex = int((self.dates[i][self.timeIndex])/6)+(self.dates[i][2]-1)*4
						#print("index3: ", self.listIndex)


					self.small_particle[self.listIndex] = self.small_particle[self.listIndex] + self.xs[i]
					self.large_particle[self.listIndex] = self.large_particle[self.listIndex] + self.ys[i]
					self.sum_particle[self.listIndex] = self.small_particle[self.listIndex] + self.large_particle[self.listIndex]


			if(self.wid.checkBoxSmall.isChecked() & self.wid.checkBoxLarge.isChecked()):
				self.plotHistogram(self.sum_particle, "All")
			elif self.wid.checkBoxSmall.isChecked():
				self.plotHistogram(self.small_particle, "Small" )
			else:
				self.plotHistogram(self.large_particle, "Large")

		else:
			msgBox = QMessageBox()
			msgBox.setText("Choose small, large or both particle!")
			msgBox.exec_()

	def plotHistogram(self, data, kindOfData):

		print("particle: ", data)
		if self.tickWidth > 120:
			fig = plt.figure(figsize=(19,5))
		elif self.tickWidth > 30:
			fig = plt.figure(figsize=(15,5))
		else:
			fig = plt.figure(figsize=(7,5))
		ax = fig.add_subplot(111)
		width = 0.35
		ind = np.arange(len(data))



		if(kindOfData == "Small"):
			ax.bar(ind, data, width, color='green')
		elif kindOfData == "Large":
			ax.bar(ind, data, width, color='red')
		else:
			ax.bar(ind, data, width, color='orange')
		#large = ax.bar(ind + width, self.large_hours, width,color='red')  # ax.bar(Position, Datensatz, Breite der Bar, Farbe=
		# axes and labels

		ax.set_xticks(ind + width)
		ax.set_xlim(-width, len(ind) + width)
		ax.set_ylim(0, max(data))
		ax.set_ylabel(kindOfData + ' particle')
		ax.set_title('Dust Data')
		xTickMarks = [i for i in range(1, self.tickWidth+1)]
		print(self.tickWidth)
		if ((self.tickWidth > 31) & (self.tickWidth < 121)):
			for i in range(0, self.tickWidth):
				if (i > 0) & ((i % 2) != 0):
					xTickMarks[i]=""
		elif self.tickWidth > 120:
			for i in range(0, self.tickWidth):
				if (i > 0) & ((i % 15) != 0):
					xTickMarks[i]=""
		print(xTickMarks)

		xtickNames = ax.set_xticklabels(xTickMarks)
		plt.setp(xtickNames, rotation=45, fontsize=10)

		plt.show()