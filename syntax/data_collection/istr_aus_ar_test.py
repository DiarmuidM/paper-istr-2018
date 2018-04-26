# Annual Returns #

import itertools
import json
import csv
import re
import requests, zipfile, io
import os
import os.path
import errno
import urllib
from time import sleep
from bs4 import BeautifulSoup
from downloaddate_function import downloaddate


# Run the downloaddate function to get the date 'benefacts_master.py' was executed.
ddate = downloaddate()

projpath = 'C:/Users/mcdonndz-local/Desktop/github/paper-istr-2018/'
datapath = 'C:/Users/mcdonndz-local/Desktop/data/paper-istr-2018/data_raw/'


# Define urls where datasets can be found

url2016 = 'https://data.gov.au/dataset/7e073d71-4eef-4f0c-921b-9880fb59b206' # 2016 ACNC Annual Returns
url2015 = 'https://data.gov.au/dataset/86cad799-2601-4f23-b02c-c4c0fc3b6aff' # 2015 ACNC Annual Returns
url2014 = 'https://data.gov.au/dataset/d7992845-5d3b-4868-b012-71f672085412' # 2014 ACNC Annual Returns
url2013 = 'https://data.gov.au/dataset/cc9d8524-39d8-4374-84b9-20e9d1070e82' # 2013 ACNC Annual Returns

aisdatasets = [url2013, url2014, url2015, url2016]
expldatasets = [url2013, url2014, url2015, url2016]
groupdatasets = [url2014, url2015, url2016] # No group reports for 2013

# Download data
'''
for dataset in aisdatasets:

	r = requests.get(dataset, allow_redirects=True)
	soup = BeautifulSoup(r.text, 'html.parser')
	print(soup)
	links = soup.find_all('a')
	print(links)
	for link in links:
	   print(link.get('href'))
	arlink = soup.select_one("a[href*=datadotgovais]") # Find link with 'datadotgovais' in the href field
	print(arlink)

	aislink = arlink['href'] # Extract the href part of the <a> element.
	print(aislink)

	r = requests.get(aislink, allow_redirects=True)
	print(r.status_code, r.ok, r.headers)

	#print(r.content)
	z = zipfile.ZipFile(io.BytesIO(r.content))
	z.extractall(datapath + ddate)

print('Successfully downloaded annual return files for 2013-2016')

'''
# Download group reports #

year = 2014 # Define a counter for naming the files

for dataset in groupdatasets:

	r = requests.get(dataset, allow_redirects=True)
	soup = BeautifulSoup(r.text, 'html.parser')
	print(soup)
	links = soup.find_all('a')
	print(links)
	for link in links:
	   print(link.get('href'))
	arlink = soup.select("a[href*=group]") # Find link with 'group' in the href field
	print(arlink)
	print(len(arlink))

	aislink = arlink[1]['href'] # Extract the href part of the <a> element.
	print(aislink)

	r = requests.get(aislink, allow_redirects=True)
	print(r.status_code, r.ok, r.headers)

	# Write content to xlsx

	xlsxpath = datapath + ddate + '/' + 'ais_group_' + str(year) + '.xlsx'

	outxlsx = open(xlsxpath, 'wb')
	outxlsx.write(r.content)
	outxlsx.close()
	year +=1

	# 2015 is not working

# Download ancillary files #
'''
year = 2013 # Define a counter for naming the files

for dataset in expldatasets:

	r = requests.get(dataset, allow_redirects=True)
	soup = BeautifulSoup(r.text, 'html.parser')
	print(soup)
	links = soup.find_all('a')
	print(links)
	for link in links:
	   print(link.get('href'))
	arlink = soup.select_one("a[href*=explanatory]") # Find link with 'datadotgovais' in the href field
	print(arlink)

	aislink = arlink['href'] # Extract the href part of the <a> element.
	print(aislink)

	r = requests.get(aislink, allow_redirects=True)
	print(r.status_code, r.ok, r.headers)

	# Write content to pdf

	pdfpath = datapath + ddate + '/' + 'ais_' + str(year) + '_explanatory-notes.pdf'

	outpdf = open(pdfpath, 'wb')
	outpdf.write(r.content)
	outpdf.close()
	year +=1

# 2013 not working because it is a .docx
'''