#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 22:42:04 2020

@author: ken

ref: https://www.fullstackpython.com/blog/export-pandas-dataframes-sqlite-sqlalchemy.html

"""

import argparse
import sys
import os
import tempfile
import pandas as pd
from sqlalchemy import create_engine
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.width', 200)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                        description='Program converts a csv file to a sqlite database ' +
                        'file.  The csv file is derived from the database data of ' +
                        "Dekker's original Drawing Log program, or from the " +
                        'sqlite database from the Drawing Log 2 program.  The latter ' +
                        'program is a replacement for the former.')
    parser.add_argument('file_in', help='Name of file to import.')
    parser.add_argument('file_out', help='Name of file to export.')
 
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()     
    dwglog2_convert(args.file_in, args.file_out)
    
    
def dwglog2_convert(fn_in, fn_out):
    _, file_extension = os.path.splitext(fn_in)
    if (file_extension.lower() == '.csv' or file_extension.lower() == '.txt' or
            file_extension.lower() == '.xls' or file_extension.lower() == '.xlsx'):
        df = import_excel(fn_in)
        export2db(fn_out, df)
    elif file_extension.lower() == '.db':
        pass
    else:
        print('Invalid file type')
    
    
def import_excel(fn_in):
    try:
        _, file_extension = os.path.splitext(fn_in)
        if file_extension.lower() == '.csv' or file_extension.lower() == '.txt':
            data = make_csv_file_stable(fn_in)
            temp = tempfile.TemporaryFile(mode='w+t')
            for d in data:
                temp.write(d)
            temp.seek(0)
            df = pd.read_csv(temp, na_values=[' '], sep='$',
                             encoding='iso8859_1', engine='python',
                             dtype = str)
            temp.close()
        elif file_extension.lower() == '.xlsx' or file_extension.lower() == '.xls':
            df = pd.read_excel(fn_in, na_values=[' '])
            colnames = []
            for colname in df.columns:  # rid colname of '\n' char if exists
                colnames.append(colname.replace('\n', ''))
            df.columns = colnames
        print('Data sucessfully imported')
    except:
        printStr = '\nError processing file: ' + fn_in + '\nIt has been excluded from the BOM check.\n'
        print(printStr)
    return df
    
    

def export2db(fn_out, df):
    pass

def export2excel():
    pass



def make_csv_file_stable(filename):
    ''' Except for any commas in a parts DESCRIPTION, replace all commas
    in a csv file with a $ character.  Commas will sometimes exist in a
    DESCRIPTION field, e.g, "TANK, 60GAL".  But commas are intended to be field
    delimeters; commas in a DESCRIPTION field are not.  Excess commas in
    a line from a csv file will cause a program crash.  Remedy: change those 
    commas meant to be delimiters to a dollor sign character, $.
        
    Parmeters
    =========

    filename: string
        Name of SolidWorks csv file to process.

    Returns
    =======

    out: list
        A list of all the lines (rows) in filename is returned.  Commas in each
        line are changed to dollar signs except for any commas in the
        DESCRIPTION field.
    '''
    with open(filename, encoding="ISO-8859-1") as f:
        data1 = f.readlines()
    # n1 = number of commas in 2nd line of filename (i.e. where column header
    #      names located).  This is the no. of commas that should be in each row.
    n1 = data1[1].count(',')
    n2 = data1[1].upper().find('Description')  # locaton of the word DESCRIPTION within the row.
    n3 = data1[1][:n2].count(',')  # number of commas before the word DESCRIPTION
    data2 = list(map(lambda x: x.replace(',', '$') , data1)) # replace ALL commas with $
    data = []
    for row in data2:
        n4 = row.count('$')
        if n4 != n1:
            # n5 = location of 1st ; character within the DESCRIPTION field
            #      that should be a , character
            n5 = row.replace('$', '?', n3).find('$')
            # replace those ; chars that should be , chars in the DESCRIPTION field:
            data.append(row[:n5] + row[n5:].replace('$', ',', (n4-n1))) # n4-n1: no. commas needed
        else:
            data.append(row)
    return data