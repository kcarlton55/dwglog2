#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 21:12:52 2021

@author: ken
"""


from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import (QTableWidget, QMainWindow, QDialog, QApplication,
                             QToolBar, QStatusBar, QAction, QLabel, QLineEdit,
                             QTableWidgetItem, QVBoxLayout, QPushButton, QComboBox,
                             QHBoxLayout, QMessageBox, QDialogButtonBox, QRadioButton)
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
import sys
import sqlite3
import os
from datetime import datetime, date
import webbrowser



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
    
    # === preliminary setup... need some data from the database 
    try:
        if column <= 1:
            conn = sqlite3.connect('dwglog2.db')
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
            currentIndex = result[0]
            currentDescrip = result[2]
            currentPN = result[1]      # name was currentPart
        if column <= 1:
            c.close()        
            conn.close()
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        message(errmsg, 'Error')
 
    # === analyze column input to determine what should happen next
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
    elif column == 1:
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
        # if cell has 10 characters, like '0300-2020', fill in with synced pt. no.
        elif (len(k[1]) == 10 and k[1].endswith('-') and k[1][5:9] == dg[:4]):
            k[1] = k[1] + k[0][4:]
           
        if (not currentDescrip.strip() and len(k[1]) >= 13 and k[1][4] == '-'
            and  int(k[1][:4]) in pndescrip):
            k[2] = pndescrip[int(k[1][:4])]
    elif column == 2:
        k[2] = k[2][:40]
    elif column == 3 and k[3].count('/') == 2:  # date column
        j = k[3].split('/')
        if (all(i.isdigit() for i in j)
                and (1 <= int(j[0]) <= 12)
                and (1 <= int(j[1]) <= 31)
                and (1998 <= int(j[2]) <= 2099)):
            k[3] = j[0].zfill(3)[-2:] + '/' + j[1].zfill(3)[-2:] + '/' + j[2]
        else:
            return  # Entered date doesn't make sense.  Make no change.
    elif column == 3:to place a a Dekker drawing
        return  # Entered date doesn't make sense.  Make no change.   
    elif column == 4:
        k[4] = k[4].lower()    
        
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
                + k[2] + '\ndate:     ' + k[3] + to place a a Dekker drawing'\nauthor:  ' + k[4])
    elif overwrite == True:
        msgtitle = 'Overwrite?'
        msg = ('Warning: You are about to overwrite a standard drawing\n' +
               'number used at Dekker. If overwritten, to retrieve the\n' +
               'original number edit the drawing number field and leave it\n' +
               'blank.  Press Enter and the original number will reappear.\n' +
               'This is true even if you close the program and reopen it.')
    elif pnerr == True:
        msgtitle = 'Warning!'
        msg = ('It looks like you are trying to enter a part no. that this\n' +
               'program would normally generate. Do you expect that the\n' +
               'drawing no. will update to be in sync with this part no.?\n' +
               '(e.g. dwg. no. 2020410 is in sync with pn 0300-2020-410.)\n' +
               'If so, you are taking the wrong approach.\n\n ' +
             
               'Instead change the drawing number.  The part number,\n' +
               'assuming it is currenly in sync with the drawing mumber, will  \n' +
               'automatically update to be in sync with the new drawing number.')
    elif pnWillChgWithDwgNo:
        msgtitle = 'Update?'
        msg =  ('from: ' +  clicked_text + '\nto:     ' + k[column])
        msg += ('\n            and,  \n')
        msg += ('from: ' +  currentPN  + '\nto:     '  + updatePN(currentPN, currentIndex, proposedNewIndex))
    else:
        msgtitle = 'Update?'
        msg = ('from: ' +  clicked_text + '\nto:     ' + k[column])

    # ===  Show validation message to user 
    retval = message(msg, msgtitle, msgtype='Warning', showButtons=True)    
    
    # === Generate the command to command to update the database
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
    elif column == 0:  # case 2, legit no.
        sqlUpdate = ("UPDATE dwgnos SET " + 
                     #colnames[0] + " = " + k[0] +
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
    
    # === Update the database
    userresponse = True if retval == QMessageBox.Ok else False
    try:
        if userresponse == True:    
            conn = sqlite3.connect("dwglog2.db")
            c = conn.cursor()
            c.execute(sqlUpdate)
            conn.commit()
            c.close()        
            conn.close()
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        message(errmsg, 'Error')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    if column == 0:
        conn = sqlite3.connect('dwglog2.db')
        c = conn.cursor()
        c.execute("SELECT dwg_index FROM dwgnos ORDER BY dwg_index DESC LIMIT 1")
        result1 = c.fetchone()
        c.execute("SELECT dwg_index, part FROM dwgnos WHERE dwg = '" + clicked_text + "'")
        result2 = c.fetchone()
        c.close()        
        conn.close()
        currentIndex = result2[0]
        currentPN = result2[1]
        lastIndex = result1[0]
    if column == 1:
        conn = sqlite3.connect('dwglog2.db')
        c = conn.cursor()
        c.execute("SELECT dwg_index, part, description FROM dwgnos WHERE dwg = '" + k[0] + "'")
        result3 = c.fetchone()
        c.close()        
        conn.close()
        currentIndex = result3[0]
        currentDescrip = result3[2]
        currentPart = result3[1]
        k[column] = k[column][:30]
        lst = k[column].split('-')
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
        # if cell has 10 characters, like '0300-2020', fill in with synced pt. no.
        elif (len(k[1]) == 10 and k[1].endswith('-') and k[1][5:9] == dg[:4]):
            k[1] = k[1] + k[0][4:]
            
        if (not currentDescrip.strip() and len(k[1]) >= 13 and k[1][4] == '-'
            and  int(k[1][:4]) in pndescrip):
            k[2] = pndescrip[int(k[1][:4])]
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
    # case 1: delete a record:    
    elif column == 0 and k[column].lower() in ('delete', 'remove', 'del', 'rm'):
        k[column] = 'delete'
    # case 2: user enters what appears to be a legit dwg. no.:
    elif column == 0 and  k[0].isdigit() and (k[0][:2] == '20') and (len(k[0]) >= 7):
        proposedNewIndex = int(k[0][:4] + (9 % len(k[0]))*'0' + k[0][4:])
        
        if currentPN != updatePN(currentPN, currentIndex, proposedNewIndex):
            pnWillChgWithDwgNo = True

        maxAllowedIndex = lastIndex + 50
        if proposedNewIndex > maxAllowedIndex:
            k[column] = 'abort0_maxexceeded'
    # case 3: dwg. no. erased e.g. 104119, to get back program generated no., e.g. 2020867
    elif column == 0 and k[0].strip() == '':
        originalnum = True
        k[0] = str(indexnum2dwgnum(currentIndex))
    # case 4: program generated no. overwritten, e.g. 2020867 overwritten by 104119
    elif column == 0:
        overwrite = True
    elif column == 4:
        k[column] = k[column].lower()
        
    try:
        if k[column] == 'abort3':
            return
        elif (k[column] == 'abort0') or (k[column] == 'abort0_maxexceeded'):
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
            msg = ('Warning: You are about to overwrite a standard drawing\n' +
                   'number used at Dekker. If overwritten, to retrieve the\n' +
                   'original number edit the drawing number field and leave it\n' +
                   'blank.  Press Enter and the original number will reappear.\n' +
                   'This is true even if you close the program and reopen it.')
        elif pnerr == True:
            msgtitle = 'Warning!'
            msg = ('It looks like you are trying to enter a part no. that this\n' +
                   'program would normally generate. Do you expect that the\n' +
                   'drawing no. will update to be in sync with this part no.?\n' +
                   '(e.g. dwg. no. 2020410 is in sync with pn 0300-2020-410.)\n' +
                   'If so, you are taking the wrong approach.\n\n ' +
                 
                   'Instead change the drawing number.  The part number,\n' +
                   'assuming it is currenly in sync with the drawing mumber, will  \n' +
                   'automatically update to be in sync with the new drawing number.')
        elif pnWillChgWithDwgNo:
            msgtitle = 'Update?'
            msg =  ('from: ' +  clicked_text + '\nto:     ' + k[column])
            msg += ('\n            and,  \n')
            msg += ('from: ' +  currentPN  + '\nto:     '  + updatePN(currentPN, currentIndex, proposedNewIndex))
        else:
            msgtitle = 'Update?'
            msg = ('from: ' +  clicked_text + '\nto:     ' + k[column])
        retval = message(msg, msgtitle, msgtype='Warning', showButtons=True)
        
        if retval == QMessageBox.Cancel:
            userresponse = False
        elif retval == QMessageBox.Ok:
            userresponse = True       
        if userresponse == True:    
            conn = sqlite3.connect("dwglog2.db")
            c = conn.cursor()
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
            elif column == 0:  # case 2, legit no.
                sqlUpdate = ("UPDATE dwgnos SET " + 
                             #colnames[0] + " = " + k[0] +
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

            c.execute(sqlUpdate)
            conn.commit()
            c.close()        
            conn.close() 
            
    except sqlite3.Error as er:
        errmsg = 'SQLite error: %s' % (' '.join(er.args))
        message(errmsg, 'Error')
    except Exception as er:
        QMessageBox.warning(QMessageBox(), 'Error', er.args[0])
   
            