#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from bs4 import BeautifulSoup
import re
import shutil
import pandas as pd
import sys

def extractPage(page, idx_body, idx_page, path):
    soup = BeautifulSoup(page, "lxml")
    if soup.body:
        soup = soup.body

    for i, table in enumerate(soup.find_all('table')):
        df = readTable(table)
        fname = 'table%03d_body%03d-page%03d.txt' % (i, idx_body, idx_page)
        with open(path + fname, 'w') as f:
            print('--Write table: ', i, ' to csv.')
            df.to_csv(f)
        table.extract()

    text = '\n'.join(list(soup.stripped_strings))
    fname = 'text_body%03d-page%03d.txt' % (idx_body, idx_page)
    with open(path + fname, 'w') as f:
        print('--Write text file.')
        f.write(text)

def splitTextFile(fname, path):
    # check if output dir exists
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
        
    # read original data file  
    with open(fname, 'r', encoding='utf-8') as f:
        source_code = f.read()
    pattern = re.compile('[\r\n\t]')
    html = pattern.sub('', source_code) 
    
    # split html by 'body'
    bodys = re.findall('<body.*?</body>', html)
    
    # split body to pages by horizontal line
    segments = []
    for i, body in enumerate(bodys):
        pages = re.split('<hr.*?>', body)
        segments.append(pages)
        for j, page in enumerate(pages):
            filename = path + 'body%03d-page%03d.html' % (i, j)
            print('Write file: ', filename)
            with open(filename, 'w') as f:
                f.write(page)
                
            # extract information from page
            extractPage(page, i, j, path)
        
    return(segments)

def readTable(table):
    matrix = []
    if table.th:
        data = []
        for j, col in enumerate(table.th.find_all('td')):
            data.append(''.join(list(col.stripped_strings)))
        matrix.append(data)

    for i, row in enumerate(table.find_all('tr')):
        data = []
        for j, col in enumerate(row.find_all('td')):
            data.append(''.join(list(col.stripped_strings)))

        matrix.append(data)
    return(pd.DataFrame(matrix))

if __name__ == '__main__':
	#print(len(sys.argv))
	if len(sys.argv) > 1:
		fname = sys.argv[1]
	else:
		fname = "EdgarFillings_full/Form10K/1467858/1467858_10-K_2017-02-07_0001467858-17-000028.txt"
	print('Input file: ', fname)
	output_path = 'output/'
	segments = splitTextFile(fname, output_path)
