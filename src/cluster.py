from PyQt4.QtGui import QWidget
import cluster_ui
import os.path
import csv
import colorsys
import numpy as np
import sklearn.cluster as cl
import matplotlib.pyplot as plt

_bindir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
csvpath = _bindir + '/data/dust-2014-grainsize.dat'
rows = 425397
cols = 31
grainsizes = np.empty([rows, cols])

with open(csvpath, 'r') as csvfile:
	csvreader = csv.reader(csvfile, delimiter=';')
	next(csvfile)
	rowindex = 0
	for row in csvreader:
		grainsizes[rowindex, :] = [int(x) for x in row[1:]]
		rowindex += 1
		if rowindex == rows-1:  # whole january
			break


# from: http://stackoverflow.com/a/9701141
def get_colors(num_colors):
	colors = []
	for i in np.arange(0., 360., 360. / num_colors):
		hue = i/360.
		lightness = (50 + np.random.rand() * 10)/100.
		saturation = (90 + np.random.rand() * 10)/100.
		colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
	return colors


class ClusterWidget(QWidget, cluster_ui.Ui_Dialog):
	def __init__(self, btnCluster):
		super(ClusterWidget, self).__init__()
		self.btnCluster = btnCluster

	def closeEvent(self, event):
		self.btnCluster.setEnabled(True)
		self.hide()
		self.widForm.close()

	def onCluster(self):
		self.btnCluster.setEnabled(False)
		self.widForm = QWidget()
		self.wid = cluster_ui.Ui_Dialog()
		self.wid.setupUi(self.widForm)
		self.widForm.closeEvent = self.closeEvent
		self.widForm.show()
		self.wid.btnCancel.clicked.connect(self.closeEvent)
		self.wid.btnOk.clicked.connect(self.computeCluster)

	def computeCluster(self):
		histogramCount = self.wid.histogramCountSpinBox.value()
		timeInterval = self.wid.timeIntervalSpinBox.value()
		meanGrainSizes = np.empty([int(rows/(60*timeInterval)), 31])
		for r in range(0, meanGrainSizes.shape[0]-1):
			meanGrainSizes[r, :] = np.mean(grainsizes[r*60*timeInterval:(r+1)*60*timeInterval-1, :], axis=0)

		kmeans = cl.KMeans(n_clusters=histogramCount)
		kmeans.fit(meanGrainSizes)
		centroids = kmeans.cluster_centers_
		nrows = int(np.ceil(np.sqrt(histogramCount)))+1
		ncols = int(np.ceil(histogramCount/nrows))
		colors = get_colors(histogramCount)
		# sort by luminance (http://stackoverflow.com/a/596243)
		colors.sort(key=lambda rgb: 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2])
		# sort by lowest grain size
		centroids = sorted(centroids, key=lambda c: c[0], reverse=True)

		plt.figure(figsize=(15, 10))
		for i in range(0, histogramCount):
			ax = plt.subplot2grid((nrows, ncols), np.unravel_index(i+ncols, (nrows, ncols)))
			plt.bar(range(0, 31), centroids[i])
			ax.set_axis_bgcolor(tuple(colors[i]))

		dists = kmeans.transform(meanGrainSizes)
		labels = kmeans.labels_
		scale = 1 - np.divide(np.amin(dists, axis=1), np.amax(dists, axis=1))

		ax_line = plt.subplot2grid((nrows, ncols), (0, 0), colspan=ncols)
		ax_line.set_xlim(-.1, meanGrainSizes.shape[0]+.1)
		ax_line.set_ylim(0, 1.1)
		ax_line.set_xticks(range(0, meanGrainSizes.shape[0]-1, int((meanGrainSizes.shape[0]-1)/11)))
		ax_line.set_xticklabels(('Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'))

		for r in range(0, meanGrainSizes.shape[0]-1):
			plt.plot(r, scale[labels[r]], 'o', lw = 0, ms = timeInterval/5, color=colors[labels[r]])

		plt.show()
