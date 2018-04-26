## Python script to download list of Canadian charities from the CRA website

# Diarmuid McDonnell, Alasdair Rutherford
# Created: 12 April 2018
# Last edited: captured in Github file history


import csv
import requests
import os
import os.path
import errno
import zipfile
import io
from time import sleep

from downloaddate_function import downloaddate



# Run the downloaddate function to get the date 'benefacts_master.py' was executed.
ddate = downloaddate()

projpath = 'C:/Users/mcdonndz-local/Desktop/github/paper-istr-2018/'
datapath = 'C:/Users/mcdonndz-local/Desktop/data/paper-istr-2018/data_raw/'

print(projpath)
print(datapath)

# Define urls where data can be found

base_results_url = 'http://www.cra-arc.gc.ca/ebci/haip/srch/advancedsearchresult-eng.action?'
base_download_url = 'http://www.cra-arc.gc.ca/ebci/haip/srch/download-eng.action?'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# Create a dictonary with the different types of charities and their search terms

chartype = {'CharitableOrganisation': 'C', 'PrivateFoundation': 'B', 'PublicFoundation':'A'} 

# Perform the search

for key, val in chartype.items():

	print('---------------------')
	print(key)

	try:
		os.mkdir(datapath+'/'+key)
	except:
		print('Folder already exists')

	s = requests.session()

	search_url = base_results_url + 'n=&b=&q=&s=+&d=&e=+&c=&v=+&z=&g=' + val + '&t=+&y=+&p=1'
	print(search_url)

	rsearch = s.get(search_url, headers=headers)
	print('Search results:', rsearch.status_code)

	download_url = base_download_url + 'n=&b=&q=&s=+&d=&e=+&c=&v=+&z=&g=' + val + '&t=+&y=+&p=1'

	rdoc = s.get(download_url, headers=headers)
	print('Download:', rdoc.status_code)

	z = zipfile.ZipFile(io.BytesIO(rdoc.content))
	print(z.namelist)
	z.extractall(datapath+'/'+key)
	print('...extracted')
	print('')


# Write contents of .txt files to csv

outputfile = datapath + '/' +  'canada_register.csv'
varnames = ['BN/Registration Number', 'Charity Name', 'Charity Status', 'Effective Date of Status', 'Sanction', 'Designation Code', 'Category Code', 'Address', 'City', 'Province', 'Country', 'Postal Code']
print(len(varnames))
orgcounter = 0

# Open the output file and write the header
with open(outputfile, 'w', newline='') as outcsv:
	writer = csv.writer(outcsv, varnames)
	writer.writerow(varnames)

	for key, val in chartype.items():
		dir_name = datapath + '/' + key
		print('----------------')
		print('|', key, dir_name)

		for item in os.listdir(dir_name): # Loop through files in directory
			if item.startswith('Charities_results_'): # Check for results file
				file_name = dir_name + "/" + item # Get full path of files
				print('		Reading ', file_name) 
				with open(file_name, 'r') as f:
					reader = csv.reader(f, delimiter='\t')
					next(reader) # Skip the first row as we already have the headings
					for row in reader:
						#print(row)
						writer.writerow(row)
						orgcounter +=1
			else:
				print('		No need to write this file as it does not contain charity details')			

print('Merged details of', orgcounter, 'Canadian nonprofit organisations.')
print('All done.')


#########################################################################################################

#########################################################################################################

# Search for financial information about these charities

