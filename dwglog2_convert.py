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
import sqlite3
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.width', 200)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                        description="If it doesn't already exist, create an sqlite database file " +
                        'named dwglog2.db and import data from a csv or Excel file into it.  If the file ' +
                        'database file already exist, append data from a csv or Excel file to the ' +
                        "existing data.  The table within the database " +
                        'file will be named "dwgnos".  Column names are dwg, part, description, ' +
                        'date, and author.  Data types for all data will be text.  The ' +
                        'format of dates will be YYYY-MM-DD')
    parser.add_argument('file_in', help='Name of file Excel or csv file to import.')
    parser.add_argument('file_out', help='Name of file to export to.', default='dwglog2.db')
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()     
    dwglog2_convert(args.file_in, args.file_out)
    
    
def dwglog2_convert(fn_in, fn_out='dwglog2.db'):
    _, ext_in = os.path.splitext(fn_in)
    _, ext_out = os.path.splitext(fn_out)
    viable = ['.csv', '.txt', '.xls', '.xlsx']
    if ext_in in viable and ext_out == '.db':
        excel2db(fn_in, fn_out)
    elif ext_in == '.db' and ext_out in viable:
        db2excel(fn_in, fn_out)
    else:
        print('Invalid file name.  Did file name end with .csv, .txt, .xls, .xlsx, or .db?')
    
        
def excel2db(fn_in, fn_out='dwglog2.db'):
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
        df.rename(columns={'Dwg No.':'dwg', 'Drawing Number':'dwg', 'Part No.':'part',
                           'Part Number':'part', 'Sheet Size':'Size',
                           'Description':'description', 'Date':'date', 'Drawing Date':'date',
                           'Author':'author'}, inplace=True)
        if 'Size' in df.columns:  # New dwglog2 program will not deal with sheet sizes: A, B, C, D
            del df['Size']

        df['date'] = pd.to_datetime(df['date'])
        print('Working...')
        df.sort_values(by=['dwg'], inplace=True, ascending=True)
        
        # code to export to sqlite db file:                
        conn = sqlite3.connect(fn_out)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS 
                        dwgnos(dwg_index INTEGER PRIMARY KEY NOT NULL UNIQUE,
                        dwg INTERGER NOT NULL UNIQUE, part TEXT, 
                        description TEXT, date TEXT NOT NULL, author TEXT)''')                                 
        df_dict = df.to_dict()        
        len_dict = len(df_dict['dwg'])
        not_unique = []
        for i in range(len_dict):
            dwg = str(df_dict['dwg'][i])  # e.g. 2021125            
            dwg_index = dwg[:4] + (9 % len(dwg))*'0' + dwg[4:] # e.g. 202100125      
            part = str(df_dict['part'][i])
            description = str(df_dict['description'][i])
            date = df_dict['date'][i]
            author = str(df_dict['author'][i])
            #_date = date.strftime("%Y-%m-%d")
            _date = date.strftime("%m/%d/%Y")
            try:
                c.execute("INSERT INTO dwgnos (dwg_index, dwg, part, description, date, author) VALUES (?,?,?,?,?,?)",
                                             (dwg_index, dwg, part, description, _date, author))
                conn.commit()
                print("{:7} {:8} {:32} {:42} {:12} {:14}".format(dwg_index, dwg, part, description, _date, author))  
            except:
                not_unique.append(dwg)             
        c.close()
        conn.close()
        print('Data sucessfully exported to ' + fn_out)
        if not_unique:
            print('Some drawing numbers from the imported file were not unique and have been discarded: ')
            print(not_unique)
    except:
        printStr = '\nError processing file: ' + fn_in + '\n'
        print(printStr) 
        

def db2excel():  # todo
    pass


def date2USAformat():  # todo
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