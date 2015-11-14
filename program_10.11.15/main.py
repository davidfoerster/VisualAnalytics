from PyQt4.QtGui import *
import widgetwin
import window_ui
import pyqtgraph as pg
import numpy as np
import sys

'''
dtype legt den Datentyp der Spalten fest -> |S19 erzeugt aber keinen String sondern einen Bytestrom vom Format b'2014-01-01 00:00:00'
names=["date", "small", "large"] legt die Namen der Spalten fest

Weil die Ladedauer sehr hoch ist, wird erstmal nur der Datensatz mit allen Messdaten aus Januar verwendet. Beachtet dies bei den Filtern.
'''
data = np.genfromtxt('January.txt', dtype=[('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter=';',
                     names=["date", "small", "large"])

# Wandelt die Byte Daten aus data['date'] in Strings um
data['date'] = map(bytes.decode, data['date'])

# x_var = data['small']
# y_var = data['large']

# TODO: was ist mit Schaltjahren?
# Liste mit Tagen und dazu gehörenden Datum zB Tag 365 ist der 2014-12-31
day = np.genfromtxt('DateInDays.txt', dtype=[('day', '|i8'), ('date', 'S10')], delimiter=',',
                    names=["sliderDay", "sliderDate"])


class MainWindow(QMainWindow, window_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


'''
Plottet die Daten, welche in 'data' stehen.
Filter-Button öffnet das Filter-Fenster
Quit-Button schließt die Anwendung
'''
class Plot:
    def __init__(self):
        self.form = MainWindow()
        self.form.move(300, 300)
        self.scatterpoints = pg.ScatterPlotItem(data['small'], data['large'], pen=None, symbol='o', autoDownsample=True)
        self.form.graphicsView.addItem(self.scatterpoints)
        self.form.graphicsView.setLabel(axis='left', text='large')
        self.form.graphicsView.setLabel(axis='bottom', text='small')
        self.form.show()
        self.tooltip = pg.TextItem(text='', color=(176, 127, 255), anchor=(1, 1))
        self.form.graphicsView.addItem(self.tooltip)
        self.tooltip.hide()
        self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)
        self.form.btnFilter.clicked.connect(self.onfilterWindow)
        self.form.btnQuit.clicked.connect(self.onQuit)

    def onMove(self, pos):
        act_pos = self.scatterpoints.mapFromScene(pos)
        pts = self.scatterpoints.pointsAt(act_pos)
        if len(pts) != 0:
            self.tooltip.setText('small=%d\nlarge=%d' % (pts[0].pos()[0], pts[0].pos()[1]))
            # anchor des Tooltips anpassen, sodass Tooltip nicht aus dem Graph faellt
            self.tooltip.setPos(pts[0].pos())
            self.tooltip.show()
        else:
            self.tooltip.hide()

    '''
    Das Filter-Fenster: besteht aus tabWidget mit 2 Reitern
     Reiter Filter by Month/Day: treeWidget mit der Filterung von Monat und Tag. Ohne Tagangabe wird der komplette Monat gewählt
     Reiter Filter by Range: Über zwei Slider kann ein Startdatum und Enddatum ausgewählt werden
    OK-Button funktioniert nur, wenn ein Filter gewählt wurde
    Cancel-Button schließt das Filter-Fenster
    '''
    def onfilterWindow(self):
        print("Filter")
        self.widForm = QWidget()
        self.widForm.move(1110, 300)
        self.wid = widgetwin.Ui_Form()
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

    '''
    Sucht die Messdaten welche im Filter 'Filter by Month/Day' ausgewählt wurden
    1. onOkMonth: Baue Suchstring, bestehend aus Monat und Tag, zusammen
    2. filterMonth: Suche im Datensatz nach alle zutreffenden Messdaten
    3. plot(self, filter): Plotten der Daten
    '''
    def onOkMonth(self):
        if len(self.wid.labMonth.text()) > 1:
            strMonth = self.wid.labMonth.text()
            if strMonth == 'January':
                print("January")
                self.filterMonth('2014-01' + '-' + self.wid.labDay.text())

            # Nur Januar funktioniert bisher zu Testzwecken
            elif strMonth == 'February':
                print("February")
                self.plot('daten-sehr-klein.dat')
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
        small = []
        large = []
        date = data['date']
        for s in date:
            if timeInterval in s:
                index = date.index(s)
                small.append(str(data[index][1]))
                large.append(str(data[index][2]))

        if len(small) > 0:
            self.plotFilterRange(small, large)
        else:
            msgBox = QMessageBox()
            msgBox.setText("No data exists for the filter!")
            msgBox.exec_()

    '''
    Kann verwendet werden, wenn ein kompletter Monat ausgewählt wurde
    Parameter 'filter' muss eine Datei sein
    '''
    def plot(self, filter):
        # def plot(self, small, large):
        self.form = MainWindow()
        self.form.move(300, 300)
        new_data = np.genfromtxt(filter, dtype=[('date', '|S19'), ('small', 'i8'), ('large', 'i8')], delimiter=';',
                                 names=["date", "small", "large"])
        self.scatterpoints = pg.ScatterPlotItem(new_data['small'], new_data['large'], pen=None, symbol='o')
        # self.scatterpoints = pg.ScatterPlotItem(small, large, pen=None, symbol='o')
        self.form.graphicsView.addItem(self.scatterpoints)
        self.form.graphicsView.setLabel(axis='left', text='large')
        self.form.graphicsView.setLabel(axis='bottom', text='small')
        self.form.show()
        self.tooltip = pg.TextItem(text='', color=(176, 127, 255), anchor=(1, 1))
        self.form.graphicsView.addItem(self.tooltip)
        self.tooltip.hide()
        self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)
        self.form.btnFilter.clicked.connect(self.onfilterWindow)
        self.form.btnQuit.clicked.connect(self.onQuit)

    '''
    Jeder Cancel-Button blendet das Filter-Fenster aus
    '''
    def onCancel(self):
        self.widForm.close()

    '''
    Quit-Button schließt die Anwendung
    '''
    def onQuit(self):
        self.widForm.close()
        sys.exit()

    '''
    Sucht alle Messdaten in gegeben Zeitraum (von 'fromValue' bis 'toValue')
    1. onOkFilterSlider: Prüfe ob fromValue < toValue ist, ansonsten tausche die Werte und ändere Slider
       danach suche alle Messdaten im Zeitraum
    2. plotFilterRange(self, small, large): Plotten der Daten. Small/Large = Liste allen kleinen/großen Partikel
    '''
    def onOkFilterSlider(self):
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

        plotDays = []
        small = []
        large = []
        print(fromDate)
        print(toDate)
        isStarted = False
        date = data['date']
        for s in date:
            if toDate in s:
                break
            else:
                if (fromDate in s) or isStarted:
                    isStarted = True
                    index = date.index(s)
                    res = [data[index][0], str(data[index][1]), str(data[index][2])]
                    small.append(res[1])
                    large.append(res[2])
                    plotDays.append(res)

        if (len(small) > 0):
            self.plotFilterRange(small, large)
        else:
            print("Keine Daten: Plot2")

    def plotFilterRange(self, small, large):
        self.form = MainWindow()
        self.form.move(300, 300)
        self.scatterpoints = pg.ScatterPlotItem(small, large, pen=None, symbol='o')
        self.form.graphicsView.addItem(self.scatterpoints)
        self.form.graphicsView.setLabel(axis='left', text='large')
        self.form.graphicsView.setLabel(axis='bottom', text='small')
        self.form.show()
        self.tooltip = pg.TextItem(text='', color=(176, 127, 255), anchor=(1, 1))
        self.form.graphicsView.addItem(self.tooltip)
        self.tooltip.hide()
        self.scatterpoints.scene().sigMouseMoved.connect(self.onMove)
        self.form.btnFilter.clicked.connect(self.onfilterWindow)
        self.form.btnQuit.clicked.connect(self.onQuit)

    '''
    Wandelt die Byte-Daten in Strings um
    '''
    def getDateFromDay(self, chooseDay):
        sliderDate = day['sliderDate']
        chooseDateByte = sliderDate[chooseDay]
        chooseDate = chooseDateByte.decode("utf-8")
        return chooseDate

    '''
    Setzen des From-Sliders bei Änderung
    '''
    def setFrom(self):
        chooseDay = self.wid.sliderFrom.value()
        chooseDate = self.getDateFromDay(chooseDay)
        print(chooseDate)
        self.wid.labFrom.setText(chooseDate)

    '''
    Setzen des To-Sliders bei Änderung
    '''
    def setTo(self):
        chooseDay = self.wid.sliderTo.value()
        chooseDate = self.getDateFromDay(chooseDay)
        self.wid.labTo.setText(chooseDate)


app = QApplication(sys.argv)
myplot = Plot()
app.exec_()
