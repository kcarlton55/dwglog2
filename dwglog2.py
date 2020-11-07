#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:49:28 2020

@author: ken

https://www.youtube.com/watch?v=kKNINH-Nf8w&t=7s
"""


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import *
import sys
import sqlite3
import os
from datetime import datetime, date

__version__ = '0.1'
__author__ = 'Kenneth E. Carlton'


class InsertDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(InsertDialog, self).__init__(*args, **kwargs)
           
        self.setWindowTitle('Insert Part Data')
        self.setFixedWidth(350)
        self.setFixedHeight(150)
        
        layout = QVBoxLayout()
        
        self.partinput = QLineEdit()
        self.partinput.setPlaceholderText('Part No. (e.g., will autofill: 0300- or 0300)')
        self.partinput.setMaxLength(30)
        layout.addWidget(self.partinput)
                
        self.descriptioninput = QLineEdit()
        self.descriptioninput.setPlaceholderText('Description')
        self.descriptioninput.setMaxLength(40)
        layout.addWidget(self.descriptioninput)
                

# =============================================================================
#         self.authorinput = QLineEdit()
#         self.authorinput.setPlaceholderText('Author')
#         layout.addWidget(self.authorinput)
# =============================================================================

        
        self.QBtn = QPushButton('text-align:center')
        self.QBtn.setText("OK")
        self.QBtn.setMaximumWidth(75)
        self.QBtn.clicked.connect(self.addpart)   
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtn)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def addpart(self):
        part = ""
        description = ""
        author = "unknown"
        
        if os.getenv('USERNAME'):
            author = os.getenv('USERNAME')  # Works only on MS Windows
            author.replace('_', '')         
        
        #dwgno, part = generate_nos(part)
        #dwgno = '091088'
        
        part = self.partinput.text().upper().strip()
        description = self.descriptioninput.text().upper().strip()
        now = datetime.now()
        _date = now.strftime("%Y-%m-%d %H:%M:%S")
        # _date = date.today()
<<<<<<< HEAD
        #author = self.authorinput.text()
=======
        author = self.authorinput.text()
>>>>>>> 7e4232f68a8f716213c57e4ab8f7714beda4bd75
        
        try:
            self.conn = sqlite3.connect('dwglog2.db')
            self.c = self.conn.cursor()
<<<<<<< HEAD
            
            # self.c.execute("SELECT MAX(dwg) FROM ptnos")
            # result = self.c.fetchone()[0]
            self.c.execute("SELECT dwg FROM ptnos")
            result = self.c.fetchall()
=======
            self.c.execute("SELECT MAX(dwg) FROM ptnos") 
            result = self.c.fetchone()[0]
>>>>>>> 7e4232f68a8f716213c57e4ab8f7714beda4bd75
            dwgno, part = generate_nos(result, part)       
            self.c.execute("INSERT INTO ptnos (dwg, part, description, Date, author) VALUES (?,?,?,?,?)",
                           (dwgno, part, description, _date,author))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            self.close()
        except TypeError:
            year = date.today().year
            dwgno, part  = str(year*1000), 'Invalid part no.'
            self.c.execute("INSERT INTO ptnos (dwg, part, description, Date, author) VALUES (?,?,?,?,?)",
                           (dwgno, part, description, _date,author))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            self.close()
            QMessageBox.warning(QMessageBox(), 'Error', 'No initial drawing number was found to begin from.  '
                          'Will create a new one.  Possibly the error is a result of a new, empty, database '
                          'file (dwglog2.db) having just been created?  Edit the new drawing number that '
                          'is about to be created to adjust the start point.  Make it something like 2020305 '
                          '(7 or 8 characters, all digits, the first 4 digits are the current year).')
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add pt no. to the database')
            
class SearchDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText('Search')
        
        self.setWindowTitle('Seach part')
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.searchpart)
        layout = QVBoxLayout()
        
        self.searchinput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.searchinput.setValidator(self.onlyInt)
        self.searchinput.setPlaceholderText('Dwg No.')
        layout.addWidget(self.searchinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def searchpart(self):
        #https://stackoverflow.com/questions/30732480/sqlite-where-clause-for-every-column
        searchrol = ""
        searchrol = self.searchinput.text()
        try:
            self.conn = sqlite3.connect("dwglog2.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from ptnos WHERE dwg=" + str(searchrol))
            row = result.fetchone()
            searchresult = ("Dwgno: " + str(row[1]) + '\nPart: ' + str(row[2]) +
                            '\nDescription: ' + str(row[3]) + 
                            '\nDate: ' + str(row[4]) + '\nAuthor: ' + str(row[5]))
            QMessageBox.information(QMessageBox(), 'Successful', searchresult)
            self.conn.commit()
            self.c.close()
            self.conn.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not Find ptnos from the dwglog2 database.')
 
<<<<<<< HEAD
            
class SearchDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText('Search')
        
        self.setWindowTitle('Seach part')
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.searchpart)
        layout = QVBoxLayout()
        
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('Dwg No.')
        layout.addWidget(self.searchinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def searchpart(self):
        #https://stackoverflow.com/questions/30732480/sqlite-where-clause-for-every-column
        searchterm = ""
        searchterm = self.searchinput.text()
        try:
            self.conn = sqlite3.connect("dwglog2.db")
            self.c = self.conn.cursor()
# =============================================================================
#             result = self.c.execute("SELECT * from ptnos WHERE ((dwg+part+description+date+author) LIKE " 
#                                     + str("'%" + searchterm + "%'") + ')')
# =============================================================================
            print('aaa')
            sqlSelect = ("SELECT * from ptnos WHERE " +
                         "(dwg LIKE %" + searchterm + "%) OR " +
                         "(part LIKE %" + searchterm + "%)")
            
            sqlSelect = ("SELECT * from ptnos WHERE " +
                         "dwg LIKE %" + searchterm + "%")
            print(sqlSelect)
            
            result = self.c.execute(sqlSelect)
            

            row = result.fetchone()
            print(row)
# =============================================================================
#             searchresult = ("Dwgno: " + str(row[1]) + ', Part: ' + str(row[2]) +
#                             ', Descrip: ' + str(row[3]) + 
#                             ', Date: ' + str(row[4]) + ', Author: ' + str(row[5]))
# =============================================================================
            searchresult = row[0] + row[1] + row[2] + row[3] + row[4]
            
            print('ccc')
=======
            
class SearchDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText('Search')
        
        self.setWindowTitle('Seach part')
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.searchpart)
        layout = QVBoxLayout()
        
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('Dwg No.')
        layout.addWidget(self.searchinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def searchpart(self):
        #https://stackoverflow.com/questions/30732480/sqlite-where-clause-for-every-column
        searchterm = ""
        searchterm = self.searchinput.text()
        try:
            self.conn = sqlite3.connect("dwglog2.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from ptnos WHERE ((dwg) LIKE" 
                                    + str("'%" + searchterm + "%'") + ')')
            

            row = result.fetchone()
            searchresult = ("Dwgno: " + str(row[1]) + ', Part: ' + str(row[2]) +
                            ', Descrip: ' + str(row[3]) + 
                            ', Date: ' + str(row[4]) + ', Author: ' + str(row[5]))
>>>>>>> 7e4232f68a8f716213c57e4ab8f7714beda4bd75
            
            #QMessageBox.set
            QMessageBox.information(QMessageBox(), 'Successful', searchresult)
            self.conn.commit()
            self.c.close()
            self.conn.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not find ' + searchterm)
     
class DeleteDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText("Delete")
        
        self.setWindowTitle("Delete Part")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        self.QBtn.clicked.connect(self.deletepart)
        layout = QVBoxLayout()
        
        self.deleteinput = QLineEdit()
        self.onlyInt = QIntValidator()
        self.deleteinput.setValidator(self.onlyInt)
        self.deleteinput.setPlaceholderText('Dwg No.')
        layout.addWidget(self.deleteinput)
        layout.addWidget(self.QBtn)
        self.setLayout(layout)
        
    def deletepart(self):
        deldwg = ""
        deldwg = self.deleteinput.text()
        try:
            self.conn = sqlite3.connect('dwglog2.db')
            self.c = self.conn.cursor()
            self.c.execute('DELETE from ptnos WHERE dwg = ' + str(deldwg))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(), 'Successful', 'Deleted From Table Successful')
            self.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not Delete ptno from the database.')
            
            
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        
        self.setFixedWidth(500)
        self.setFixedHeight(250)
        
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.regected.connect(self.reject)
        
        layout = QVBoxLayout()
        
        self.setWindowTitle('About')
        title = QLabel('Dekker Drawing Log 2')
        font = title.font()
        font.setPointSize(20)
        title.setFoxt(font)
        
        labelpic = QLabel()
        pixmap = QPixmap('icon/dexter.jpg')
        pixmap = pixmap.scaledToWidth(275)
        labelpic.setPixmap(pixmap)
        labelpic.setFixedHeight(150)
        
        layout.addWidget(title)
        
        layout.addWidget(QLabel('version ' + __version__))
        layout.addWidget(labelpic)
        
        layout.addWidget(self.buttonBox)
        
        
        self.setLayout(layout)
        
        
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('icon/dwglog2.ico'))
        
        self.conn = sqlite3.connect('dwglog2.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS 
                        ptnos(dwg TEXT PRIMARY KEY NOT NULL UNIQUE, part TEXT, 
                        description TEXT, date TEXT NOT NULL, author TEXT)''')
        self.c.close()
        
        file_menu = self.menuBar().addMenu('&File')
        
        help_menu = self.menuBar().addMenu('&About')
        self.setWindowTitle('Dekker Drawing Log 2')
        self.setMinimumSize(850, 600)
        #self.setMaximumSize(800, 1200)
        
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(5)
        
        #self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        #self.tableWidget.resizeColumnsToContents()
        
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 335)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 30)
        
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)

        #self.tableWidget.verticalHeader().setStretchLastSection(False)
        #https://forum.qt.io/topic/3921/solved-qtablewidget-columns-with-different-width/4
# =============================================================================
#         self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
#         self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
#         self.tableWidget.horizontalHeader().setStretchLastSection(True)
#         self.tableWidget.verticalHeader().setVisible(False)
#         self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
#         self.tableWidget.verticalHeader().setStretchLastSection(False)
# =============================================================================
        self.tableWidget.setHorizontalHeaderLabels(('Dwg No.', 'Part No.',
                                            'Description', 'Date', 'Author'))
        
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        btn_ac_addpart = QAction(QIcon('icon/add2.png'), 'AddPart', self)  # add part icon
        btn_ac_addpart.triggered.connect(self.insert)
        btn_ac_addpart.setStatusTip('Add Part')
        toolbar.addAction(btn_ac_addpart)
        
        btn_ac_refresh = QAction(QIcon('icon/r3.png'), 'Refresh', self)  # refresh icon
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip('Refresh Table')
        toolbar.addAction(btn_ac_refresh)
 
        btn_ac_search = QAction(QIcon('icon/s1.png'), 'Search', self)  #search icon
        btn_ac_search.triggered.connect(self.search)
        btn_ac_search.setStatusTip('Search Parts')
        toolbar.addAction(btn_ac_search)
       

        
        btn_ac_delete = QAction(QIcon('icon/d1.png'), 'Delete', self)
        btn_ac_delete.triggered.connect(self.delete)
        btn_ac_delete.setStatusTip('Delete Part')
        toolbar.addAction(btn_ac_delete)

#-----------
        
<<<<<<< HEAD
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('Text to search for')
        self.searchinput.setMaxLength(40)
        self.searchinput.returnPressed.connect(self.searchpart)
        toolbar.addWidget(self.searchinput)
        
        

    
#-----------        
        
        addpart_action = QAction(QIcon('icon/add2.png'), 'Insert Part', self)
        addpart_action.triggered.connect(self.insert)
        file_menu.addAction(addpart_action)
        
        searchpart_action = QAction(QIcon('icon/s1.png'), 'Search Parts', self)
        searchpart_action.triggered.connect(self.search)
        file_menu.addAction(searchpart_action)
        
=======
        addpart_action = QAction(QIcon('icon/add2.png'), 'Insert Part', self)
        addpart_action.triggered.connect(self.insert)
        file_menu.addAction(addpart_action)
        
        searchpart_action = QAction(QIcon('icon/s1.png'), 'Search Parts', self)
        searchpart_action.triggered.connect(self.search)
        file_menu.addAction(searchpart_action)
        
>>>>>>> 7e4232f68a8f716213c57e4ab8f7714beda4bd75
        delpart_action = QAction(QIcon('icon/d1.png'), 'Delete Part', self)
        delpart_action.triggered.connect(self.delete)
        file_menu.addAction(delpart_action)
        
        about_action = QAction(QIcon('icon/i1.png'), 'Developer', self) 
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        
    def setTableWidth(self):
        width = self.table.verticalHeader().width()
        width += self.table.horizontalHeader().length()
        if self.table.verticalScrollBar().isVisible():
            width += self.table.verticalScrollBar().width()
        width += self.table.frameWidth() * 2
        self.table.setFixedWidth(width)
        
    def loaddata(self):
        self.connection = sqlite3.connect('dwglog2.db')
        query = ('''SELECT dwg, part, description, strftime("%m/%d/%Y", date), author 
                    FROM ptnos
                    ORDER BY dwg DESC''')
        result = self.connection.execute(query)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.connection.close()
        
    def handlePaintRequest(self, printer):
        document = QTextDocument()
        cursor = QTextCursor(document)
        model = self.table.model()
        table = cursor.insertTable(model.rowCount, model.columnCount())
        for row in range(table.rows()):
            for column in range(talbe.columns()):
                cursor.insrtText(model.item(row, column).text())
                cursor.movePosition(QTextCursor.NextCell)
        document.print_(printer)
                
    def insert(self):
        dlg = InsertDialog()
        dlg.exec_()
        self.loaddata()
        
    def delete(self):
        dlg = DeleteDialog()
        dlg.exec_()
        
    def search(self):
        dlg = SearchDialog()
        dlg.exec_()
        
    def about(self):
        dlg = AboutDilog()
        dlg.exec_()
        
    def onPressed(self):
        self.label.setText(self.lineedit.text())
          
    def searchpart(self):
        #https://stackoverflow.com/questions/30732480/sqlite-where-clause-for-every-column
        #searchrol = ""
        # https://codeloop.org/pyqt5-creating-qlineedit-with-returnpressed-signal/
        searchrol = self.searchinput.text()
        print('ccc', searchrol)
        try:
            self.conn = sqlite3.connect("dwglog2.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from ptnos WHERE dwg=" + str(searchrol))
            row = result.fetchone()
            print('ddd', row)
            searchresult = ("Dwgno: " + str(row[0]) + '\nPart: ' + str(row[1]) +
                            '\nDescription: ' + str(row[2]) + 
                            '\nDate: ' + str(row[3]) + '\nAuthor: ' + str(row[4]))
            QMessageBox.information(QMessageBox(), 'Successful', searchresult)
            self.conn.commit()
            self.c.close()
            self.conn.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not Find ptnos from the dwglog2 database.')        
        
<<<<<<< HEAD
        
def generate_nos(dwg_nos, partNo):
    '''
    Generate a new drawing number and a new part no.

    Parameters
    ----------
    dwg_nos: list
        A list of tuples derived from the dwg column of the prtnos table of the
        dwglog2.db sqlite database file.  The list has a form like:
        [('2020048',), ('2020049',), ('2020050',)]
            
    partNo: str
        Part no. given by the user.

    Returns
    -------
    dwgNo: str
        A new drawing no. to add to the dwglog2.db file, e.g. '2020051'
    partNo: str
        Same PartNo as input to this function unless autofill kicks in to
        change nos. from, for example, '0300' to '0300-2020-051', or 
        '6521' to '6521-2020-051'.
    '''
    year = date.today().year  # current year, e.g. 2020 (an int)
    int_list = []
    for x in dwg_nos:  # dwg_nos has a form like [('2020048',), ('2020049',), ('2020050',)]
        if len(x[0])>6 and x[0].isnumeric() and year == int(x[0][:4]):
            int_list.append(int(x[0][4:])) # e.g. 48, 49, and 50 from "2020048", "2020049", and "2020050"          
    if int_list:
        max_int = max(int_list)                # e.g. 50
        dwg_prefix = str(max_int + 1)          # e.g. "51"
        if len(dwg_prefix) > 3:
            _len = -1 * len(dwg_prefix)
        else:
            _len = -3
        dwg_prefix = dwg_prefix.zfill(10)[_len:]  # e.g. filled: "51" to "051"
        dwgNo = str(year) + dwg_prefix         # e.g. a new dwg no.: "2020051"
    else:
        dwgNo = str(year) + '001'  # if no ints in list, then is 1st dwg no. for a new year
    if ((partNo.isnumeric() and len(partNo) == 4) or
           (len(partNo) == 5 and partNo[:4].isnumeric() and partNo[-1] == '-')):
        partNo = partNo[:4] + '-' + str(year) + '-' + dwgNo[4:]  # e.g. "0300" to "0300-2020-051"
    return dwgNo, partNo
    
=======
def generate_nos(largestDwgNo, partNo):
    partNo = partNo.strip()  # partNo is a string
    year = date.today().year  # year is a float
    if str(year) > largestDwgNo:  # A new year!
        dwgNo = str(year*1000 + 1)
    #elif partNo.isnumeric() and len(partNo) == 6:  # if is production no. like 091088
    #    dwgNo = partNo
    else:
        dwgNo = str(int(largestDwgNo) + 1)
    if ((partNo.isnumeric() and len(partNo) == 4) or
           (len(partNo) == 5 and partNo[:4].isnumeric() and partNo[-1] == '-')):
        partNo = partNo[:4] + '-' + str(year) + '-' + dwgNo[4:]
    #elif ((len(partNo) == 9 or len(partNo) == 10) and partNo[4] == '-'
    #        and partNo[:4].isnumeric() and partNo[5:9].isnumeric()):
    #    partNo = partNo[:9] + '-' + dwgNo[4:]
            
    return dwgNo, partNo    
>>>>>>> 7e4232f68a8f716213c57e4ab8f7714beda4bd75
    

        
        
        
app = QApplication(sys.argv)
if (QDialog.Accepted == True):
    window = MainWindow()
    window.show()
    window.loaddata()
sys.exit(app.exec_())
        
        
        
        
        
        
        
        
        
        
        
        
