#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:49:28 2020

@author: Kenneth E. Carlton

Written for Dekker Vaccuum Technologies, Inc.. Generates drawing numbers and
stores those numbers, along with part numbers and part descriptions, in a
sqlite database file.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTableWidget, QMainWindow, QDialog, QApplication,
                             QToolBar, QStatusBar, QAction, QLabel, QLineEdit,
                             QTableWidgetItem, QVBoxLayout, QPushButton, QComboBox,
                             QHBoxLayout, QMessageBox, QDialogButtonBox, QRadioButton)
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QColor
import sys
import sqlite3
import os
from datetime import datetime, date
import webbrowser

__version__ = '0.3'
__author__ = 'Kenneth E. Carlton'

if os.getenv('USERNAME'):
    author = os.getenv('USERNAME')  # Works only on MS Windows
    author = author.replace('_', '').lower()
elif sys.platform[:3] == 'lin':  # I'm working on my Linux system
    author = 'kcarlton'
else:
    author = 'unknown'


class MainWindow(QMainWindow):
    ''' Shows a table of data derived from the dwglog2.db database.  Menu items
    allow for the manipulation of this data.
    '''
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        global sqldatafile
        sqldatafile = get_sqldatafile()        
        self.conn = sqlite3.connect(sqldatafile)

        with self.conn:
            self.c = self.conn.cursor()
            self.c.execute('''CREATE TABLE IF NOT EXISTS
                            dwgnos(dwg_index INTEGER PRIMARY KEY NOT NULL UNIQUE,
                            dwg KEY NOT NULL UNIQUE, part TEXT,
                            description TEXT, date TEXT NOT NULL, author TEXT)''')
                            
        self.setWindowIcon(QIcon('icon/dwglog2.ico'))                    

        file_menu = self.menuBar().addMenu('&File')
        help_menu = self.menuBar().addMenu('&Help')
        self.setWindowTitle('Dekker Drawing Log 2')
        self.setMinimumSize(765, 600)

        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(5)

        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 170)
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

        btn_ac_refresh = QAction(QIcon('icon/refresh.png'), 'Refresh', self)  # refresh icon
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip('Refresh Table')
        toolbar.addAction(btn_ac_refresh)

        empty_label1 = QLabel()
        empty_label1.setText('   ')
        toolbar.addWidget(empty_label1)

        self.radio_button_on = False
        self.radio_button = QRadioButton('AutoCopy')
        self.radio_button.setChecked(False)
        self.radio_button.setStatusTip('Automatically copy contents of a clicked cell to the clipboard')
        self.radio_button.clicked.connect(self.check)
        toolbar.addWidget(self.radio_button)

        empty_label2 = QLabel()
        empty_label2.setText('   ')
        toolbar.addWidget(empty_label2)

        self.searchinput = QLineEdit()
        self.searchinput.setPlaceholderText('\U0001F50D Type here to search (e.g. BASEPLATE*; kcarlton)')
        self.searchinput.setToolTip('; = intersection of search result sets. Search is case sensitive. \n' +
                                    'GLOB characters *, ?, [, and ] can be used for searching')
        self.searchinput.returnPressed.connect(self.searchpart)
        toolbar.addWidget(self.searchinput)

        addpart_action = QAction(QIcon('icon/add_record.png'), '&Add Record', self)
        #self.addshortcut = QShortcut(QKeySequence('Ctrl+A'), self)  # ===========
        #self.addshortcut.activated.connect(self.insert)             # ===========
        addpart_action.setShortcut(QKeySequence.SelectAll)
        addpart_action.triggered.connect(self.insert)
        file_menu.addAction(addpart_action)

        addrefresh_action = QAction(QIcon('icon/refresh.png'), '&Refresh', self)
        addrefresh_action.setShortcut(QKeySequence.Refresh)
        addrefresh_action.triggered.connect(self.loaddata)
        file_menu.addAction(addrefresh_action)
        
        settings_action = QAction(QIcon('icon/settings.png'), 'Settings', self)
        settings_action.triggered.connect(self.settings)
        file_menu.addAction(settings_action)

        quit_action = QAction(QIcon('icon/quit.png'), '&Quit', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_action = QAction(QIcon('icon/question-mark.png'), '&Help', self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self._help)
        help_menu.addAction(help_action)

        about_action = QAction(QIcon('icon/about.png'), '&About', self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        
    def settings(self):
        dlg = SettingsDialog()
        dlg.exec_()

    def loaddata(self):
        self.loadingdata = True  # make sure that "cell_was_changed" func doesn't get activated.
        
        try:
            conn = sqlite3.connect(sqldatafile)  # sqldatafile is a global variable
            with conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS
                                dwgnos(dwg_index INTEGER PRIMARY KEY NOT NULL UNIQUE,
                                dwg KEY NOT NULL UNIQUE, part TEXT,
                                description TEXT, date TEXT NOT NULL, author TEXT)''')
                query = ('''SELECT dwg, part, description, date, author
                            FROM dwgnos
                            ORDER BY dwg_index DESC LIMIT 100''')
                result = c.execute(query)
                self.tableWidget.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        item = QTableWidgetItem(str(data))
                        if '?' in str(data):
                            item.setBackground(QColor(255, 255, 0))
                        self.tableWidget.setItem(row_number, column_number, item)

        except sqlite3.Error as e:
            msg = ('sqlite error at MainWindow/loaddata: ' + str(e))
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False) 
            
        except Exception as e:
            msg = ('Error at MainWindow/loaddata: ' + str(e))
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False) 
    
        self.loadingdata = False

    def insert(self):
        dlg = AddDialog()  # call up the dialog box to add a new record.
        dlg.exec_()
        self.loaddata()   # automatically reload latest database data

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def _help(self):
        webbrowser.open('dwglog2_help.html')

    def searchpart(self):
        searchterm = self.searchinput.text()
        search(searchterm, self.radio_button_on)

    def check(self):
        if self.radio_button.isChecked():
            self.radio_button_on = True
        else:
             self.radio_button_on = False

    def cell_was_clicked(self, row, column):
        ''' When a user clicks on a table cell, record the text from that cell
        before the user changes the contents.
        '''
        item = self.tableWidget.item(row, column)
        self.clicked_cell_text = item.text().strip()

        if self.radio_button_on == True:
            #cb = QtGui.QApplication.clipboard()
            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard )
            cb.setText(self.clicked_cell_text, mode=cb.Clipboard)

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
    ''' Show company name, logo, program author, program creation date
    '''
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.setFixedHeight(300)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        self.setWindowTitle('About')

        labelpic = QLabel()
        pixmap = QPixmap('icon/DekkerLogo.png')
        #pixmap = pixmap.scaledToWidth(275)  # was 275
        labelpic.setPixmap(pixmap)
        labelpic.setFixedHeight(150)        # was 150

        layout.addWidget(labelpic)
        layout.addWidget(QLabel('dwglog2, version ' + __version__ + '\n\n' +
                                'The drawing no. generator for\n' +
                                'Dekker Vacuum Technologies, Inc.\n\n' +
                                'Written by Ken Carlton, December 1, 2020'))
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class AddDialog(QDialog):
    ''' A dialog box allowing a user to add a new record (dwg no., pt. no., etc.)
    to the database.
    '''
    def __init__(self, *args, **kwargs):
        super(AddDialog, self).__init__(*args, **kwargs)
        #self.pndescriptions()
        self.flag = False
        self.descrip = ''
        self.part = ''

        self.setWindowTitle('Insert Part Data')
        self.setFixedWidth(350)
        self.setFixedHeight(150)

        layout = QVBoxLayout()

        self.partinput = QComboBox()
        self.partinput.setEditable(True)
        self.partinput.addItems(["0300-", "2202-", "2223-", "2724-", "2273-",
                                 "2277-", "2728-", "2730-", "6050-", "6415-",
                                 "6820-", "6830-", "6875-", "6890-"])
        self.partinput.setCurrentIndex(-1)
        self.partinput.setCurrentText("Part No.")
        self.partinput.view().setMinimumHeight(220)
        self.partinput.currentTextChanged.connect(self.pntextchanged)
        layout.addWidget(self.partinput)

        self.descriptioninput = QLineEdit()
        self.descriptioninput.setPlaceholderText('Description')
        self.descriptioninput.setMaxLength(40)
        layout.addWidget(self.descriptioninput)
        
        self.author = QLineEdit()
        self.author.setPlaceholderText('Author (default: ' + author + ')')
        
        layout.addWidget(self.author)

        self.QBtn = QPushButton('text-align:center')
        self.QBtn.setText("OK")
        self.QBtn.setMaximumWidth(75)
        self.QBtn.clicked.connect(self.addpart)

        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtn)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def addpart(self):
        global author        
        description = self.descriptioninput.text().upper().strip()
        now = datetime.now()
        _date = now.strftime("%m/%d/%Y")
        
        if self.author.text():
            author = self.author.text().lower()
                    
        try:
            self.conn = sqlite3.connect(sqldatafile) # sqldatafile is a global variable
            #self.conn = sqlite3.connect('dwglog2.db')
            with self.conn:
                self.c = self.conn.cursor()
                self.c.execute("SELECT dwg_index FROM dwgnos ORDER BY dwg_index DESC LIMIT 1")
                result = self.c.fetchall()
                dwgno, self.part, new_dwg_index = generate_nos(result, self.part)
                self.c.execute("INSERT INTO dwgnos (dwg_index, dwg, part, description, Date, author) VALUES (?,?,?,?,?,?)",
                               (new_dwg_index, dwgno, self.part, description, _date, author))
            self.close()
        except TypeError:
            # if a dwg_index no. not derived from the database, try the below
            year = date.today().year
            dwgno, self.part, new_dwg_index  = generate_nos([(year*100000,)], self.part)
            #self.conn = sqlite3.connect('dwglog2.db')
            self.conn = sqlite3.connect(sqldatafile)  # sqldatafile is a global variable
            with self.conn:
                self.c = self.conn.cursor()
                self.c.execute("INSERT INTO dwgnos (dwg_index, dwg, part, description, Date, author) VALUES (?,?,?,?,?,?)",
                               (new_dwg_index, dwgno, self.part, description, _date, author))
            self.close()
            QMessageBox.warning(QMessageBox(), 'Error', 'There appears to be a problem with\n'
                                                        'the database.  Will try to cope.')
        except sqlite3.Error as er:
            errmsg = 'SQLite error: %s' % (' '.join(er.args))
            QMessageBox.warning(QMessageBox(), 'Error', errmsg)
        except Exception as er:
            errmsg = 'Error: %s' % (' '.join(er.args))
            QMessageBox.warning(QMessageBox(), 'Error', errmsg)

    def pntextchanged(self, part):
        ''' Generate a part's description based on the part no. that the user
        provides.  This description will show in the description field.  The
        user then will be alter this description as he pleases.  At least the
        first four characters of the part no., all digits, need to be provided.
        If the fifth character is not a dash, -, the description field will
        be cleared.

        Parameters
        ----------
        part : str
            e.g. 0300-, 0300-2020-400, etc.

        Returns
        -------
        None.

        '''
        self.part = part
        desc = self.descriptioninput.text().strip()
        if len(part) <= 3 and desc == self.descrip:  # if user put in his decrip, leave it
            self.descriptioninput.setText("")
        elif (len(part) == 4 and part.isdigit() and (int(part) in pndescrip)
                and (not desc  or desc == self.descrip.strip())):
            self.descrip = pndescrip[int(part[:4])]
            self.descriptioninput.setText(self.descrip.strip())
        elif (len(part) == 5 and part[:4].isdigit() and (int(part[:4]) in pndescrip)
                and (not desc  or desc == self.descrip.strip())):
            self.descrip = pndescrip[int(part[:4])]
            self.descriptioninput.setText(self.descrip.strip())
        if (len(part) == 5 and part[-1:] != '-' and desc == self.descrip.strip()):
            self.descriptioninput.setText("")
            

class SearchResults(QDialog):
    ''' A dialog box to show search results based on a users search query.
    The results are shown in a table.  Note that any changes made to a cell
    in the table are passed on to the dwglog2.db database.  Afterward the
    table is refreshed.
    '''
    def __init__(self, found, searchterm, radio_button_on, parent=None):
        super(SearchResults, self).__init__(parent)
        self.found = found
        self.searchterm = searchterm
        self.radio_button_on = radio_button_on
        lenfound = len(found)
        self.setWindowTitle('Search Results: ' + searchterm)
        self.setMinimumWidth(785)
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
        self.tableWidget.setColumnWidth(1, 170)
        self.tableWidget.setColumnWidth(2, 335)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 30)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.tableWidget.cellChanged.connect(self.cell_was_changed)

        btn_refresh = QPushButton()
        btn_refresh.setIcon(QIcon("icon/refresh.png"))
        btn_refresh.setFixedSize(16, 16)
        btn_refresh.setFlat(True)
        btn_refresh.setToolTip('Refresh')
        btn_refresh.clicked.connect(self.refresh)

        self.radio_button = QRadioButton('AutoCopy')
        if self.radio_button_on==True:
            self.radio_button.setChecked(True)
        else:
            self.radio_button.setChecked(False)
        self.radio_button.clicked.connect(self.check)

        hbox = QHBoxLayout()
        hbox.setSpacing(18)
        #hbox.addStretch(2)
        hbox.addWidget(btn_refresh)
        hbox.addWidget(self.radio_button)

        layout = QVBoxLayout()
        #layout.addStretch(1)
        layout.addLayout(hbox)

        #layout = QVBoxLayout()
        #layout.addWidget(btn_refresh)
        #layout.addWidget(self.radio_button)
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.loaddata()

    def check(self):
        if self.radio_button.isChecked():
            self.radio_button_on = True
        else:
            self.radio_button_on = False
        print(self.radio_button_on)

    def loaddata(self):
        ''' The __init__ func loads data without using this function.  Rather
        this function reloads data.
        '''
        try:
            self.loadingdata = True  # make sure that "cell_was_changed" func doesn't get activated.
            self.tableWidget.clear()
            self.tableWidget.setColumnCount(self.c_max)
            self.tableWidget.setRowCount(self.r_max)
            self.tableWidget.setHorizontalHeaderLabels(['Dwg No.', 'Part No.',
                                                'Description', 'Date', 'Author'])
            for r in range(self.r_max):
                for c in range(self.c_max):
                    item = QTableWidgetItem(str(self.found[r][c]))
                    if '?' in str(str(self.found[r][c])):
                        item.setBackground(QColor(255, 255, 0))
                    item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                    self.tableWidget.setItem(r, c, item)
            self.loadingdata = False
        except:
            self.tableWidget.clear()
            self.loadingdata = False

    def searchpart(self):
        ''' If a user changed a cell, then the database would have been updated.
         This function serves to again search the database using the previously
         used search query so that the table can be refreshed.
        '''
        caller_is_SearchResults = True
        self.found = search(self.searchterm, self.radio_button_on, caller_is_SearchResults)
        if len(self.found):
            self.r_max = len(self.found)
            self.c_max = len(self.found[0])

    def cell_was_clicked(self, row, column):
        ''' When a user clicks on a table cell, record the text from that cell
        before the user changes the contents.
        '''
        try:
            item = self.tableWidget.item(row, column)
            self.clicked_cell_text = item.text().strip()
            if self.radio_button_on == True:
                cb = QApplication.clipboard()
                cb.clear(mode=cb.Clipboard )
                cb.setText(self.clicked_cell_text, mode=cb.Clipboard)
        except:
            pass

    def cell_was_changed(self, row, column):
        try:
            if self.loadingdata == False:
                k = {}
                for n in range(5):
                    itemcol = self.tableWidget.item(row, n)
                    k[n] = itemcol.text()
                clicked_text = self.clicked_cell_text  # text previously in the cell
                cell_changed(k, clicked_text, column)  # update database with new data
                self.searchpart()  # cell was changed.  Search again to get table refreshed.
                self.loaddata()   # cell was changed, so reload data from database
        except:
            self.tableWidget.clear()

    def refresh(self):
        self.searchpart()
        self.loaddata()
        
        
class SettingsDialog(QDialog):
    ''' A dialog box asking the user about settings he would like to make.
    '''
        
    def __init__(self):
        super(SettingsDialog, self).__init__()

        self.setWindowTitle('Settings')
        self.setFixedWidth(450)
        #self.setFixedHeight(100)  # was 150

        layout = QVBoxLayout()
                
        self.settingsfn = ''
        self.settingsdic = {}
        try:
            self.settingsfn = get_settingsfn()
            with open(self.settingsfn, 'r') as file: # Use file to refer to the file object
                x = file.read()
                x = x.replace('\\', '\\\\')
            self.settingsdic = eval(x) 
        except Exception as e:  # it an error occured, moset likely and AttributeError
            print("error8 at SettingsDialog", e)
            
        sqldatafile_label = QLabel()
        sqldatafile_label.setText('Location of the dwglog2.db database file (C:\\path\\dwglog2.db)\n'
                                   + '(after changing and picking OK, do a Refresh):')
        layout.addWidget(sqldatafile_label)
        
        self.sqldatafile_input = QLineEdit()
        self.sqldatafile_input.setPlaceholderText('Leave blank to set back to default file on local computer')
        if 'sqldatafile' in self.settingsdic:
            self.currentsqldatafile = self.settingsdic.get('sqldatafile', '')
            self.sqldatafile_input.setText(self.currentsqldatafile)
        layout.addWidget(self.sqldatafile_input)
        
        self.QBtnOK = QPushButton('text-align:center')
        self.QBtnOK.setText("OK")
        self.QBtnOK.setMaximumWidth(75)
        self.QBtnOK.clicked.connect(self._done)
        
        self.QBtnCancel = QPushButton('text-align:center')
        self.QBtnCancel.setText("Cancel")
        self.QBtnCancel.setMaximumWidth(75)
        self.QBtnCancel.clicked.connect(self.cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.QBtnOK)
        hbox.addWidget(self.QBtnCancel)
        layout.addLayout(hbox)
        self.setLayout(layout)

    def _done(self):
        global sqldatafile
        self.sqldatafile = self.sqldatafile_input.text().strip()
        if not self.sqldatafile:  # if user leaves blank, set back to default file location
            defaultdir = os.path.dirname(get_settingsfn())
            self.sqldatafile = os.path.join(defaultdir, 'dwglog2.db')
        directory, filename = os.path.split(self.sqldatafile)
        filename = filename.lower()
        self.sqldatafile = os.path.join(directory, filename)
        flag = os.path.exists(self.sqldatafile)
        try:
            if (not os.path.isdir(directory)) or (filename != 'dwglog2.db'):
                raise FileNotFoundError
            with open(self.settingsfn, "r+") as file:
                x = file.read()
                x = x.replace('\\', '\\\\')
                self.settingsdic = eval(x) 
                self.settingsdic['sqldatafile'] = self.sqldatafile
                file.seek(0)
                strsettingsdic = str(self.settingsdic)
                strsettingsdic = strsettingsdic.replace('\\\\', '\\')
                file.write(strsettingsdic)
                file.truncate()
                sqldatafile = self.sqldatafile # set the global variable
            if (self.currentsqldatafile.lower() != self.sqldatafile.lower()
                    and not flag):
                msg =  "File not found.  New file created: \n" + self.sqldatafile
                print(msg)
                message(msg, 'New file created', msgtype='Information', showButtons=False)    
        except FileNotFoundError as e:
            msg =  "file not found: " + self.sqldatafile  + '\n' + str(e)
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False)          
        except Exception as e:  # it an error occured, most likely and AttributeError
            msg =  "error9 at SettingsDialog.  " + str(e)
            print(msg)
            message(msg, 'Error', msgtype='Warning', showButtons=False)
        self.close()
        
    def cancel(self):
        self.close()


def generate_nos(dwg_indexes, partNo):
    '''
    Generate a new drawing number and a new part no.

    Parameters
    ----------
    dwg_indexes: list
        A list of tuples derived from the dwg_index column (not the dwg column)
        of the prtnos table of the dwglog2.db sqlite database file.  The list
        has a form like: [(202100855,), (202100856,), (202100857,)]

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
    new_dwg_index: int
        ROWID, used by Sqlite, to order data and to generate new part nos.
        e.g. 202100855.
    '''
    year = date.today().year  # current year, e.g. 2021 (an int)
    int_list = []
    for x in dwg_indexes:  # dwg_indexes has a form like [(202100855,), (202100856,), (202100857,)]
        if isinstance(x[0], int) and str(x[0])[:4] == str(year):
            int_list.append(x[0])  # a list of recent dwg. nos.
    if int_list:  # list of dwg nos. in the current year
        largest = max(int_list)
        new_dwg_index = largest + 1
        chrs = str(new_dwg_index)[4:]  # e.g., from 202100855 -> "00855"
        whittled = chrs
        for x in chrs:                       # whittle off leading zeros
            if x=='0':
                whittled = whittled[1:]
            else:
                break
        whittled = whittled.zfill(3)      # e.g. "5" to "005", or "13" to "013"
        dwgNo = int(str(year) + whittled)
    else:
        dwgNo = year*1000 + 1  # if no ints in list, then is 1st dwg no. for a new year
        d = str(dwgNo)
        new_dwg_index = int(d[:4] + (9 % len(d))*'0' + d[4:])
    if ((partNo.isnumeric() and len(partNo) == 4) or
           (len(partNo) == 5 and partNo[:4].isnumeric() and partNo[-1] == '-')):
        partNo = partNo[:4] + '-' + str(year) + '-' + str(dwgNo)[4:]
    return dwgNo, partNo, new_dwg_index


def search(searchterm, radio_button_on=False, caller_is_SearchResults=False):
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
            sqlSelect +=  '''(dwg GLOB '{0}' OR part GLOB '{0}' OR description GLOB '{0}'
                              OR author GLOB '{0}'
                              OR date GLOB '{0}') AND '''.format(i)
        sqlSelect = sqlSelect[:-5] + ') OR ('
    sqlSelect = sqlSelect[:-6] + ') ORDER BY dwg_index DESC'
    try:
        conn = sqlite3.connect("dwglog2.db")
        with conn:
            c = conn.cursor()
            result = c.execute(sqlSelect)
        rows = result.fetchall()
        if caller_is_SearchResults:
            return rows
        srch = SearchResults(rows, searchterm, radio_button_on)
        srch.show()  # https://stackoverflow.com/questions/11920401/pyqt-accesing-main-windows-data-from-a-dialog
        srch.exec_()
    except Exception:
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setWindowTitle('Error')
        msgbox.setText('Could not find text searched for.')
        msgbox.exec_()


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
    if column in [0, 1, 2, 3]:
        k[column] = k[column].upper()
    elif column == 4:
        k[4] = k[column].lower()
    overwrite = False
    originalnum = False
    pnerr = False
    pnWillChgWithDwgNo = False
    showConfirmationMsg = True

    # === preliminary setup... need some data from the database
    conn = None
    try:
        if column <= 1:
            #conn = sqlite3.connect('dwglog2.db')
            conn = sqlite3.connect(sqldatafile)  # sqldatafile is a global variable
            c = conn.cursor()
        if column == 0:
            c.execute("SELECT dwg_index FROM dwgnos ORDER BY dwg_index DESC LIMIT 1")
            result = c.fetchone()
            lastIndex = result[0]
            c.execute("SELECT dwg_index, part FROM dwgnos WHERE dwg = '" + clicked_text + "'")
            result = c.fetchone()
            currentIndex = result[0]
            currentPN = result[1]
        elif column == 1:
            c.execute("SELECT dwg_index, part, description FROM dwgnos WHERE dwg = '" + k[0] + "'")
            result = c.fetchone()
            currentIndex = result[0]
            currentDescrip = result[2]
            currentPN = result[1]      # name was currentPart
        if column <= 1:
            c.close()
            conn.close()
            
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        message(errmsg, 'Error')
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()

    # === analyze column input to determine what should happen
    # case 1: delete a record:
    if column == 0 and k[0].lower() in ('delete', 'remove', 'del', 'rm'):
        k[0] = 'delete'
    # case 2: user enters what appears to be a legit dwg. no.:
    elif column == 0 and  k[0].isdigit() and (k[0][:2] == '20') and (len(k[0]) >= 7):
        proposedNewIndex = int(k[0][:4] + (9 % len(k[0]))*'0' + k[0][4:])
        # Is currentPN in sync w/ dwg no. which will allow to update to a new PN?
        if currentPN != updatePN(currentPN, currentIndex, proposedNewIndex):
            pnWillChgWithDwgNo = True
        maxAllowedIndex = lastIndex + 50
        if proposedNewIndex > maxAllowedIndex:
            k[0] = 'abort0_maxexceeded'
    # case 3: dwg. no. erased e.g. 104119, to get back program generated no., e.g. 2020867
    elif column == 0 and k[0].strip() == '':
        originalnum = True
        k[0] = str(indexnum2dwgnum(currentIndex))
    # case 4: program generated no. overwritten, e.g. 2020867 overwritten by 104119
    elif column == 0:
        overwrite = True
    elif column == 1:  # column containing the pn
        k[1] = k[1][:30]
        lst = k[1].split('-')
        lst2 = clicked_text.split('-')
        dg = str(indexnum2dwgnum(currentIndex))
        # if pn looks to be in sync w/ dwg no., standard change notice to be shown.
        # else if looks same except last digits, verify if this chqange really wanted.
        # Note, 1st group of digits, i.e, 0300, 2730, etc. not taken into account
        if ('-' in k[1] and k[1].count('-') == 2 and len(lst) == 3 and
                all(lst) and lst[1] == dg[:4] and lst[2] == dg[4:]):
            pnerr = False
        # user in inadvertantly trying to change the dwg no. by changing the pn
        elif ('-' in k[column] and k[column].count('-') == 2 and len(lst) == 3 and
                all(lst) and lst[1] == dg[:4] and lst[2] != dg[4:]):
            pnerr = True
        # if cell left empty, attempt to fill with a "syncronized" pn,
        # like 0300-2020-421 for dwgno 2020421
        elif (not k[1].strip() and '-' in clicked_text and
                  clicked_text.count('-') == 2  and len(lst2) == 3 and all(lst2)):
            k[1] = lst2[0] + '-' + dg[:4] + '-' + dg[4:]
        # if cell has 5 characters, like '0300-', fill in with synced pt. no.
        elif (len(k[1]) == 5 and k[1].endswith('-')):
            k[1] = k[1] + dg[:4] + '-' + dg[4:]
            showConfirmationMsg = False
        # if cell has 10 characters, like '0300-2020', fill in with synced pt. no.
        elif (len(k[1]) == 10 and k[1].endswith('-') and k[1][5:9] == dg[:4]):
            k[1] = k[1] + k[0][4:]

        if (not currentDescrip.strip() and len(k[1]) >= 13 and k[1][4] == '-'
            and  int(k[1][:4]) in pndescrip):
            k[2] = pndescrip[int(k[1][:4])]
    elif column == 2:
        k[2] = k[2][:40]   # limit the description to 40 characters, the same as SyteLine
    elif column == 3 and k[3].count('/') == 2:  # the column containing the date
        j = k[3].split('/')
        if (all(i.isdigit() for i in j)
                and (1 <= int(j[0]) <= 12)
                and (1 <= int(j[1]) <= 31)
                and (1998 <= int(j[2]) <= 2099)):
            k[3] = j[0].zfill(3)[-2:] + '/' + j[1].zfill(3)[-2:] + '/' + j[2]
        else:
            return  # Entered date doesn't make sense.  Make no change.
    elif column == 3:
        return  # Entered date doesn't make sense.  Make no change.
    elif column == 4:
        k[4] = k[4].lower()    # make the author name lower case

    # === Generate appropriate validation message to present to the user
    if (k[column] == 'abort0') or (k[column] == 'abort0_maxexceeded'):
        if k[column] == 'abort0_maxexceeded':
            msg = ('The maximum allowable increase for a drawing number ' +
                   'is 50.\n ' + str(indexnum2dwgnum(maxAllowedIndex)) +
                   ' is the max in this case.')
        else:
            msg = 'Improper dwg. no.'
        message(msg, 'Error', msgtype='Warning', showButtons=False)
        return
    elif k[column] == 'delete':
        msgtitle = 'Delete?'
        msg = ('dwg:      ' + clicked_text + '\nptno:     ' + k[1] + '\ndescrip: '
                + k[2] + '\ndate:     ' + k[3] + '\nauthor:  ' + k[4])
    elif overwrite == True:
        msgtitle = 'Overwrite?'
        msg = ('Warning: You are about to OVERWRITE a standard drawing number.\n\n' +
               'See "Help > Update a field > Only if company policy permits" \n\n' +
               'from: ' +  clicked_text + '\nto:     ' + k[column])
    elif pnerr == True:
        msgtitle = 'Warning!'
        msg = ('The drawing number WILL NOT be updated.  The drawing number\n' +
               'will no longer be in sync with the part number.  To keep in sync,\n' +
               'change instead the drawing number.\n\n' +
               'See "Help > Update a field > A drawing number may be changed." \n\n' +
               'from: ' +  clicked_text + '\nto:     ' + k[column])
    elif pnWillChgWithDwgNo:
        msgtitle = 'Update?'
        msg =  ('from: ' +  clicked_text + '\nto:     ' + k[column])
        msg += ('\n            and  \n')
        msg += ('from: ' +  currentPN  + '\nto:     '  + updatePN(currentPN, currentIndex, proposedNewIndex))
    else:
        msgtitle = 'Update?'
        msg = ('from: ' +  clicked_text + '\nto:     ' + k[column])

    # === Generate the sqlite command to use to update the database
    if column == 0 and k[0] == 'delete':  # case 1, delete
        sqlUpdate = "DELETE from dwgnos WHERE dwg = '" + clicked_text + "'"
    elif column == 0 and originalnum == True:  # case 3, original
        sqlUpdate = ("UPDATE dwgnos SET " +
                     "dwg = '" + str(indexnum2dwgnum(currentIndex)) +
                     "' WHERE dwg = '" + clicked_text + "'")
    elif column == 0 and overwrite == True:  # case 4, overwrite
        sqlUpdate = ("UPDATE dwgnos SET " +
                    "dwg = '" + str(k[0]) +
                    "' WHERE dwg_index = " + str(currentIndex))
    elif column == 0:  # case 2, legit dwg no.
        sqlUpdate = ("UPDATE dwgnos SET " +
                     "dwg = '" + str(indexnum2dwgnum(proposedNewIndex)) +
                     "', part = '" + updatePN(currentPN, currentIndex, proposedNewIndex) +
                     "', dwg_index =  " + str(proposedNewIndex) +
                     " WHERE dwg = '" + clicked_text + "'")
    elif column == 1:
        sqlUpdate = ("UPDATE dwgnos SET " + colnames[column]
                     + " = '" + k[column] + "', description = '" + k[2] + "' WHERE dwg = '" + k[0]) + "'"
    else:
        sqlUpdate = ("UPDATE dwgnos SET " + colnames[column]
                     + " = '" + k[column] + "' WHERE dwg = '" + k[0] + "'")

    # ===  Show validation message to user.  retval is user's response (OK or Cancel)
    if showConfirmationMsg == True:
        retval = message(msg, msgtitle, msgtype='Warning', showButtons=True)
        userresponse = True if retval == QMessageBox.Ok else False
    else:
        userresponse = True

    # === Finally, update the database
    conn = None
    try:
        #userresponse = True if retval == QMessageBox.Ok else False
        if userresponse == True:
            #conn = sqlite3.connect("dwglog2.db")
            conn = sqlite3.connect(sqldatafile)  # sqldatafile is a global variable
            c = conn.cursor()
            c.execute(sqlUpdate)
            conn.commit()
            c.close()
            conn.close()
            
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        message(errmsg, 'Error')
        
    finally:
        if conn:
            conn.close()


def message(msg, msgtitle, msgtype='Warning', showButtons=False):
    '''
    UI message to show to the user

    Parameters
    ----------
    msg: str
        Message presented to the user.
    msgtitle: str
        Title of the message.
    msgtype: str, optional
        Type of message.  Currenly only valid input is 'Warning'.
        The default is 'Warning'.
    showButtons: bool, optional
        If True, show OK and Cancel buttons. The default is False.

    Returns
    -------
    retval: QMessageBox.StandardButton
        "OK" or "Cancel" is returned
    '''
    msgbox = QMessageBox()
    if msgtype == 'Warning':
        msgbox.setIcon(QMessageBox.Warning)
    elif msgtype == 'Information':
        msgbox.setIcon(QMessageBox.Information)
    else:
        msgbox.setIcon(QMessageBox.NoIcon)
    msgbox.setWindowTitle(msgtitle)
    msgbox.setText(msg)
    if showButtons:
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msgbox.exec_()
    return retval


def indexnum2dwgnum(dwg_index):
    ''' A number from the column named dwg_index looks something like
    202000873.  From that number make it a suitable number to fit into
    the column named dwg.  So in this case the suitable number to apply is
    2020873.  Another example: for 202100034 the dwg no. would be 2021034

    Parameters
    ----------
    dwg_index : int
        Number from the column name "dwg_index".  (This column is hidden to
        the user.  It resides in the database file dwglog2.db.)

    Returns
    -------
    int
        A new drawing number.  It corresponds to dwg_index.
    '''
    chrs = str(dwg_index)[4:]
    whittled = chrs
    for x in chrs:                       # whittle off leading zeros
        if x=='0':
            whittled = whittled[1:]
        else:
            break
    whittled = whittled.zfill(3)      # e.g. "5" to "005", or "13" to "013"
    return int(str(dwg_index)[:4] + whittled)


def updatePN(oldpn, oldindexNo, newIndexNo):
    ''' If the user changes the drawing no. from, for example, 2020876 to
    2020925, and the part no. is 0300-2020-876, the part no. should change to
    0300-2020-925.  On the other hand if, for example, the part no. is
    6100-0100-315, that is it doesn't have a program generated number, the
    part no. should be left as 6100-0100-315.

    Parameters
    ----------
    pn : str
        orignal part no., from column "part"
    dwgNo : str
        original drawing no., from column "dwg"
    indexNo : int
        original index no., from column "dwg_index"
    newIndexNo : int
        The new index no. that the user is establishing.

    Returns
    -------
    str
       New pn if it was originally based on indexNo. Otherwise return return
       the original pn
    '''
    d = indexnum2dwgnum(oldindexNo)  # old dwgNo derived from oldindexNo
    p = str(oldpn)[:4] + '-' + str(d)[:4] + '-' + str(d)[4:]   # pn if it were generated from oldindexNo

    if p == oldpn:  # that is, is oldpn what would have been generated, like 0300-2020-876?
        d2 = indexnum2dwgnum(newIndexNo)
        newpn = str(oldpn)[:4] + '-' + str(d2)[:4] + '-' + str(d2)[4:]
        return newpn
    else:
        return oldpn


def get_settingsfn():
    '''Get the file name used to store settings for the dwglog2 program.
    
    1.  Get the pathname of the file named settings.txt.  It will be in a 
    directory on a user's local machine and within his user folders.  On a 
    Windows  machine the name will be something like 
    C:\\Users\\Ken\\AppData\\Local\\dwglog2\\settings.txt.  And on a Linux
    machine it will be something like /home/ken/.dwglog2/settings.txt.
    
    2.  If that filename didn't already exist, crete it, and put into it:
    "{'configdb_location': '" + defaultsqldatafile + "'}" , where 
    defaultsqldatafile will be the file named dwglog2.db and will be in the
    same directory as that of settings.txt described in note 1 above.  So then,
    the contents of the settings.txt file will look something like:
        
        "{'sqldatafile': 'C:\\Users\\Ken\\AppData\Local\\dwglog2\\dwglog2.db'}".
        
    (Pytnon requires \\ to represent a \ in a string)
    '''
    if sys.platform[:3] == 'win':
        datadir = os.getenv('LOCALAPPDATA')
        path = os.path.join(datadir, 'dwglog2')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        settingsfn = os.path.join(datadir, 'dwglog2', 'settings.txt')
        defaultsqldatafile = os.path.join(datadir, 'dwglog2', 'dwglog2.db')
                
    elif sys.platform[:3] == 'lin' or sys.platform[:3] == 'dar':  # linux or darwin (Mac OS X)
        homedir = os.path.expanduser('~')
        path = os.path.join(homedir, '.dwglog2')
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True) 
        settingsfn = os.path.join(homedir, '.dwglog2', 'settings.txt')
        defaultsqldatafile = os.path.join(homedir, '.dwglog2', 'dwglog2.db')
            
    else:
        printStr = ('At function "get_settingsfn", a suitable path was not found to create\n'
                    'a file named settings.txt.  Notify the programmer of this error.')
        print(printStr) 
        return ''
    
    _bool = os.path.exists(settingsfn)
    if not _bool or (_bool and os.path.getsize(settingsfn) == 0):
        with open(settingsfn, 'w') as file: 
            file.write("{'sqldatafile': '" + defaultsqldatafile + "'}")
                
    return settingsfn


def get_sqldatafile():
    '''
    Get from the file settings.txt the pathname of the file dwglog2.db

    Returns
    -------
    sqldatafile : str
        pathname of file dwglog2.db
    '''
    settingsfn = get_settingsfn()  # pathname of the settings.txt file
    try:
        with open(settingsfn, "r") as file:
            x = file.read()
            x = x.replace('\\', '\\\\')
            settingsdic = eval(x)
            sqldatafile = settingsdic['sqldatafile']
    except Exception as e:  # it an error occured, moset likely and AttributeError
        msg =  "error10 at get_sqldatafile.  " + str(e)
        print(msg)
        message(msg, 'Error', msgtype='Warning', showButtons=False)
    return sqldatafile


pndescrip = {300:"BASEPLATE ? CS", 2202:'CTRL/LAYOUT PNL ??HP ???V',
   2223:'CTRL/LAYOUT PNL ??HP ???V', 2250:'CTRL/LAYOUT PNL ??HP ???V',
   2273:'CTRL/LAYOUT PNL ??HP ???V CONTROLDEK',
   2277:'CTRL/LAYOUT PNL ??HP ???V CONTROLDEK',
   2451:'PLACARD SET FOR ?', 2704:"COVER PLATE ? CS", 2708:"ENDPLATE ? CS",
   2724:'SHELL ??"OD X ??"LG X ??"THK CS', 2728:"BRACKET ? CS",
   2730:"BRACKET CTRL PNL height?Xwidth? CS",
   2922:"FILTER INLET ?", 3060:"FITTING HOSE BARB ?",
   3420:'FLOW ORIFICE PLATE ??"ID',
   3510:'GASKET ?mtl? ??"OD X ??"ID X ??"THK', 3700:"GUARD COUPLING ?",
   3705:"GUARD FINGER ?", 3715:"GUARD V-BELT ?", 4010:"HT EX ?", 4715:"KIT ?",
   4790:"TAG ?", 5130:"HULLVAC INLET ?", 6000:"RECEIVER TANK HORZ ??? GAL CS",
   6004:"RECEIVER TANK VERT ??? GAL CS", 6005:"RECEIVER TANK VERT ASSY ??? GAL CS",
   6006:"RCVR TANK VERT W/PLATFORM ??? GAL CS",
   6008:"RCVR TANK HORZ GRASSHOPPER ??? GAL CS",
   6050:"RISERBLOCK ? CS", 6405:"CONDENSATE TANK ? CS", 6410:'SEPARATOR OIL FR ??"OD CS',
   6415:'SEPARATOR FR ??"OD CS', 6420:"SEPARATOR KO ? CS", 6425:'SEPARATOR NR ??"OD CS',
   6430:'SEPARATOR NR/PR ??"OD CS', 6775:"STRAINER ? CS", 6820:"SUB ASSY DISCH MANIFOLD ? CS",
   6825:"SUB ASSY INLET/DISCH MNFLD ? CS", 6830:"SUB ASSY INLET MANIFOLD ? CS",
   6840:"SUB ASSY SEPARATOR ? CS", 6860:"SUB ASSY pump? ??HP MTR",
   6875:"SUB ASSY PIPING ? CS", 6882:'SUB ASSY KO TANK ?? GAL ??"OD CS',
   6885:"SUB ASSY LEVEL SWITCH ?", 6886:"SUB ASSY V-BELT ?HP",
   6890:"SUB ASSY PIPING ? CS", 6891:"SUB ASSY 2ND STG OIL FILTER ?",
   7318:"VALVE CHK INLINE ?"}


try:
    import descriptions
    pndescrip.update(descriptions.descriptions)
except ModuleNotFoundError as inst:
    print('Error, module not found: ', inst)
except Exception as inst:
    print('Warning: ', inst)
    msgtitle =  "Warning"
    msg = ('The file named descriptions.py failed to load.  The dwglog2\n' +
           'program will attempt to continue without the data provided by\n' +
           'this file, but may crash.  Please fix the error in descriptions.py.\n' +
           "For more information, see dwglog2's help information.  As a last\n" +
           'resort, delete the descriptions.py file.\n\n' +
           str(inst))
    message(msg, msgtitle)








app = QApplication(sys.argv)
if (QDialog.Accepted == True):
    window = MainWindow()
    window.show()
    window.loaddata()
sys.exit(app.exec_())












