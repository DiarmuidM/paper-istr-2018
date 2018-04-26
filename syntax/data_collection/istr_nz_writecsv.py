# Script to search NZ Charities Services OData API
# Diarmuid McDonnell
# Created: 27 February 2018
# Last edited: Github file history records this

# Data guide: https://www.charities.govt.nz/charities-in-new-zealand/the-charities-register/open-data/

import itertools
import json
import csv
import re
import collections
import requests
import os
import os.path
import errno
import urllib
from time import sleep
import xml.etree.ElementTree as ET
from downloaddate_function import downloaddate
from xmlutils import xml2csv #pip install xmlutils


# Run the downloaddate function to get the date 'benefacts_master.py' was executed.
ddate = downloaddate()

datapath = 'C:/Users/mcdonndz-local/Desktop/data/nz_charity_data/data_raw/'

# Open xml files and write to csv #
regxml = datapath + ddate + '/' + 'nz_Organisations_' + ddate + '.xml'
regjson = datapath + ddate + '/' + 'nz_Organisations_' + ddate + '.json'
regcsv = datapath + ddate + '/' + 'nz_Organisations_' + ddate + '.csv'

# Define variable names for register
regvarnames = ['OrganisationId','AccountId','Name','CharityRegistrationNumber','WebSiteURL','EmailAddress1','Telephone1','Fax','CharityEmailAddress','CompaniesOfficeNumber','DateRegistered','deregistrationdate','Deregistrationreasons','EndOfYearDayofMonth','endofyearmonth','Establishedbyparliamentact','Excemptioncomment','Isincorporated','Maori_trust_brd','maoritrustapproved','Marae_funds','Marae_reservation','Notices','onlandunderTeTureWhenuaMaoriAct','Organisational_type','percentage_spent_overseas','RegistrationStatus','Society_institution','Trustees_trust','Exemptions','AnnualReturnDueDate','annualreturnextensiondate','GroupType','GroupId','Telephone2','TelephoneDay','PostalAddress_city','PostalAddress_country','PostalAddress_line1','PostalAddress_line2','PostalAddress_postcode','PostalAddress_suburb','StreetAddress_city','StreetAddress_country','StreetAddress_line1','StreetAddress_line2','StreetAddress_postcode','StreetAddress_suburb','MainActivityId','MainBeneficiaryId','MainSectorId','OtherNames']

# Read input files and parse as xml
tree = ET.parse(regxml)
root = tree.getroot()

print(root, root.tag, root.attrib) # The root is an element called '{http://www.w3.org/2005/Atom}feed'

print('------------------')
print('                  ')
print('                  ')
print('------------------')

#for child in root:
#	print(child.tag) # Prints all direct children
#	print(len(child)) # 'entry' element has 18 children

#for elem in tree.iter():
#	print(elem.tag, elem.attrib) # Iterates over every element in the xml

#for elem in tree.iter(tag='{http://www.w3.org/2005/Atom}entry'):
#	print(elem.tag, elem.attrib, len(elem)) # Iterates over every 'entry' element and returns the tag, attirbutes and length


## Try and write directly from xml
'''
regcsv = datapath + ddate + '/' + 'nz_Organisations_' + ddate + '.csv'

with open(regcsv, 'w', newline='', encoding='utf-8') as f:
	charity = []
	for elem in root.findall('.//properties'):
		charid = elem.find('OrganisationId').text
		charity.append(charid)
	writer = csv.writer(f)
	writer.writerow(charity)	


'''
details = {} # Create a blank dictionary to store lists of org details

for name in regvarnames:
	details[name] = []
	for elem in tree.iter(tag='{http://schemas.microsoft.com/ado/2007/08/dataservices}%s' % str(name)):
		#print(elem.text)
		details[name].append(elem.text)
		#print(details)


print(len(details))
print(len(regvarnames))


#print(details.keys())
#print(details.items())
#print(type(details))
print(len(details))
print(len(regvarnames))


print(details.keys())
print(type(details))


print('------------------')
print('                  ')
print('                  ')
print('------------------')

for val in details.values():
	print(len(val))

# Save dictonary as json
with open(regjson, 'w') as f:
    json.dump(details, f)


# Write to csv - do it for each key and then merge the files togther (really rubbish way of doing things but I'm stuck)

for key, value in details.items():
	outcsv = datapath + ddate + '/' + 'nz_' + str(key) + '_' + ddate + '.csv'
	with open(outcsv, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow([key])
		for val in value:
			writer.writerow([val])

# Combine all of the csv files to form a single file

# Read data from Organisation id into an array

'''
with open(csvfile, 'r') as fin, open('new_'+csvfile, 'w') as fout:
    reader = csv.reader(fin, newline='', lineterminator='\n')
    writer = csv.writer(fout, newline='', lineterminator='\n')
    if you_have_headers:
        writer.writerow(next(reader) + [new_heading])
    for row, val in zip(reader, data)
        writer.writerow(row + [data])
'''

'''
with open(regcsv, 'w', newline='', encoding='utf-8') as f:
	writer = csv.DictWriter(f, fieldnames=regvarnames)
	for name in regvarnames:
		incsv = datapath + ddate + '/' + 'nz_' + str(name) + '_' + ddate + '.csv'
		with open(incsv, 'r', newline='', encoding='utf-8') as f_in:
			reader = csv.DictReader(f_in)
			next(reader)
			for line in reader:
				writer.writerow(line)
'''

	


'''
with open(regcsv, 'w', newline='', encoding='utf-8') as f:
	for key, value in details.items():
		writer = csv.writer(f)
		writer.writerow([key])
		for val in value:
			writer.writerow([val])
'''		
## The above writes everything to one column.		