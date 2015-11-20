from PyQt4 import QtCore, QtGui
from data_selection import DataSelection

import numpy as np
import pyqtgraph as pg
import scipy.spatial


class TreeScatterPlotItem(pg.PlotDataItem):

	def __init__(self, *args, **kargs):
		super().__init__(*args, **kargs)
		self.data_tree = scipy.spatial.cKDTree(np.vstack((self.xData, self.yData)).transpose(), leafsize=1)


	def clear(self):
		super().clear()
		self.data_tree = None


	def point(self, idx):
		pt = self.data[idx]
		pt_item = pt['item']
		if pt_item is None:
			pt['item'] = pt_item = pg.SpotItem(pt, self)
		return pt_item


	def pointsAt(self, pos, k=1):
		ss = self._getPointSize(None)
		nearest_neighbors = self.data_tree.query([[pos.x(), pos.y()]], k, 0, 2, max(ss.x(), ss.y()))[1]
		nearest_neighbors = filter(lambda p: self._isPointAt(p, pos, ss), nearest_neighbors)
		return nearest_neighbors


	def _isPointAt(self, p_idx, pos, defaultSize=None):
		if not (0 <= p_idx < self.xData.size):
			return False

		# point = self.data[p_idx]
		ss = defaultSize
		'''ss = point['symbolSize']
		if ss < 0 or ss == self.opts['symbolSize']:
			ss = defaultSize
		else:
			assert ss <= self.opts['symbolSize']
			ss = self._getPointSize(point)'''

		# Correct point distance by (per-dimension) scaling factor
		dx = (pos.x() - self.xData[p_idx]) / ss.x()
		dy = (pos.y() - self.yData[p_idx]) / ss.y()

		return (dx * dx + dy * dy) <= 1


	def _getPointSize(self, point=None):
		if point is not None:
			ss = point['symbolSize']
		else:
			ss = -1
		if ss < 0:
			ss = self.opts['symbolSize']

		ssx = ssy = ss * 0.5
		if self.opts['pxMode']:
			pv = self.pixelVectors()
			ssx *= pv[0].x()
			ssy *= pv[1].y()

		return pg.Point(ssx, ssy)


class SelectableScatterPlotItem(TreeScatterPlotItem):

	def __init__(self, *args, **kargs):
		self.selection = None
		super().__init__(*args, **kargs)
		self.selection = DataSelection(self.data_tree.data, kargs.get('statKeys'))
		self.opts['selectedBrush'] = QtGui.QBrush(QtGui.QColor(0xffffff))


	def clear(self):
		super().clear()
		if self.selection is not None:
			self.selection.clear()
			self.selection.dataset = None


	def addPoints(self, *args, **kargs):
		super().addPoints(*args, **kargs)
		if self.selection is not None:
			self.selection.dataset = self.data_tree.data


	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			pt_idx = next(iter(self.pointsAt(ev.pos())), None)
			if pt_idx is not None:
				pt = self.point(pt_idx)
				selected = self.selection.flip(pt_idx)
				selected = 'selectedBrush' if selected else 'brush'
				pt.setBrush(self.opts[selected])

				self.sigClicked.emit(self, (pt,))
				ev.accept()
				return

		ev.ignore()
