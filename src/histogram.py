import functools

#import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from PyQt4.QtGui import QWidget, QMessageBox



import histogram_ui


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
		self.isMonth = True
		self.isDay = False


		if interval == "month":
			self.wid.sliderDay.setVisible(False)
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")
			self.isYear = False
		elif interval == "year":
			self.wid.sliderMonth.setEnabled(False)
			self.wid.cbMonth.setVisible(False)
			self.wid.labHistogram.setText("Interval: 6 hours (1460 intervals)")
			self.isMonth = False
		else:
			self.wid.sliderMonth.setVisible(False)
			self.wid.sliderDay.setEnabled(True)
			self.wid.sliderDay.setVisible(True)
			self.wid.labHistogram.setText("Interval: 1 hours (24 intervals)")
			self.isYear = False
			self.isMonth = False
			self.isDay = True

		self.wid.sliderMonth.valueChanged.connect(self.setMonthValue)
		self.wid.sliderDay.valueChanged.connect(self.setDayValue)
		self.widForm.show()
		self.wid.btnPaint.clicked.connect(functools.partial(self.computeHistogram, selectedPoints, interval))
		self.wid.btnCancel.clicked.connect(self.closeEvent)

	def setMonthValue(self):
		self.value = self.wid.sliderMonth.value()
		if (self.value == 2):
			self.wid.labHistogram.setText("Interval: 3 Day (10 intervals)")
		elif (self.value == 1):
			self.wid.labHistogram.setText("Interval: 1 Day (30 intervals)")
		else:
			self.wid.labHistogram.setText("Interval: 6 hours (120 intervals)")

	def setDayValue(self):
		self.value = self.wid.sliderDay.value()
		if (self.value == 2):
			self.wid.labHistogram.setText("Interval: 6 hours (4 intervals)")
		elif (self.value == 1):
			self.wid.labHistogram.setText("Interval: 3 hours (8 intervals)")
		else:
			self.wid.labHistogram.setText("Interval: 1 hours (24 intervals)")

	def computeHistogram(self, *args):
		if (self.wid.checkBoxSmall.isChecked() | self.wid.checkBoxLarge.isChecked() | self.isYear):
			self.month = self.wid.cbMonth.currentIndex()
			self.interval_m = self.wid.sliderMonth.value()
			self.interval_d = self.wid.sliderDay.value()
			self.xs, self.ys = args[0].values().transpose()  # xs:small, ys:large
			self.dates = args[0].get_dates()
			if self.isVisible():
				self.update()

			if self.isYear:
				self.tickWidth = 1460
				self.timeIndex = 3
			elif self.isMonth:
				if self.interval_m == 2:
					self.tickWidth = 10
					self.timeIndex = 2
				elif self.interval_m == 1:
					self.tickWidth = 30
					self.timeIndex = 2
				else:
					self.tickWidth = 120
					self.timeIndex = 3
			else:
				if self.interval_d == 2:
					self.tickWidth = 4
					self.timeIndex = 3
				elif self.interval_d == 1:
					self.tickWidth = 8
					self.timeIndex = 3
				else:
					self.tickWidth = 24
					self.timeIndex = 3


			self.sum_small_particle = [[0 for i in range(0, self.tickWidth)],[() for i in range(0, self.tickWidth)]]   # Liste mit Anzahl-tickWidth 0-Werten, für jeden Intervall ein Eintrag
			self.small_points = [[] for i in range(0, self.tickWidth)]
			self.sum_large_particle = [[0 for i in range(0, self.tickWidth)],[() for i in range(0, self.tickWidth)]]
			self.large_points = [[] for i in range(0, self.tickWidth)]
			self.sum_particle = [[0 for i in range(0, self.tickWidth)],[() for i in range(0, self.tickWidth)]]
			self.particle_points = [[] for i in range(0, self.tickWidth)]


			#Durchlaufe alle ausgewählten Punkte
			for i in range(0, len(self.xs)):
				# TODO: Tag 31 soll in das letzte Intervall mit rein?
				#Prüfe ob der Punkt im ausgewählten Monat liegt
				if((self.dates[i][1] == self.month+1) | self.isYear):
					if self.isYear:
						self.listIndex = int((self.dates[i][self.timeIndex])/6)+(self.dates[i][2]-1)*4
						#print("index4: ", self.listIndex)
					elif self.isMonth:
						if(self.interval_m == 2):
							self.listIndex = int((self.dates[i][self.timeIndex])/3)
							#print("index1: ", self.listIndex)
						elif(self.interval_m == 1):
							#print(self.dates[i][self.timeIndex])
							self.listIndex = (self.dates[i][self.timeIndex])-1
							#print("index2: ", self.listIndex)
						else:
							#Index = Stunde/6 + (Tag*4)
							#Pro Tag gibt es 4 Intervalle je 6 Stunden
							#Beispiel: 01.01.2014 06:30 Uhr -> 06:30 / 6 = 1 und (1-1)*4 = 0 -> Index: 1+0 = 1  (Tag-1, weil Index bei 0 beginnt)
							#Beispiel: 02.01.2014 06:30 Uhr -> 06:30 / 6 = 1 und (2-1)*4 = 4 -> Index: 1+4 = 5  (Tag-1, weil Index bei 0 beginnt)
							self.listIndex = int((self.dates[i][self.timeIndex])/6)+(self.dates[i][2]-1)*4
							#print("index3: ", self.listIndex)
					else:
						if self.interval_d == 2:
							self.listIndex = int((self.dates[i][self.timeIndex])/6)
						elif self.interval_d == 1:
							self.listIndex = int((self.dates[i][self.timeIndex])/3)
						else:
							self.listIndex = self.dates[i][self.timeIndex]
					print("index: ", self.listIndex)

					self.sum_small_particle[0][self.listIndex] = self.sum_small_particle[0][self.listIndex] + self.xs[i]
					self.small_points[self.listIndex].append(self.xs[i])

					self.sum_large_particle[0][self.listIndex] = self.sum_large_particle[0][self.listIndex] + self.ys[i]
					self.large_points[self.listIndex].append(self.ys[i])

					self.sum_particle[0][self.listIndex] = self.sum_small_particle[0][self.listIndex] + self.sum_large_particle[0][self.listIndex]
					self.particle_points[self.listIndex].append(self.xs[i]+self.ys[i])

			for l in range (0, self.tickWidth):
				if len(self.small_points[l])>0:
					statisticValues_small = (np.mean(self.small_points[l]),np.median(self.small_points[l]),np.sqrt(np.var(self.small_points[l])))
					statisticValues_large = (np.mean(self.large_points[l]),np.median(self.large_points[l]),np.sqrt(np.var(self.large_points[l])))
					statisticValues_particle = (np.mean(self.particle_points[l]),np.median(self.particle_points[l]),np.sqrt(np.var(self.particle_points[l])))
					self.sum_small_particle[1][l] = statisticValues_small
					self.sum_large_particle[1][l] = statisticValues_large
					self.sum_particle[1][l] = statisticValues_particle

			if(self.wid.checkBoxSmall.isChecked() & self.wid.checkBoxLarge.isChecked()):
				self.plotHistogram(self.sum_particle, "All")
			elif self.wid.checkBoxSmall.isChecked():
				self.plotHistogram(self.sum_small_particle, "Small" )
			else:
				self.plotHistogram(self.sum_large_particle, "Large")

		else:
			msgBox = QMessageBox()
			msgBox.setText("Select small, large or both particle!")
			msgBox.exec_()

	def plotHistogram(self, data, kindOfData):
		#print("max :",max(data[0]))
		if(max(data[0]) > 0):
			#Fenstergröße des Histogramms anpassen
			if self.tickWidth > 120:
				fig = plt.figure(figsize=(19,5))
			elif self.tickWidth > 30:
				fig = plt.figure(figsize=(15,5))
			else:
				fig = plt.figure(figsize=(8,5))

			ax = fig.add_subplot(111)
			width = 0.35
			ind = np.arange(len(data[0]))

			if(kindOfData == "Small"):
				ax.bar(ind, data[0], width, color='green') # ax.bar(Position, Datensatz, Breite der Bar, Farbe)
			elif kindOfData == "Large":
				ax.bar(ind, data[0], width, color='red')
			else:
				ax.bar(ind, data[0], width, color='orange')

			ax.set_xticks(ind + width/2)
			ax.set_xlim(-width, len(ind) + width)
			ax.set_ylim(0, max(data[0])+(0.1* max(data[0])))
			ax.set_ylabel(kindOfData + ' particle')
			ax.set_title('Dust Data')

			if self.isDay:
				if self.wid.sliderDay.value() == 2:
					xTickMarks = ["0-5", "6-11", "12-17", "18-23"]
				elif self.wid.sliderDay.value() == 1:
					xTickMarks = ["0-2", "3-5", "6-8", "9-11", "12-14", "15-17", "18-20", "21-23"]
				else:
					xTickMarks = [i for i in range(0, self.tickWidth)]
			else:
				xTickMarks = [i for i in range(1, self.tickWidth+1)]

			#Anpassen der x-Achsen Ticks bei sehr vielen Ticks
			if ((self.tickWidth > 31) & (self.tickWidth < 121)):
				for i in range(0, self.tickWidth):
					if (i > 0) & ((i % 2) != 0):
						xTickMarks[i]=""
			elif self.tickWidth > 120:
				for i in range(0, self.tickWidth):
					if (i > 0) & ((i % 15) != 0):
						xTickMarks[i]=""

			xtickNames = ax.set_xticklabels(xTickMarks)
			plt.setp(xtickNames, rotation=45, fontsize=10)

			txt = None
			def onMove(event):
				if event.xdata is None:
					return
				global txt
				max_y = data[0][int(event.xdata)]
				statistic_values =  data[1][int(event.xdata)]
				if statistic_values:
					tt = 'Mean={:.3}\nMedian={:.3}\nStd. Deviation={:.3}'.format(*statistic_values)
					props = dict(boxstyle='round', facecolor='wheat')
					txt = plt.text(event.xdata, max_y, tt,	horizontalalignment='center',verticalalignment='center', bbox=props)
					fig.canvas.draw()
					txt.remove()

			fig.canvas.mpl_connect('motion_notify_event', onMove)
			plt.show()

		else:
			msgBox = QMessageBox()
			msgBox.setText("No data selected for "+self.wid.cbMonth.currentText()+"!")
			msgBox.exec_()
