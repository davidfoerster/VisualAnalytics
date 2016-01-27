from PyQt4.QtGui import QWidget
import cluster_ui
import os.path
import csv
import numpy as np

_bindir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
csvpath = _bindir + '/data/dust-2014-grainsize.dat'
grainsizes = np.array([])
with open(csvpath, 'r') as csvfile:
	csvreader = csv.reader(csvfile, delimiter=';')
	next(csvfile)
	rowindex = 1
	for row in csvreader:
		grainsizes.append([int(x) for x in row[1:]])
		rowindex += 1
		if rowindex > 39388:  # whole january
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
		pass
