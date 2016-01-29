from PyQt4.QtGui import QWidget
import cluster_ui
import os.path
import csv
import numpy as np
import sklearn.cluster as cl
import matplotlib.pyplot as plt

_bindir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
csvpath = _bindir + '/data/dust-2014-grainsize.dat'
january_rows = 39388
cols = 31
grainsizes = np.empty([january_rows, cols])

with open(csvpath, 'r') as csvfile:
	csvreader = csv.reader(csvfile, delimiter=';')
	next(csvfile)
	rowindex = 0
	for row in csvreader:
		grainsizes[rowindex, :] = [int(x) for x in row[1:]]
		rowindex += 1
		if rowindex == january_rows-1:  # whole january
			break


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
		meanGrainSizes = np.empty([int(january_rows/(60*timeInterval)), 31])
		for r in range(0, meanGrainSizes.shape[0]-1):
			meanGrainSizes[r, :] = np.mean(grainsizes[r*60*timeInterval:(r+1)*60*timeInterval-1,:], axis=0)

		centroids = cl.k_means(meanGrainSizes, histogramCount)
		fig = plt.figure(figsize=(10,10))
		plt.bar(range(0,31), centroids[0][0])
		plt.show()
