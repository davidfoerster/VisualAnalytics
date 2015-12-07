#!/usr/bin/env python3.4

import os.path
import sys
import functools

import math
import scipy.special
import numpy as np
import pyqtgraph as pg
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import window_ui
import widgetwin_ui
from tree_scatter_plot import SelectableScatterPlotItem
import math_utils


def _main(*args):
	"""
	dtype legt den Datentyp der Spalten fest -> |S19 erzeugt aber keinen String sondern einen Bytestrom vom Format b'2014-01-01 00:00:00'
	names=["date", "small", "large"] legt die Namen der Spalten fest

	Weil die Ladedauer sehr hoch ist, wird erstmal nur der Datensatz mit allen Messdaten aus Januar verwendet. Beachtet dies bei den Filtern.
	"""

	data_path = args[0] if args else (_bindir + '/data/daten-klein.dat')
	data = np.genfromtxt(data_path,
		dtype = [('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter = ';',
		names = ["date", "small", "large"])

	app = QApplication(sys.argv)
	myplot = Plot(data)
	app.exec_()


_bindir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# TODO: was ist mit Schaltjahren?
# Liste mit Tagen und dazu gehörenden Datum zB Tag 365 ist der 2014-12-31
day = np.genfromtxt(_bindir + '/data/DateInDays.txt',
	dtype = [('day', '|i8'), ('date', 'S10')], delimiter = ',',
	names = ["sliderDay", "sliderDate"])


class MainWindow(QMainWindow, window_ui.Ui_MainWindow):
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)


class Plot:
	"""
	Plottet die Daten, welche in 'data' stehen.
	Filter-Button öffnet das Filter-Fenster
	Quit-Button schließt die Anwendung
	"""


	def __init__(self, data = None):
		self.data = data
		self.form = None
		self._regression_lines = ()
		self.scatterpoints = None
		self.tooltip = None
		self.scene = QGraphicsScene()
		self.pen = QPen(QColor(0, 0, 255))

		self.original_data = data
		self.new_data = data
		self.undo_data1 = self.new_data
		self.undo_data2 = self.undo_data1

		if data is not None:
			self.plotFilterRange(data['small'], data['large'], data['date'], autoDownsample = True)


	def onMove(self, scene_pos):
		pos = self.scatterpoints.mapFromScene(scene_pos)
		nearest_neighbor = self.scatterpoints.pointsAt(pos)
		nearest_neighbor = next(iter(nearest_neighbor), None)
		if nearest_neighbor is None:
			self.tooltip.hide()
			return

		s = self.data[nearest_neighbor]
		selection = self.scatterpoints.selection
		if nearest_neighbor in selection:
			tt = '{} selected items'.format(len(selection))
			for m in ('sum', 'median', 'mean', 'var'):
				tt += '\n{}s=[{:.3}, {:.3}]'.format(m.upper(), *selection.get_stat(m))
		else:
			tt = 'small={2:d}\nlarge={3:d}\ndate={0}'.format(s[0].decode(), *s)

		self.tooltip.setText(tt)
		# anchor des Tooltips anpassen, sodass Tooltip nicht aus dem Graph fällt
		self.tooltip.setPos(s[1], s[2])
		self.tooltip.show()


	def onfilterWindow(self):
		"""
		Das Filter-Fenster: besteht aus tabWidget mit 2 Reitern
		 Reiter Filter by Month/Day: treeWidget mit der Filterung von Monat und Tag. Ohne Tagangabe wird der komplette Monat gewählt
		 Reiter Filter by Range: Über zwei Slider kann ein Startdatum und Enddatum ausgewählt werden
		OK-Button funktioniert nur, wenn ein Filter gewählt wurde
		Cancel-Button schließt das Filter-Fenster
		"""

		self.widForm = QWidget()
		self.widForm.move(1110, 300)
		self.wid = widgetwin_ui.Ui_Form()
		self.wid.setupUi(self.widForm)

		# Erzeuge Liste mit allen eingetragenen Monaten aus dem treeWidget
		topLevelItem = self.wid.treeWidget.topLevelItem(0)
		childs = tuple(map(topLevelItem.child, range(topLevelItem.childCount())))

		# Sliders
		self.wid.sliderTo.setValue(365)
		self.wid.sliderFrom.valueChanged.connect(self.setFrom)
		self.wid.sliderTo.valueChanged.connect(self.setTo)
		self.widForm.show()

		# TreeWidget
		self.wid.treeWidget.itemClicked.connect(functools.partial(self.onItemClick, childs))

		# Buttons
		self.wid.btnCancel.clicked.connect(self.onCancel)
		self.wid.btnOk2.clicked.connect(self.onOkFilterSlider)
		self.wid.btnCancel2.clicked.connect(self.onCancel)
		self.wid.btnOk.clicked.connect(self.onOkMonth)


	def onItemClick(self, childs):
		getSelected = self.wid.treeWidget.selectedItems()
		if len(getSelected) > 0:
			baseNode = getSelected[0]
			# Prüft ob ein Monat bzw. Tag ausgewählt wurde
			childNodeText = baseNode.text(0)
			if baseNode in childs:
				print(len(self.wid.labMonth.text()))
				self.wid.labMonth.setText(childNodeText)
				print(len(self.wid.labMonth.text()))
			else:
				if len(childNodeText) == 1:
					childNodeText = "0" + childNodeText
				self.wid.labDay.setText(childNodeText)


	def onOkMonth(self):
		"""
		Sucht die Messdaten welche im Filter 'Filter by Month/Day' ausgewählt wurden
		1. onOkMonth: Baue Suchstring, bestehend aus Monat und Tag, zusammen
		2. filterMonth: Suche im Datensatz nach alle zutreffenden Messdaten
		3. plot(self, filter): Plotten der Daten
		"""

		if len(self.wid.labMonth.text()) > 1:
			strMonth = self.wid.labMonth.text()
			if strMonth == 'January':
				print("January")
				self.filterMonth('2014-01' + '-' + self.wid.labDay.text())
			elif strMonth == 'February':
				print("February")
				self.filterMonth('2014-02' + '-' + self.wid.labDay.text())
			elif strMonth == 'March':
				print("March")
				self.filterMonth('2014-03' + '-' + self.wid.labDay.text())
			elif strMonth == 'April':
				print("April")
				self.filterMonth('2014-04' + '-' + self.wid.labDay.text())
			elif strMonth == 'May':
				print("May")
				self.filterMonth('2014-05' + '-' + self.wid.labDay.text())
			elif strMonth == 'June':
				print("June")
				self.filterMonth('2014-06' + '-' + self.wid.labDay.text())
			elif strMonth == 'July':
				print("July")
				self.filterMonth('2014-07' + '-' + self.wid.labDay.text())
			elif strMonth == 'August':
				print("August")
				self.filterMonth('2014-08' + '-' + self.wid.labDay.text())
			elif strMonth == 'September':
				print("September")
				self.filterMonth('2014-09' + '-' + self.wid.labDay.text())
			elif strMonth == 'October':
				print("October")
				self.filterMonth('2014-10' + '-' + self.wid.labDay.text())
			elif strMonth == 'November':
				print("November")
				self.filterMonth('2014-11' + '-' + self.wid.labDay.text())
			elif strMonth == 'December':
				print("December")
				self.filterMonth('2014-12' + '-' + self.wid.labDay.text())


	def filterMonth(self, timeInterval):
		# TODO: Use numpy.ndarray's range filter view instead of deleting tuples piece by piece
		self.undo_data2 = self.undo_data1
		self.undo_data1 = self.new_data
		new_data = self.original_data
		index = 0
		for s in new_data:
			decode_date = s[0].decode("utf-8")
			if timeInterval in decode_date:
				index += 1
			else:
				new_data = np.delete(new_data, index)
		if new_data:
			self.data = new_data
			if len(self.data) > 0:
				self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample = True)
		else:
			msgBox = QMessageBox()
			msgBox.setText("No data exists for the filter!")
			msgBox.exec_()


	def plot(self, filter):
		"""
		Kann verwendet werden, wenn ein kompletter Monat ausgewählt wurde
		Parameter 'filter' muss eine Datei sein
		"""

		new_data = np.genfromtxt(filter, dtype = [('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter = ';',
			names = ["date", "small", "large"])
		self.plotFilterRange(new_data['small'], new_data['large'])


	def onDelete(self):
		if len(self.scatterpoints.selection) > 0:
			self.undo_data2 = self.undo_data1
			self.undo_data1 = self.new_data  # undo_data1 speichert die Datenmenge vor dem Bearbeiten
			index = 0
			index_diff = 0
			for s in self.new_data:
				for p in self.scatterpoints.selection.copy():
					r = p-index_diff #Index-Differenz beim Löschen von Elementen aus new_data und p
					if self.new_data[r] == s:
						index_deff = index_diff +1
						self.new_data = np.delete(self.new_data, index)
						index = index - 1  # new_data wird kleiner, darum darf der Index nicht wachsen.
						self.scatterpoints.selection.remove(p)
				index = index + 1
			self.data = self.new_data  # somit kann weiterhin mit data['small'] und data['large'] gearbeitet werden.

			self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample = True)


	def undoFunction(self):
		self.new_data = self.undo_data1
		self.undo_data1 = self.undo_data2
		self.data = self.new_data
		self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample = True)


	def onCancel(self):
		"""
		Jeder Cancel-Button blendet das Filter-Fenster aus
		"""

		self.widForm.close()


	def onQuit(self):
		"""
		Quit-Button schließt die Anwendung
		"""
		sys.exit()


	def onOkFilterSlider(self):
		"""
		Sucht alle Messdaten in gegeben Zeitraum (von 'fromValue' bis 'toValue')
		1. onOkFilterSlider: Prüfe ob fromValue < toValue ist, ansonsten tausche die Werte und ändere Slider
			 danach suche alle Messdaten im Zeitraum
		2. plotFilterRange(self, small, large): Plotten der Daten. Small/Large = Liste allen kleinen/großen Partikel
		"""

		fromValue = int(self.wid.sliderFrom.value())
		toValue = int(self.wid.sliderTo.value())
		if fromValue > toValue:
			fromValue = toValue
			toValue = self.wid.sliderFrom.value()
			self.wid.sliderFrom.setValue(fromValue)
			self.wid.sliderTo.setValue(toValue)

		fromDate = self.getDateFromDay(fromValue)
		toDate = self.getDateFromDay(toValue)
		self.wid.labFrom.setText(fromDate)
		self.wid.labTo.setText(toDate)

		isDeletePoint = True  # Alle Punkte die nicht im Filterzeitraum liegen, werden aus der Datenmenge gelöscht
		self.undo_data2 = self.undo_data1
		self.undo_data1 = self.new_data
		self.new_data = self.original_data
		index = 0
		for s in self.new_data:
			decode_date = s[0].decode("utf-8")

			if (fromDate in decode_date) and isDeletePoint:
				isDeletePoint = False

			if (toDate in decode_date) and not isDeletePoint:
				isDeletePoint = True

			if isDeletePoint:
				self.new_data = np.delete(self.new_data, index)
				# new_data wird kleiner, darum darf der Index nicht wachsen.
			else:
				index += 1

		if len(self.new_data) > 0:
			self.data = self.new_data
			if len(self.data) > 0:
				self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample = True)
		else:
			msgBox = QMessageBox()
			msgBox.setText("No data exists for the filter!")
			msgBox.exec_()


	def _update_regression_line(self, *args):
		lines = self._regression_lines
		if not lines:
			return

		if self.form.actionFitLine.isChecked():
			if self.scatterpoints.selection:
				xs, ys = self.scatterpoints.selection.values().transpose()
			else:
				xs = self.data['small']
				ys = self.data['large']

			if len(xs) > 2:
				a, b, q, r, sigma_a, sigma_b = math_utils.fitLine(xs, ys)

				lines[0].setValue(QPointF(0, a))
				lines[1].setValue(QPointF(0, a - sigma_a))
				lines[2].setValue(QPointF(0, a + sigma_a))

				lines[0].setAngle(math.degrees(math.atan(b)))
				lines[1].setAngle(math.degrees(math.atan(b - sigma_b)))
				lines[2].setAngle(math.degrees(math.atan(b + sigma_b)))

				lines[0].setToolTip('a = %f\nb = %f\np = %f\nr = %f' % (a, b, q, r))

				for l in lines:
					l.show()
				return

		for l in lines:
			l.hide()


	def fitCubic(self, *args):
		if self.form.actionFitCubic.isChecked():
			pass

			# was ist Maximum-Likelihood
			# wie berechnet man das Polynom
			# wie stellt man es dar

		else:
			pass


	def plotFilterRange(self, small, large, dates, **kwargs):
		self.form = MainWindow()
		# self.form.move(300, 300)
		self.form.timeline.setScene(self.scene)
		self.form.timeline.setSceneRect(0, 0, 710, 10)

		dayIndices = list(map(lambda x: x[1], day))
		dayIndex = -1
		for d in dates:
			d = d[0:10]  # b'2014-01-01 00:00:00' => b'2014-01-01'
			if dayIndex != dayIndices.index(d):
				dayIndex = dayIndices.index(d)
				rect = self.scene.addRect(2 * dayIndex, 1, 1, 10, self.pen)
				rect.setToolTip(bytes.decode(d))

		self.scatterpoints = SelectableScatterPlotItem(small, large, pen=None, symbol='o', **kwargs)
		self.form.graphicsView.addItem(self.scatterpoints)
		self.form.graphicsView.setLabel(axis = 'left', text = 'large')
		self.form.graphicsView.setLabel(axis = 'bottom', text = 'small')
		self.form.graphicsView.showGrid(True, True)
		self.form.show()
		self.tooltip = pg.TextItem(text = '', color = (176, 127, 255), anchor = (1, 1))
		self.form.graphicsView.addItem(self.tooltip)
		self.tooltip.hide()
		self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)
		self.form.btnFilter.clicked.connect(self.onfilterWindow)
		self.form.btnQuit.clicked.connect(self.onQuit)
		self.form.btnDelete.clicked.connect(self.onDelete)
		self.form.btnUndo.clicked.connect(self.undoFunction)

		self.form.actionFitLine.triggered.connect(self._update_regression_line)
		self.form.actionFitCubic.triggered.connect(self.fitCubic)
		self.scatterpoints.selection.change_listeners += (self._update_regression_line, self.fitCubic)

		insecurity_line_pen = QPen(QColor.fromRgbF(1, 1, 0, 0.5))
		self._regression_lines = (
			pg.InfiniteLine(),
			pg.InfiniteLine(pen=insecurity_line_pen),
			pg.InfiniteLine(pen=insecurity_line_pen))
		for l in self._regression_lines:
			l.hide()
			self.form.graphicsView.addItem(l)

		print("len Filter: ", len(self.new_data))


	def getDateFromDay(self, chooseDay):
		"""
		Wandelt die Byte-Daten in Strings um
		"""

		sliderDate = day['sliderDate']
		chooseDateByte = sliderDate[chooseDay]
		chooseDate = chooseDateByte.decode("utf-8")
		return chooseDate


	def setFrom(self):
		"""
		Setzen des From-Sliders bei Änderung
		"""
		chooseDay = self.wid.sliderFrom.value()
		chooseDate = self.getDateFromDay(chooseDay)
		print(chooseDate)
		self.wid.labFrom.setText(chooseDate)


	def setTo(self):
		"""
		Setzen des To-Sliders bei Änderung
		"""

		chooseDay = self.wid.sliderTo.value()
		chooseDate = self.getDateFromDay(chooseDay)
		self.wid.labTo.setText(chooseDate)


if __name__ == '__main__':
	_main(*sys.argv[1:])
