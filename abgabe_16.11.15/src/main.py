from PyQt4.QtGui import *
import widgetwin_ui
import window_ui
import pyqtgraph as pg
import numpy as np
import scipy.spatial
import sys


def _main(*args):
    """
    dtype legt den Datentyp der Spalten fest -> |S19 erzeugt aber keinen String sondern einen Bytestrom vom Format b'2014-01-01 00:00:00'
    names=["date", "small", "large"] legt die Namen der Spalten fest

    Weil die Ladedauer sehr hoch ist, wird erstmal nur der Datensatz mit allen Messdaten aus Januar verwendet. Beachtet dies bei den Filtern.
    """

    data_path = args[0] if args else 'data/January.txt'
    data = np.genfromtxt(data_path,
                         dtype=[('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter=';',
                         names=["date", "small", "large"])

    app = QApplication(sys.argv)
    myplot = Plot(data)
    app.exec_()


# TODO: was ist mit Schaltjahren?
# Liste mit Tagen und dazu gehörenden Datum zB Tag 365 ist der 2014-12-31
day = np.genfromtxt('data/DateInDays.txt', dtype=[('day', '|i8'), ('date', 'S10')], delimiter=',',
                    names=["sliderDay", "sliderDate"])


class MainWindow(QMainWindow, window_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


class Plot:
    """
    Plottet die Daten, welche in 'data' stehen.
    Filter-Button öffnet das Filter-Fenster
    Quit-Button schließt die Anwendung
    """


    def __init__(self, data=None):
        self.data = data
        self.form = None
        self.scatterpoints = None
        self.tooltip = None
        self.scene = QGraphicsScene()
        self.pen = QPen(QColor(0, 0, 255))

        self.original_data = self.data
        self.new_data = self.data
        self.undo_data1 = self.new_data
        self.undo_data2 = self.undo_data1
        #print("len: ",len(self.new_data))
        self.selectedPoints = []

        #Globale Variablen für Average
        self.average = ()

        if data is not None:
            self.plotFilterRange(data['small'], data['large'], data['date'], autoDownsample=True)


    def onMove(self, scene_pos):
        self.selectedPoint = ()
        tooltipDate = ''
        pos = self.scatterpoints.mapFromScene(scene_pos)

        ss = self.scatterpoints.opts['size']
        ssx = ssy = ss * 0.5
        if self.scatterpoints.opts['pxMode']:
            pv = self.scatterpoints.pixelVectors()
            ssx *= pv[0].x()
            ssy *= pv[1].y()
        else:
            pv = None

        nearest_neighbor_idx = self.data_tree.query([[pos.x(), pos.y()]], distance_upper_bound=max(ssx, ssy))[1][0]

        if 0 <= nearest_neighbor_idx < self.data.size:
            s = self.scatterpoints.data[nearest_neighbor_idx]
            sx = s['x']
            sy = s['y']
            date_of_point = self.data['date'][nearest_neighbor_idx]

            ss2 = s['size']
            if ss2 > 0 and ss2 != ss:
                ss = ss2
                assert ss <= self.scatterpoints.opts['size']
                ssx = ssy = ss * 0.5
                if pv is not None:
                    ssx *= pv[0].x()
                    ssy *= pv[1].y()

            if abs(pos.x() - sx) <= ssx and abs(pos.y() - sy) <= ssy:
                tooltipDate = date_of_point.decode("utf-8")
                self.selectedPoint = (date_of_point, int(sx), int(sy))
                #print(date_of_point,sx,sy)
                if self.selectedPoint not in self.selectedPoints:
                    self.selectedPoints.append(self.selectedPoint)
                    self.average = self.calculateAverage(self.selectedPoints)

                self.tooltip.setText('small={0:d}\nlarge={1:d}\ndate={2:s}\naverageSmall={3:.3f}\naverageLarge={4:.3f}'.format(int(sx), int(sy), tooltipDate, self.average[0], self.average[1]))
                # anchor des Tooltips anpassen, sodass Tooltip nicht aus dem Graph faellt
                self.tooltip.setPos(pos)
                self.tooltip.show()
                return

        self.tooltip.hide()

    def calculateAverage(self, points):
        sumS = 0
        sumL = 0
        i = 0
        #Null Elemente werden im Durchschnitt nicht mitberechnet
        for p in points:
            if (p[1] > 0) | (p[2] > 0):

                sumS = sumS + p[1]
                sumL = sumL + p[2]
            elif len(points)> 1:
                i = i+1

        averageSmall = sumS / (len(points)-i)
        averageLarge = sumL / (len(points)-i)
        #print("averageSmall: ", averageSmall)
        #print("averageLarge: ", averageLarge)

        return (averageSmall, averageLarge)


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
        child_count = topLevelItem.childCount()
        childs = []

        for i in range(child_count):
            item = topLevelItem.child(i)
            childs.append(item)

        # Sliders
        self.wid.sliderTo.setValue(365)
        self.wid.sliderFrom.valueChanged.connect(self.setFrom)
        self.wid.sliderTo.valueChanged.connect(self.setTo)
        self.widForm.show()

        # TreeWidget
        self.wid.treeWidget.itemClicked.connect(lambda: self.onItemClick(childs))

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

            # Nur Januar funktioniert bisher zu Testzwecken
            elif strMonth == 'February':
                print("February")
                self.filterMonth('2014-02' + '-' + self.wid.labDay.text())
            elif strMonth == 'March':
                print("March")
                self.filterMonth('2014-03' + '-' + self.wid.labDay.text())
            elif strMonth == 'April':
                print("April")
                self.filterMonth('2014-04')
            elif strMonth == 'May':
                print("May")
                self.filterMonth('2014-05')
            elif strMonth == 'June':
                print("June")
                self.filterMonth('2014-06')
            elif strMonth == 'July':
                print("July")
                self.filterMonth('2014-07')
            elif strMonth == 'August':
                print("August")
                self.filterMonth('2014-08')
            elif strMonth == 'September':
                print("September")
                self.filterMonth('2014-09')
            elif strMonth == 'October':
                print("October")
                self.filterMonth('2014-10')
            elif strMonth == 'November':
                print("November")
                self.filterMonth('2014-11')
            elif strMonth == 'December':
                print("December")
                self.filterMonth('2014-12')


    def filterMonth(self, timeInterval):
        self.undo_data2 = self.undo_data1
        self.undo_data1 = self.new_data
        self.new_data = self.original_data
        print(timeInterval)
        index = 0
        for s in  self.new_data:
            decode_date = s[0].decode("utf-8")

            if timeInterval not in decode_date:
                self.new_data = np.delete( self.new_data, index)
                index=index-1 #new_data wird kleiner, darum darf der Index nicht wachsen.
            index = index+1
        if(len(self.new_data) > 0):
            print("len new_data: ",len(self.new_data))
            self.data = self.new_data
            if len(self.data)>0:
                self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample=True)
        else:
            msgBox = QMessageBox()
            msgBox.setText("No data exists for the filter!")
            msgBox.exec_()


    def plot(self, filter):
        """
        Kann verwendet werden, wenn ein kompletter Monat ausgewählt wurde
        Parameter 'filter' muss eine Datei sein
        """

        new_data = np.genfromtxt(filter, dtype=[('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter=';',
                                 names=["date", "small", "large"])
        self.plotFilterRange(new_data['small'], new_data['large'])

    def onDelete(self):

        if(len(self.selectedPoints)>0):
            self.undo_data2 = self.undo_data1
            self.undo_data1 = self.new_data #undo_data1 speichert die Datenmenge vor dem Bearbeiten
            index = 0
            for s in self.new_data:
                for p in self.selectedPoints:
                    if p[0] == s[0]:
                        self.new_data = np.delete(self.new_data, index)
                        index=index-1 #new_data wird kleiner, darum darf der Index nicht wachsen.
                        del self.selectedPoints[self.selectedPoints.index(p)]
                index = index+1
            print("len delete: ",len(self.new_data))
            self.data = self.new_data #somit kann weiterhin mit data['small'] und data['large'] gearbeitet werden.

            self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample=True)

    def undoFunction(self):

        self.new_data = self.undo_data1
        self.undo_data1 = self.undo_data2
        self.data = self.new_data
        self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample=True)

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

        isDeletePoint = True #Alle Punkte die nicht im Filterzeitraum liegen, werden aus der Datenmenge gelöscht
        self.undo_data2 = self.undo_data1
        self.undo_data1 = self.new_data
        self.new_data = self.original_data
        index = 0
        for s in self.new_data:
            decode_date = s[0].decode("utf-8")

            if((fromDate in decode_date) & isDeletePoint):
                isDeletePoint = False

            if((toDate in decode_date) & (not isDeletePoint)):
                isDeletePoint = True

            if(isDeletePoint):
                self.new_data = np.delete( self.new_data, index)
                index=index-1 #new_data wird kleiner, darum darf der Index nicht wachsen.

            index = index+1
        if(len(self.new_data) > 0):
            print("len new_data: ",len(self.new_data))
            self.data = self.new_data
            if len(self.data)>0:
                self.plotFilterRange(self.data['small'], self.data['large'], self.data['date'], autoDownsample=True)
        else:
            msgBox = QMessageBox()
            msgBox.setText("No data exists for the filter!")
            msgBox.exec_()

        '''
        plotDays = []
        small = []
        large = []
        dates = []
        print(fromDate)
        print(toDate)
        isStarted = False

        for s in self.data['date']:
            if toDate in s:
                break
            else:
                if (fromDate in s) or isStarted:
                    isStarted = True
                    index = date.index(s)
                    res = [self.data[index][0], str(self.data[index][1]), str(self.data[index][2])]
                    dates.append(res[0])
                    small.append(res[1])
                    large.append(res[2])
                    plotDays.append(res)

        if (len(small) > 0):
            self.plotFilterRange(small, large, dates)
        else:
            print("Keine Daten: Plot2")

        '''


    def plotFilterRange(self, small, large, dates, **kwargs):
        self.data_tree = scipy.spatial.cKDTree(np.vstack((small, large)).transpose())
        self.form = MainWindow()
        #self.form.move(300, 300)
        self.form.timeline.setScene(self.scene)
        self.form.timeline.setSceneRect(0, 0, 710, 10)

        dayIndices = list(map(lambda x: x[1], day))
        dayIndex = -1
        for d in dates:
            d = d[0:10]  # b'2014-01-01 00:00:00' => b'2014-01-01'
            if dayIndex != dayIndices.index(d):
                dayIndex = dayIndices.index(d)
                rect = self.scene.addRect(2*dayIndex, 1, 1, 10, self.pen)
                rect.setToolTip(bytes.decode(d))

        self.scatterpoints = pg.ScatterPlotItem(small, large, pen=None, symbol='o', **kwargs)
        self.form.graphicsView.addItem(self.scatterpoints)
        self.form.graphicsView.setLabel(axis='left', text='large')
        self.form.graphicsView.setLabel(axis='bottom', text='small')
        self.form.graphicsView.showGrid(True, True)
        self.form.show()
        self.tooltip = pg.TextItem(text='', color=(176, 127, 255), anchor=(1, 1))
        self.form.graphicsView.addItem(self.tooltip)
        self.tooltip.hide()
        self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)
        self.form.btnFilter.clicked.connect(self.onfilterWindow)
        self.form.btnQuit.clicked.connect(self.onQuit)
        self.form.btnDelete.clicked.connect(self.onDelete)
        self.form.btnUndo.clicked.connect(self.undoFunction)
        print("len Filter: ",len(self.new_data))

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
