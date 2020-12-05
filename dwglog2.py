
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:49:28 2020

@author: Kenneth E. Carlton

Written for Dekker Vaccuum Technologies, Inc.  Manages and minipulates data
in a sqlite database file.  This database file contains drawing numbers with 
associated part numbers, part discriptions, drawing dates, and drawing authors.
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


class MainWindow(QMainWindow):
    ''' Shows a table of data derived from the dwglog2.db database.  Menu items
    allow for the manipulation of this data.
    '''
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowIcon(QIcon('icon/dwglog2.ico'))
        
        self.conn = sqlite3.connect('dwglog2.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS 
                        dwgnos(dwg INTEGER PRIMARY KEY NOT NULL UNIQUE, part TEXT, 
                        description TEXT, date TEXT NOT NULL, author TEXT)''')
        self.c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_dwgnos_dwg ON dwgnos (dwg)')  
        self.c.close()
        
        file_menu = self.menuBar().addMenu('&File')
        help_menu = self.menuBar().addMenu('&Help')
        self.setWindowTitle('Dekker Drawing Log 2')
        self.setMinimumSize(850, 600)
        
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(5)
        
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 335)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 30)
        
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(('Dwg No.', 'Part No.',
                                            'Description', 'Date', 'Author'))
        
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.tableWidget.cellChanged.connect(self.cell_was_changed)

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
       
        empty_label = QLabel()
        empty_label.setText('         ')
        toolbar.addWidget(empty_label)
        
        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('\U0001F50D Type here to search (e.g. BASEPLATE*; kcarlton)')
        self.searchinput.setToolTip('; = intersection of search result sets. Search is case sensitive. \n' +
                                    'GLOB characters *, ?, [, ], and ^ can be used for searching')
        self.searchinput.returnPressed.connect(self.searchpart)
        toolbar.addWidget(self.searchinput)
            
        addpart_action = QAction(QIcon('icon/add_record.png'), '&Add Record', self)
        addpart_action.triggered.connect(self.insert)
        file_menu.addAction(addpart_action)
        
        addrefresh_action = QAction(QIcon('icon/r3.png'), 'Refresh', self)
        addrefresh_action.setShortcut(QKeySequence.Refresh)
        addrefresh_action.triggered.connect(self.loaddata)
        file_menu.addAction(addrefresh_action)
        
        quit_action = QAction(QIcon('icon/quit.png'), '&Quit', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        help_action = QAction(QIcon('icon/question-mark.png'), '&Help', self) 
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self._help)
        help_menu.addAction(help_action)
        
        about_action = QAction(QIcon('icon/i1.png'), '&About', self) 
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        
    def loaddata(self):
        self.loadingdata = True  # make sure that "cell_was_changed" func doesn't get activated.
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
                
    def insert(self):
        dlg = AddDialog()  # call up the dialog box to add a new record.
        dlg.exec_()
        self.loaddata()   # automatically reload latest database data
                
    def about(self):
        dlg = AboutDialog()
        dlg.exec_()
        
    def _help(self):
        dlg = HelpDialog()
        dlg.exec_()
                  
    def searchpart(self):
        searchterm = self.searchinput.text()
        search(searchterm)
             
    def cell_was_clicked(self, row, column):
        ''' When a user clicks on a table cell, record the text from that cell
        before the user changes the contents.
        '''
        item = self.tableWidget.item(row, column)
        self.clicked_cell_text = item.text().strip()
                            
    def cell_was_changed(self,row,column):
        if self.loadingdata == False:
            k = {}
            for n in range(5):
                itemcol = self.tableWidget.item(row, n)
                k[n] = itemcol.text()
            clicked_text = self.clicked_cell_text  # text previously in the cell
            cell_changed(k, clicked_text, column)  # update database with new data
            self.loaddata()  # automatically reload latest database data
            
            
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        
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
        
        
class AddDialog(QDialog):
    ''' A dialog box allowing a user to add a new record (dwg no., pt. no., etc.)
    to the database.
    '''
    def __init__(self, *args, **kwargs):
        super(AddDialog, self).__init__(*args, **kwargs)
           
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
        _date = now.strftime("%m/%d/%Y")
        
        try:
            self.conn = sqlite3.connect('dwglog2.db')
            self.c = self.conn.cursor()
            self.c.execute("SELECT dwg FROM dwgnos ORDER BY dwg DESC LIMIT 50")
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
        except sqlite3.Error as er:
            errmsg = 'SQLite error: %s' % (' '.join(er.args))
            QMessageBox.warning(QMessageBox(), 'Error', errmsg)
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not add pt no. to the database')
        
        
class HelpDialog(QDialog):
    ''' Show help info '''
    def __init__(self, *args, **kwargs):
        super(HelpDialog, self).__init__(*args, **kwargs)
        
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
                     + '    Note that searches are case sensitive.  For more information about searching, see:\n'
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
        
        
class SearchResults(QDialog): 
    ''' A dialog box to show search results based on a users search query.
    The results are shown in a table.  Note that any changes made to a cell
    in the table are passed on to the dwglog2.db database.  Afterward the
    table is refreshed.
    '''   
    def __init__(self, found, searchterm, parent=None):
        super(SearchResults, self).__init__(parent)
        
        addrefresh_action = QAction(QIcon('icon/r3.png'), 'Refresh', self)
        addrefresh_action.setShortcut(QKeySequence.Refresh)
        addrefresh_action.triggered.connect(self.loaddata)
        
        self.found = found
        self.searchterm = searchterm
        lenfound = len(found)
        self.setWindowTitle('Search Results: ' + searchterm)
        self.setMinimumWidth(850)
        if lenfound >= 16:
            self.setMinimumHeight(600)
        elif 16 > lenfound > 5:    # to rescrict the size of the dialog box somewhat
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
        
    def loaddata(self):  # or rather to reload data.  The __init__ func loads data without this func.
        self.loadingdata = True  # make sure that "cell_was_changed" func doesn't get activated.         
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
        ''' If a user changed a cell, then the database would have been updated.
         This function serves to again search the database using the previously
         used search query so that the table can be refreshed.
        '''
        caller_is_SearchResults = True
        self.found = search(self.searchterm, caller_is_SearchResults)
                
    def cell_was_clicked(self, row, column):
        ''' When a user clicks on a table cell, record the text from that cell
        before the user changes the contents.
        '''
        item = self.tableWidget.item(row, column)
        self.clicked_cell_text = item.text().strip()
                            
    def cell_was_changed(self, row, column):
        if self.loadingdata == False:
            k = {}
            for n in range(5):
                itemcol = self.tableWidget.item(row, n)
                k[n] = itemcol.text()
            clicked_text = self.clicked_cell_text  # text previously in the cell
            cell_changed(k, clicked_text, column)  # update database with new data
            self.searchpart()  # cell was changed.  Search again to get table refreshed.
            self.loaddata()   # cell was changed, so reload data from database
        
        
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
    '''  As explained in this program's help section, takes input of a form
    like: "09*; 11/*/2020 or 09*; 12/*/2020", parses it according to embedded
    semicolons and "or"s, then passes that info on to sqlite as a query,
    and sqlite then yields search results from the dwglog2.db database. 
    
    Parameters
    ----------
    searchterm: str
        A search term to search for. 
        
    caller_is_SearchResults: bool, optional
        When this function is called upon by the "SearchResults" class, it sets
        "caller_is_SearchResults" to True  The default is False.

    Returns
    -------
    rows: list or SearchResults
        If caller_is_SearchResults is set to True, returns a list tuples.  Each
        tuple contains five items: dwg no., pt. no., description, date, and
        author.  These tuples are found items based upon a users query.  If
        caller_is_SearchResults is set to False, opens a gui window created by
        the class "SearchResults" which shows query results.
    '''
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
    ''' This function is called if a table cell has changed, whether in the
    table of the MainWindow or in a table in a SearchResults window.  The 
    appropriatness of the change and how the change is handled depends on in 
    what column the change is made in.  For example, if a user enters a value 
    in a cell meant for a date, and the format of the text for that date is not
    appropriate, the change will not be allowed.
    
    If the change is deemed acceptable, a change verification dialog is shown
    to the user.  If the user clicks OK to verify the change, the sqlite 
    dwglog2.db database is updated.
    
    Parameters
    ----------
    k: dictionary
        The dicionary has keys named 0, 1, 2, 3, and 4.  The values
        corresponding to these keys are text in columns 0 (dwg no.), 
        1 (part no.), 2 (description), 3 (date), and 4 (author); these 
        corresponding to the row that contains the cell that has changed.  
    clicked_text: str
        The original text that was in the cell that has been changed to 
        contain the updated text.
    column: int
        The column in which the change occurred: 0, 1, 2, 3, or 4
        (corresponding to the columns dwg, part, description, date, or author).
        (Note that this "cell_changed" function knows to which table row to
        apply the change to because k[0] of the dictionary contains the drawing
        number, and this number is unique in the table.)

    Returns
    -------
    None.  (The dwglog2.db database is updated.)

    '''
    colnames = {0:'dwg', 1:'part', 2:'description', 3:'date', 4:'author'}
    k[column] = k[column].upper()
    if column == 1:
        k[column] = k[column][:30]
    elif column == 2:
        k[column] = k[column][:40]
    if column == 3 and k[column].count('/') == 2:  # date column
        j = k[column].split('/')
        if (all(i.isdigit() for i in j)
                and (1 <= int(j[0]) <= 12)
                and (1 <= int(j[1]) <= 31)
                and (1998 <= int(j[2]) <= 2099)):
            k[column] = j[0].zfill(3)[-2:] + '/' + j[1].zfill(3)[-2:] + '/' + j[2]
        else:
            k[column] = 'abort3'
    elif column == 3:
        k[column] = 'abort3'
    elif column == 0 and k[column].lower() in ('delete', 'remove', 'trash', 'cut',
                                                  'erase', 'void', 'null', 'clear'):
        k[column] = 'delete'
    elif column == 0 and  k[column].isdigit():  # dwgno col
        conn = sqlite3.connect('dwglog2.db')
        c = conn.cursor()
        c.execute("SELECT dwg FROM dwgnos LIMIT 50")
        result = c.fetchall()
        dwgno, part = generate_nos(result, '')
        if (int(k[column]) < 2009193) or (dwgno + 20 > int(k[column])):
            k[column] = 'abort0'
    elif column == 0:
        k[column] = 'abort0'  
    elif column == 4:
        k[column] = k[column].lower()
                
    try:
        if k[column] == 'abort3':
            raise  Exception('improper date format')
        elif k[column] == 'abort0':
            raise  Exception('improper dwg. no.')
            
        # set up message box for user to verify update
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Warning)
        if k[column] == 'delete':
            msgbox.setWindowTitle('Delete?')
            msg = ('dwg:      ' + clicked_text + '\nptno:     ' + k[1] + '\ndescrip: '
                    + k[2] + '\ndate:     ' + k[3] + '\nauthor:  ' + k[4])
            msgbox.setText(msg)
        else:
            msgbox.setWindowTitle('Update?')
            msg = ('from: ' +  clicked_text + '\nto:     ' + k[column])
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
            if column == 0 and k[column] == 'delete':
                sqlUpdate = 'DELETE from dwgnos WHERE dwg = ' + clicked_text
            elif column == 0:
                sqlUpdate = ('UPDATE dwgnos SET ' + colnames[column] 
                             + " = " + k + " WHERE dwg = " + clicked_text)
            else:
                sqlUpdate = ('UPDATE dwgnos SET ' + colnames[column] 
                             + " = '" + k[column] + "' WHERE dwg = " + k[0])
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
            


           
                    
app = QApplication(sys.argv)
if (QDialog.Accepted == True):
    window = MainWindow()
    window.show()
    window.loaddata()
sys.exit(app.exec_())
        
        
        
        
        
        
        
        
        
        
        
        
