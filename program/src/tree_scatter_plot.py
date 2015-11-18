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


	def pointsAt(self, pos, k=1):
		ss = self._getPointSize(None)
		nearest_neighbors = self.data_tree.query([[pos.x(), pos.y()]], k, 0, 2, max(ss.x(), ss.y()))[1]
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
