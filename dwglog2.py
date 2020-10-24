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
import time
import os
from datetime import date


class InsertDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(InsertDialog, self).__init__(*args, **kwargs)
           
        self.setWindowTitle('Insert Part Data')
        self.setFixedWidth(350)
        self.setFixedHeight(150)
        
        layout = QVBoxLayout()
        
        self.partinput = QLineEdit()
        self.partinput.setPlaceholderText('Part No.')
        self.partinput.setMaxLength(30)
        layout.addWidget(self.partinput)
                
        self.descriptioninput = QLineEdit()
        self.descriptioninput.setPlaceholderText('Description')
        self.descriptioninput.setMaxLength(40)
        layout.addWidget(self.descriptioninput)
                
        self.authorinput = QLineEdit()
        self.authorinput.setPlaceholderText('Author')
        layout.addWidget(self.authorinput)
        
        self.QBtn = QPushButton('text-align:center')
        self.QBtn.setText("Submit")
        self.QBtn.setMaximumWidth(75)
        self.QBtn.clicked.connect(self.addpart)   
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtn)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def addpart(self):
        part = ""
        description = ""
        author = ""
        
        part = self.partinput.text()
        description = self.descriptioninput.text()
        _date = date.today()
        author = self.authorinput.text()
        try:
            self.conn = sqlite3.connect('dwglog2.db')
            self.c = self.conn.cursor()
            self.c.execute("INSERT INTO ptnos (part,description,Date,author) VALUES (?,?,?,?)",
                           (part,description,_date,author))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            # QMessageBox.information(QMessageBox(), 'Successful', 'Pt no. added successfully to the database.')
            self.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add pt no. to the database')
            
class SearchDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText('Search')
        
        self.setWindowTitle('Seach user')
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
        searchrol = ""
        searchrol = self.searchinput.text()
        try:
            self.conn = sqlite3.connect("dwglog2.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from ptnos WHERE dwg=" + str(searchrol))
            row = result.fetchone()
            searchresult = ("Dwgno : " + str(row[0]) + '\n' + "Part : " + str(row[1]) +
                            '\n' + "Description : " + str(row[2]) + '\n' +
                            "Author : " + str(row[4]))
            QMessageBox.information(QMessageBox(), 'Successful', searchresult)
            self.conn.commit()
            self.c.close()
            self.conn.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not Find ptnos from the dwglog2 database.')
            
     
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
        delrol = ""
        delrol = self.deleteinput.text()
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
        
        layout.addWidget(QLabel('v2.0'))
        layout.addWidget(QLabel('Copyright Okay Dekter 2019'))
        layout.addWidget(labelpic)
        
        layout.addWidget(self.buttonBox)
        
        
        self.setLayout(layout)
        
        
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('icon/g2.png'))
        
        self.conn = sqlite3.connect('dwglog2.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS 
                        ptnos(item INTEGER PRIMARY KEY AUTOINCREMENT
                        ,dwg INTEGER, part TEXT, description TEXT, date TEXT,
                        author TEXT)''')
        self.c.close()
        
        file_menu = self.menuBar().addMenu('&File')
        
        help_menu = self.menuBar().addMenu('&About')
        self.setWindowTitle('Dekker Drawing Log 2')
        self.setMinimumSize(750, 600)
        #self.setMaximumSize(800, 1200)
        
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(5)
        
        #self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        #self.tableWidget.resizeColumnsToContents()
        
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 140)
        self.tableWidget.setColumnWidth(2, 330)
        self.tableWidget.setColumnWidth(3, 80)
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
        
        btn_ac_adduser = QAction(QIcon('icon/add2.jpg'), 'AddPart', self)  # add part icon
        btn_ac_adduser.triggered.connect(self.insert)
        btn_ac_adduser.setStatusTip('Add Part')
        toolbar.addAction(btn_ac_adduser)
        
        btn_ac_refresh = QAction(QIcon('icon/r3.png'), 'Refresh', self)  # refresh icon
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip('Refresh Table')
        toolbar.addAction(btn_ac_refresh)
        
        btn_ac_search = QAction(QIcon('icon/s1.png'), 'Search', self)  #search icon
        btn_ac_search.triggered.connect(self.search)
        btn_ac_search.setStatusTip('Search User')
        toolbar.addAction(btn_ac_search)
        
        btn_ac_delete = QAction(QIcon('icon/d1.png'), 'Delete', self)
        btn_ac_delete.triggered.connect(self.delete)
        btn_ac_delete.setStatusTip('Delete User')
        toolbar.addAction(btn_ac_delete)
        
        adduser_action = QAction(QIcon('icon/add2.jpg'), 'Insert Part', self)
        adduser_action.triggered.connect(self.insert)
        file_menu.addAction(adduser_action)
        
        searchuser_action = QAction(QIcon('icon/s1.png'), 'Search Part', self)
        searchuser_action.triggered.connect(self.search)
        file_menu.addAction(searchuser_action)
        
        deluser_action = QAction(QIcon('icon/i1.png'), 'Delete', self)
        deluser_action.triggered.connect(self.delete)
        file_menu.addAction(deluser_action)
        
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
        query = 'SELECT dwg, part, description, date, author FROM ptnos ORDER BY Item DESC'
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
        
        
app = QApplication(sys.argv)
if (QDialog.Accepted == True):
    window = MainWindow()
    window.show()
    window.loaddata()
sys.exit(app.exec_())
        
        
        
        
        
        
        
        
        
        
        
        