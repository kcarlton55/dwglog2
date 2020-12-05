#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:49:28 2020

@author: ken

https://www.youtube.com/watch?v=kKNINH-Nf8w&t=7s
"""



from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent
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
        self.partinput.setPlaceholderText('Part No. (nos. like 0300- or 0300 will autofill)')
        self.partinput.setMaxLength(30)
        layout.addWidget(self.partinput)
                
        self.descriptioninput = QLineEdit()
        self.descriptioninput.setPlaceholderText('Description')
        self.descriptioninput.setMaxLength(40)
        layout.addWidget(self.descriptioninput)
                        
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

        part = self.partinput.text().upper().strip()
        description = self.descriptioninput.text().upper().strip()
        now = datetime.now()
        #_date = now.strftime("%Y-%m-%d %H:%M:%S")
        _date = now.strftime("%m/%d/%Y")
        
        try:
            self.conn = sqlite3.connect('dwglog2.db')
            self.c = self.conn.cursor()
            self.c.execute("SELECT dwg FROM dwgnos LIMIT 50")
            result = self.c.fetchall()
            dwgno, part = generate_nos(result, part)
            self.c.execute("INSERT INTO dwgnos (dwg, part, description, Date, author) VALUES (?,?,?,?,?)",
                           (dwgno, part, description, _date, author))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            self.close()
        except TypeError:
            year = date.today().year
            dwgno, part  = year*1000, 'Invalid part no.'
            self.c.execute("INSERT INTO dwgnos (dwg, part, description, Date, author) VALUES (?,?,?,?,?)",
                           (dwgno, part, description, _date, author))
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
            

class DeleteDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteDialog, self).__init__(*args, **kwargs)
        
        self.QBtn = QPushButton()
        self.QBtn.setText("Delete")
        
        self.setWindowTitle("Delete a Record")
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
            self.c.execute('DELETE from dwgnos WHERE dwg = ' + str(deldwg))
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
        
        #self.setFixedWidth(500)
        self.setFixedHeight(250)
        
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        
        self.setWindowTitle('About')
        
        labelpic = QLabel()
        pixmap = QPixmap('icon/dekkerlogo.png')
        pixmap = pixmap.scaledToWidth(275)
        labelpic.setPixmap(pixmap)
        labelpic.setFixedHeight(150)
    
        layout.addWidget(labelpic)
        layout.addWidget(QLabel('program name: dwglog2, version: ' + __version__ + '\n'
                                + 'Written by: Ken Carlton, December 1, 2020'))
        
        layout.addWidget(self.buttonBox)
        
        
        self.setLayout(layout)
        
        
class HelpDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(HelpDialog, self).__init__(*args, **kwargs)
        
        #self.setFixedWidth(500)
        #self.setFixedHeight(500)
        
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        
        self.setWindowTitle('Help')
        
        helpinfo = ('Add a new record:\n\n'
                     + '    Press the button that has the plus sign on it.  Enter the part no. and description.\n'
                     + '    Other record fields (dwg no., date, author) will be automatically filled in.  If\n'
                     + '    only the first four digits of a part no. are entered, then the remainder of the\n'
                     + '    part no. will be filled in automatically.  That is 0300 -> 0300-2020-401\n\n'
                     + 'Search examples:\n\n'
                     + '    query:  VMX0036?A1-00*    (note the use of the quesion mark, ?)\n'
                     + '    finds:    2020808, 093954, VMX0036MA1-00 460V TEFC, 11/04/2020, whoyt\n'
                     + '                 2020804, 093859, VMX0036KA1-00 575V TEFC, 11/04/2020, kcarlton\n'
                     + '                 ...\n\n'
                     + '    query:  09*; 0[345]/*/2020; kcarlton\n'
                     + '    finds:    2020811, 093902, VMX0103KA1-00 460V TEFC, 03/25/2020, kcarlton\n'
                     + '                 2020804, 093859, RVL212HH-14 W/OPTIONS 380V/50/3, 05/03/2020, kcarlton\n'
                     + '                 ...\n'
                     + '        That is, finds production units of March, April, and May of 2020 by kcarlton.  The ; \n'
                     + '        character finds the intersection of search results of "09*", "0[345]/*/2020", and "kcarlton"\n\n'
                     + '    query:  09*; kcar*; 11/*/2020 or 09*; rcol*; 11/*/2020 or 09*; who*; 11/*/2020\n'
                     + '    finds:     2020818, 093798, VMXVFD0203KA2-00 460V TEFC, 11/11/2020, kcarlton\n'
                     + '                  2020816, 094189, RVL031H-03 PUMP W/VG 208-230/460V, 11/11/2020, rcollins\n'
                     + '                  2020808, 093954, VMX0036MA1-00 460V TEFC, 11/04/2020, whoyt\n'
                     + '                 ...\n'
                     + '        Yields results for any or all of "09*; kcar*; 11/*/2020" or "rcol*; 11/*/2020 or 09*"\n'
                     + '        or "09*; who*; 11/*/2020".  The word "or" must be in lower case letters.\n\n'
                     + '    Note that searches are case sensitive.  For more inforation about searching, see:\n'
                     + '    https://en.wikipedia.org/wiki/Glob_(programming) \n\n'
                     + 'Update a field:\n\n'
                     + '    To update a field (a table cell), change the text in the cell and then press the Enter key.\n\n'
                     + 'Delete a record:\n\n'
                     + '    To delete a data record (a table row), enter one of the following words into the cell\n'
                     + '    that contains the drawing number: delete, remove, trash.  Then press Enter.\n\n'
                     + 'Refresh the table:\n\n'
                     + '    While you are working on the dwglog2 program, other users simultaneously have access to\n'
                     + '    the same data shown to you.  You may wish to push the refresh button to see changes\n'
                     + '    other users have made while you have been working with the program.  Also, if you wish\n'
                     + '    to see that your data has been updated successfully, push the refresh button.\n\n'
                     )            
        
        layout.addWidget(QLabel(helpinfo))
        
        layout.addWidget(self.buttonBox)
        
        
        self.setLayout(layout)
        
        
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.installEventFilter(self)
        
        self.setWindowIcon(QIcon('icon/dwglog2.ico'))
        
        self.conn = sqlite3.connect('dwglog2.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS 
                        dwgnos(dwg INTEGER PRIMARY KEY NOT NULL UNIQUE, part TEXT, 
                        description TEXT, date TEXT NOT NULL, author TEXT)''')
        # https://stackoverflow.com/questions/42004505/sqlite-select-with-limit-performance
        self.c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_dwgnos_dwg ON dwgnos (dwg)')  
        self.c.close()
        
        file_menu = self.menuBar().addMenu('&File')
        
        help_menu = self.menuBar().addMenu('&Help')
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
        
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.tableWidget.cellChanged.connect(self.cell_was_changed)

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
        
        btn_ac_addpart = QAction(QIcon('icon/add_record.png'), 'Add Record', self)  # add part icon
        btn_ac_addpart.triggered.connect(self.insert)
        btn_ac_addpart.setStatusTip('Add a Record')
        toolbar.addAction(btn_ac_addpart)
        
        btn_ac_refresh = QAction(QIcon('icon/r3.png'), 'Refresh', self)  # refresh icon
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip('Refresh Table')
        toolbar.addAction(btn_ac_refresh)
       
# =============================================================================
#         btn_ac_delete = QAction(QIcon('icon/trash.png'), 'Delete', self) 
#         #btn_ac_delete.triggered.connect(self.delete)
#         btn_ac_delete.triggered.connect(self.deletedialog)
#         btn_ac_delete.setStatusTip('Delete a record')
#         toolbar.addAction(btn_ac_delete)
# =============================================================================
        
        empty_label = QLabel()
        empty_label.setText('         ')
        toolbar.addWidget(empty_label)

#-----------
        
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('\U0001F50D Type here to search (e.g. BASEPLATE*; kcarlton)')
        self.searchinput.setToolTip('; = intersection of search result sets. Search is case sensitive. \n' +
                                    'GLOB characters *, ?, [, ], and ^ can be used for searching')
        self.searchinput.returnPressed.connect(self.searchpart)

        toolbar.addWidget(self.searchinput)
        
        

    
#-----------        
        
        addpart_action = QAction(QIcon('icon/add_record.png'), '&Add Record', self)
        addpart_action.triggered.connect(self.insert)
        file_menu.addAction(addpart_action)
        
        addrefresh_action = QAction(QIcon('icon/r3.png'), 'Refresh', self)
        addrefresh_action.setShortcut(QKeySequence.Refresh)
        addrefresh_action.triggered.connect(self.loaddata)
        file_menu.addAction(addrefresh_action)

        
# =============================================================================
#         searchpart_action = QAction(QIcon('icon/s1.png'), 'Search Records', self)
#         searchpart_action.triggered.connect(self.search)
#         file_menu.addAction(searchpart_action)
# =============================================================================
        
# =============================================================================
#         delpart_action = QAction(QIcon('icon/trash.png'), 'Delete a Record', self)
#         delpart_action.triggered.connect(self.delete)
#         file_menu.addAction(delpart_action)
# =============================================================================
        
        quit_action = QAction(QIcon('icon/quit.png'), '&Quit', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self._close)
        file_menu.addAction(quit_action)
        
        help_action = QAction(QIcon('icon/question-mark.png'), '&Help', self) 
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self._help)
        help_menu.addAction(help_action)
        
        about_action = QAction(QIcon('icon/i1.png'), '&About', self) 
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        
# =============================================================================
#     def setTableWidth(self):
#         width = self.table.verticalHeader().width()
#         width += self.table.horizontalHeader().length()
#         if self.table.verticalScrollBar().isVisible():
#             width += self.table.verticalScrollBar().width()
#         width += self.table.frameWidth() * 2
#         self.table.setFixedWidth(width)
# =============================================================================
        
    def loaddata(self):
        self.loadingdata = True
        conn = sqlite3.connect('dwglog2.db')
        c = conn.cursor()
        query = ('''SELECT dwg, part, description, date, author 
                    FROM dwgnos
                    ORDER BY dwg DESC LIMIT 100''')
        result = c.execute(query)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number, column_number, item)
        c.close()        
        conn.close()
        self.loadingdata = False
        
# =============================================================================
#     def handlePaintRequest(self, printer):
#         document = QTextDocument()
#         cursor = QTextCursor(document)
#         model = self.table.model()
#         table = cursor.insertTable(model.rowCount, model.columnCount())
#         for row in range(table.rows()):
#             for column in range(talbe.columns()):
#                 cursor.insrtText(model.item(row, column).text())
#                 cursor.movePosition(QTextCursor.NextCell)
#         document.print_(printer)
# =============================================================================
                
    def insert(self):
        dlg = InsertDialog()
        dlg.exec_()
        self.loaddata()
        
    def delete(self):
        dlg = DeleteDialog()
        dlg.exec_()
        dlg.show()
        self.loaddata()
        
    def deletedialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText('Delete a Record')
        msg.setText('To delete a record (a table row), replace the dwg no.\n'
                    + 'with one of these words: delete, remove, or trash.  Then\n'
                    + 'press the Enter key.')
        msg.setWindowTitle('Remove a record')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        #msg.buttonClicked.connect(self.msgbtn)
        
    def msgbtn():
        print('Button clicked')
        
    def search(self):
        dlg = SearchDialog()
        dlg.exec_()
        
    def about(self):
        dlg = AboutDialog()
        dlg.exec_()
        
    def _help(self):
        dlg = HelpDialog()
        dlg.exec_()
        
    def _close(self):
        self.close()
        
    def onPressed(self):
        self.label.setText(self.lineedit.text())
                  
    def searchpart(self):
        searchterm = self.searchinput.text()
        search(searchterm)
             
    def cell_was_clicked(self, row, column):
        item = self.tableWidget.item(row, column)
        self.clicked_cell_text = item.text().strip()
                            
    def cell_was_changed(self,row,column):
        if self.loadingdata == False:
            k = {}
            item = self.tableWidget.item(row, column)
            k['changed'] = item.text().strip().upper()
            for n in range(5):
                itemcol = self.tableWidget.item(row, n)
                k[n] = itemcol.text()
            clicked_text = self.clicked_cell_text
            cell_changed(k, clicked_text, column)
            self.loaddata()
            
                
class SearchResults(QDialog):        
    def __init__(self, found, searchterm, parent=None):
        super(SearchResults, self).__init__(parent)
        
        addrefresh_action = QAction(QIcon('icon/r3.png'), 'Refresh', self)
        addrefresh_action.setShortcut(QKeySequence.Refresh)
        addrefresh_action.triggered.connect(self.loaddata)
        
        self.found = found
        self.searchterm = searchterm
        lenfound = len(found)
        self.setWindowTitle('Search Results: ' + searchterm)
        #self.setMinimumSize(850, lenfound*75)      # 600)
        self.setMinimumWidth(850)
        if lenfound >= 16:
            self.setMinimumHeight(600)
        elif 16 > lenfound > 5:
            self.setMinimumHeight(lenfound*37 + 40)
        self.r_max = len(self.found)
        self.c_max = len(self.found[0])
        self.values = {}
        for r in range(self.r_max):
             for c in range(self.c_max):
                self.values[(r, c)] = found[r][c]
        self.tableWidget = QTableWidget()   
        self.tableWidget.setColumnCount(5)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 335)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 30)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.tableWidget.cellChanged.connect(self.cell_was_changed)
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.loaddata()
        
    def loaddata(self):
        self.loadingdata = True            
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(self.c_max)
        self.tableWidget.setRowCount(self.r_max)
        self.tableWidget.setHorizontalHeaderLabels(['Dwg No.', 'Part No.',
                                            'Description', 'Date', 'Author'])
        for r in range(self.r_max):
            for c in range(self.c_max):
                item = QTableWidgetItem(str(self.found[r][c]))
                item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                self.tableWidget.setItem(r, c, item)
        self.loadingdata = False
        
    def searchpart(self):
        caller_is_SearchResults = True
        self.found = search(self.searchterm, caller_is_SearchResults)
                
    def cell_was_clicked(self, row, column):
        item = self.tableWidget.item(row, column)
        self.clicked_cell_text = item.text().strip()
                            
    def cell_was_changed(self,row,column):
        if self.loadingdata == False:
            k = {}
            item = self.tableWidget.item(row, column)
            k['changed'] = item.text().strip().upper()
            for n in range(5):
                itemcol = self.tableWidget.item(row, n)
                k[n] = itemcol.text()
            clicked_text = self.clicked_cell_text
            cell_changed(k, clicked_text, column)
            self.searchpart()
            self.loaddata()
            

def generate_nos(dwg_nos, partNo):
    '''
    Generate a new drawing number and a new part no.

    Parameters
    ----------
    dwg_nos: list
        A list of tuples derived from the dwg column of the prtnos table of the
        dwglog2.db sqlite database file.  The list has a form like:
        [(2020048,), (2020049,), (2020050,)]
            
    partNo: str
        Part no. given by the user.

    Returns
    -------
    dwgNo: int
        A new drawing no. to add to the dwglog2.db file, e.g. 2020051
    partNo: str
        Same PartNo as input to this function unless autofill kicks in to
        change nos. from, for example, '0300' to '0300-2020-051', or 
        '6521' to '6521-2020-051'.
    '''
    year = date.today().year  # current year, e.g. 2020 (an int)
    int_list = []
    for x in dwg_nos:  # dwg_nos has a form like [(2020048,), (2020049,), (2020050,)]
        if isinstance(x[0], int) and str(x[0])[:4] == str(year):
            int_list.append(x[0])  
    if int_list:
        dwgNo = max(int_list) + 1
    else:
        dwgNo = year*1000 + 1  # if no ints in list, then is 1st dwg no. for a new year
    if ((partNo.isnumeric() and len(partNo) == 4) or
           (len(partNo) == 5 and partNo[:4].isnumeric() and partNo[-1] == '-')):
        partNo = partNo[:4] + '-' + str(year) + '-' + str(dwgNo)[4:]
    return dwgNo, partNo


def search(searchterm, caller_is_SearchResults=False):
    searchlistparent = searchterm.split(' or ')
    searchlistparent = [x.strip('; ') for x in searchlistparent]  # get rid of any junk on ends of str
    sqlSelect = 'SELECT dwg, part, description, date, author FROM dwgnos WHERE ('
    for searchtermchild in searchlistparent:
        searchlistchild = searchtermchild.split(';')
        searchlistchild = [x.strip() for x in searchlistchild]
        for i in searchlistchild:
            sqlSelect +=  '''(part GLOB '{0}' OR description GLOB '{0}'
                              OR author GLOB '{0}' OR dwg GLOB '{0}'
                              OR date GLOB '{0}') AND '''.format(i)
        sqlSelect = sqlSelect[:-5] + ') OR ('   
    sqlSelect = sqlSelect[:-6] + ') ORDER BY dwg DESC'        
    try:
        conn = sqlite3.connect("dwglog2.db")
        c = conn.cursor()
        result = c.execute(sqlSelect)            
        rows = result.fetchall()
        c.close()        
        conn.close()
        if caller_is_SearchResults:
            return rows            
        srch = SearchResults(rows, searchterm)
        srch.show()  # https://stackoverflow.com/questions/11920401/pyqt-accesing-main-windows-data-from-a-dialog
        srch.exec_()
    except Exception:
        QMessageBox.warning(QMessageBox(), 'Error', 'Could not find text searched for.')


def cell_changed(k, clicked_text, column):
    colnames = {0:'dwg', 1:'part', 2:'description', 3:'date', 4:'author'}
    if column == 1:
        k['changed'] = k['changed'][:30]
    elif column == 2:
        k['changed'] = k['changed'][:40]
    if column == 3 and k['changed'].count('/') == 2:  # date column
        j = k['changed'].split('/')
        if (all(i.isdigit() for i in j)
                and (1 <= int(j[0]) <= 12)
                and (1 <= int(j[1]) <= 31)
                and (1998 <= int(j[2]) <= 2099)):
            k['changed'] = j[0].zfill(3)[-2:] + '/' + j[1].zfill(3)[-2:] + '/' + j[2]
        else:
            k['changed'] = 'abort3'
    elif column == 3:
        k['changed'] = 'abort3'
    elif column == 0 and k['changed'].lower() in ('delete', 'remove', 'trash', 'cut',
                                                  'erase', 'void', 'null', 'clear'):
        k['changed'] = 'delete'
    elif column == 0 and  k['changed'].isdigit():  # dwgno col
        conn = sqlite3.connect('dwglog2.db')
        c = conn.cursor()
        c.execute("SELECT dwg FROM dwgnos LIMIT 50")
        result = c.fetchall()
        dwgno, part = generate_nos(result, '')
        if (int(k['changed']) < 2009193) or (dwgno + 20 > int(k['changed'])):
            k['changed'] = 'abort0'
    elif column == 0:
        k['changed'] = 'abort0'  
    elif column == 4:
        k['changed'] = k['changed'].lower()
        
    try:
        if k['changed'] == 'abort3':
            raise  Exception('improper date format')
        elif k['changed'] == 'abort0':
            raise  Exception('improper dwg. no.')
            
        # set up message box for user to verify update
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Warning)
        if k['changed'] == 'delete':
            msgbox.setWindowTitle('Delete?')
            msg = ('dwg:      ' + clicked_text + '\nptno:     ' + k[1] + '\ndescrip: '
                    + k[2] + '\ndate:     ' + k[3] + '\nauthor:  ' + k[4])
            msgbox.setText(msg)
        else:
            msgbox.setWindowTitle('Update?')
            msg = ('from: ' +  clicked_text + '\nto:     ' + k['changed'])
            msgbox.setText(msg)
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msgbox.exec_()
        if retval == QMessageBox.Cancel:
            userresponse = False
        elif retval == QMessageBox.Ok:
            userresponse = True
              
        if userresponse == True:    
            conn = sqlite3.connect("dwglog2.db")
            c = conn.cursor()
            if column == 0 and k['changed'] == 'delete':
                sqlUpdate = 'DELETE from dwgnos WHERE dwg = ' + clicked_text
            elif column == 0:
                sqlUpdate = ('UPDATE dwgnos SET ' + colnames[column] 
                             + " = " + k + " WHERE dwg = " + clicked_text)
            else:
                sqlUpdate = ('UPDATE dwgnos SET ' + colnames[column] 
                             + " = '" + k['changed'] + "' WHERE dwg = " + k[0])
            result = c.execute(sqlUpdate)
            conn.commit()
            c.close()        
            conn.close() 
        
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        QMessageBox.warning(QMessageBox(), 'Error', errmsg)
    except Exception as er:
        if er.args:
            QMessageBox.warning(QMessageBox(), 'Error', er.args[0])
        else:
            QMessageBox.warning(QMessageBox(), 'Error', 'field not updated')            
            
            
            
def verifyQMessageBox(msg):
    verify = QMessageBox()
    verify.setIcon(QMessageBox.Warning)
    verify.setText(msg)
    verify.setWindowTitle('Verify')
    verify.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    verify.buttonClicked.connect(verifyUserResponse)
    verify._exec()
    
def userResponse(i):
    print("Button pressed is:",i.text())
    
        
app = QApplication(sys.argv)
if (QDialog.Accepted == True):
    window = MainWindow()
    window.show()
    window.loaddata()
sys.exit(app.exec_())
        
        
        
        
        
        
        
        
        
        
        
        
