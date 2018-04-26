# Script to search and download Charity Register from ACNC API and annual returns submitted to ACNC 2013-2016
# Diarmuid McDonnell
# Created: 26 February 2018
# Last edited: captured in Github file history

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


# Charity Register #	

request = urllib.request.urlopen('https://data.gov.au/api/3/action/datastore_search?resource_id=eb1e6be4-5b13-4feb-b28e-388bf7c26f93&limit=100000') # Search for all charities
print(request.status, request.headers)
# I need to capture the last modified information so I can name the files/decide when to download etc.
'''
metadata = request.headers
print(type(metadata))
lastmod = metadata['Last-Modified']
print(lastmod)
print(len(lastmod))
udate = lastmod[5:16].replace(' ', '')
print(udate)
'''
response = request.read().decode('utf-8')
#print(response)
data = json.loads(response)
#print(data)
'''
	File structure: dictionary with 3 items, one of which ('result') is a dictionary with a list for some of its values.
	'result' contains variable names ['id'] in the 'fields' key, and observations in 'records' (list with one element: a dictionary).
'''
outputfilepath_csv = datapath + ddate + '/' + 'auscharities_' + ddate + '.csv'
outputfilepath_json = datapath + ddate + '/' + 'auscharities_' + ddate + '.json'
inputfilepath = outputfilepath_json
print(outputfilepath_csv)
print(outputfilepath_json)
print(inputfilepath)

## Export the json data to a .json file
with open(outputfilepath_json, 'w') as auscharitiesjson:
    json.dump(data, auscharitiesjson)

#Read JSON data into the regchar variable (i.e. a Python object)
with open(inputfilepath, 'r') as f:
	auschar = json.load(f)

print(len(auschar)) # Counts number of keys in the dictionary
print(len(auschar['result']))
#print(auschar['result'].keys()) # Looks like everything I need is in the 'result' key
#print(auschar['result'].values())
print('----------------------------------------------------')
print('                                                    ')
print('                                                    ')
#print(auschar['help'].values())
print('                                                    ')
print('                                                    ')
print('----------------------------------------------------')
print('                                                    ')
print('                                                    ')
#print(auschar['success'].values())

varnames = auschar['result']['records'][0].keys() # Extract the variable names from the dictionary keys of the first observation

# Write the results to a csv file #

with open(outputfilepath_csv, 'w', newline='') as outCSVfile:

	dict_writer = csv.DictWriter(outCSVfile, varnames)
	dict_writer.writeheader()
	dict_writer.writerows(auschar['result']['records'])



################################################################################################################################

################################################################################################################################



# Annual Returns #

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
'''
# Download ancillary files #

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