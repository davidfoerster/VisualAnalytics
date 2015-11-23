from PyQt4.QtCore import Qt, QRectF
from PyQt4 import QtGui
from data_selection import DataSelection

import numpy as np
import pyqtgraph as pg
import scipy.spatial


class TreeScatterPlotItem(pg.ScatterPlotItem):

	def __init__(self, *args, **kargs):
		self.data_tree = None
		super().__init__(*args, **kargs)


	def addPoints(self, *args, **kargs):
		super().addPoints(*args, **kargs)
		data = self.data
		self.data_tree = scipy.spatial.cKDTree(np.vstack((data['x'], data['y'])).transpose())


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
		nearest_neighbors = self.data_tree.query(((pos.x(), pos.y()),), k, 0, 2, max(ss.x(), ss.y()))[1]
		nearest_neighbors = filter(lambda p: self._isPointAt(p, pos, ss), nearest_neighbors)
		return nearest_neighbors


	def _isPointAt(self, p_idx, pos, defaultSize=None):
		if not (0 <= p_idx < self.data.size):
			return False

		point = self.data[p_idx]
		ss = point['size']
		if ss < 0 or ss == self.opts['size']:
			ss = defaultSize
		else:
			assert ss <= self.opts['size']
			ss = self._getPointSize(point)

		# Correct point distance by (per-dimension) scaling factor
		dx = (pos.x() - point['x']) / ss.x()
		dy = (pos.y() - point['y']) / ss.y()

		return (dx * dx + dy * dy) <= 1


	def _getPointSize(self, point=None):
		if point is not None:
			ss = point['size']
		else:
			ss = -1
		if ss < 0:
			ss = self.opts['size']

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

		selected_pen = self.opts.get('selectedPen')
		if selected_pen is None:
			selected_pen = QtGui.QPen(Qt.DashLine)
			selected_pen.setColor(QtGui.QColor(0xffffff))
			self.opts['selectedPen'] = selected_pen

		self.drag_rectangle = QtGui.QGraphicsRectItem()
		self.drag_rectangle.setPen(selected_pen)


	def itemChange(self, change, value):
		value = super().itemChange(change, value)

		if change == self.ItemSceneChange:
			if value is not self.scene():
				if value is not None:
					value.addItem(self.drag_rectangle)
				else:
					self.scene().removeItem(self.drag_rectangle)

		return value


	def clear(self):
		super().clear()
		if self.selection is not None:
			self.selection.clear()
			self.selection.dataset = None


	def addPoints(self, *args, **kargs):
		super().addPoints(*args, **kargs)
		if self.selection is not None:
			self.selection.dataset = self.data_tree.data


	def _setSelectionBrush(self, selected, *p_idxs):
		if selected:
			brush = self.opts['selectedPen'].brush()
		else:
			brush = self.opts['brush']
		for i in p_idxs:
			self.point(i).setBrush(brush)


	def mouseClickEvent(self, ev):
		if ev.button() == Qt.LeftButton:
			pt_idx = next(iter(self.pointsAt(ev.pos())), None)
			if pt_idx is not None:
				pt = self.point(pt_idx)
				selected = self.selection.flip(pt_idx)
				self._setSelectionBrush(selected, pt_idx)

				self.sigClicked.emit(self, (pt,))
				ev.accept()
				return

		ev.ignore()


	def mouseDragEvent(self, ev):
		rect_item = self.drag_rectangle

		if not ev.isFinish():
			rect_item.setRect(QtCore.QRectF(ev.buttonDownScenePos(), ev.scenePos()).normalized())
			rect_item.show()
		else:
			rect_item.hide()

		ev.accept()
