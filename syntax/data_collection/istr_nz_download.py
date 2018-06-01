# Script to search NZ Charities Services OData API
# Diarmuid McDonnell, Alasdair Rutherford
# Created: 27 February 2018
# Last edited: 5 Apr 2018

# Data guide: https://www.charities.govt.nz/charities-in-new-zealand/the-charities-register/open-data/


import csv
import re
import requests
import shutil
import os
import os.path

from time import sleep
from datetime import datetime
from downloaddate_function import downloaddate

'''
# Run the downloaddate function to get the date
ddate = downloaddate()

# Path to save the downloaded data

datapath = 'C:/Users/mcdonndz-local/Dropbox/paper-istr-2018/data_raw/' # Dropbox folder for project


# Given the web address and a recordtype, this function downloads a CSV with specified splits
def downloadcsv(baseurl, data, ddate,  splityear=0, splitmonth=0, splitday=0, splitemp=0, spliteymonth=0):

	# Build the filters based on the search split
	recordfilter = ''
	if splityear>0:
		recordfilter = '&$filter=year(DateRegistered) eq ' + str(splityear)
	if splitmonth>0:
		recordfilter = recordfilter + ' and month(DateRegistered) ge ' + str(splitmonth) + ' and month(DateRegistered) lt ' + str(splitmonth + 1)
	if splitday>0:
		recordfilter = recordfilter + ' and day(DateRegistered) eq ' + str(splitday)
	if splitemp>0:
		recordfilter = recordfilter + ' and numberoffulltimeemployees mod 2 eq ' + str(splitemp - 1)
	if spliteymonth>0:
		recordfilter = recordfilter + ' and endofyearmonth eq ' + str(spliteymonth)
	
	# Write the r.content to a file in the newly created folder #
	outputfile = datapath + '/' + data + '/' + 'nz_' + data + '_y' + str(splityear) + '_m' + str(spliteymonth) +  '_p' + str(splitemp) + '_' + ddate + '.csv'
	print('		Saving CSV file to:', outputfile)

	# Build the query web address
	queryadd = baseurl + data + '?$returnall=true&$format=csv' + recordfilter
	print('		Request page:', queryadd, end='')
	sleep(1)

	# Make the request.  If it fails, try two further times.
	attempt = 1
	failures = 0
	while attempt<=3:
		try:
			# Stream the large csv straight to a downloaded file
			r = requests.get(queryadd, stream=True, allow_redirects=True)
			with open(outputfile, 'wb') as f:
				shutil.copyfileobj(r.raw, f)
			attempt=5
			print('		Success!')
		except:
			print('		Failed on attempt', attempt, '| ', end='')
			failures+=1
			attempt+=1
			sleep(60*2)
	success = attempt==5
                                                                              
	print('		---------------------------------------')

	return outputfile, queryadd, success, failures


########################################################################################################

										# Specify the parameters #

########################################################################################################


# Define url and data endpoints to search in

baseurl = 'http://www.odata.charities.govt.nz/'

register = 'Organisations' 
grpannreturns = 'GrpOrgAllReturns'
activities = 'Activities'
area = 'AreaOfOperations'
beneficiaries = 'Beneficiaries'
group = 'Groups'
officers = 'Officers'
sectors = 'Sectors'
funds = 'SourceOfFunds'
vorgs = 'vOrganisations'
voff = 'vOfficerOrganisations'


print('_____________________________________________')

########################################################################################################

										# Download data #

########################################################################################################

search = [activities, area, beneficiaries, group, sectors, funds, register, vorgs, officers] 
search_big = [voff, grpannreturns] 

# Open logfile
logfilepath = datapath + 'log_' + ddate + '.csv'
logfile = open(logfilepath, 'w', newline='')
logcsv = csv.writer(logfile)
logcsv.writerow(['timestamp', 'filename', 'url', 'downloaded', 'failedattempts'])


# Download all the small datasets
for data in search:

	print('CSV - Whole files 	|	Record type:', data)

	# Create a folder for the record type
	try:
		os.mkdir(datapath+'/'+data)
		print(data, 'folder created')
	except:
		print(data, 'folder already exists')

	filename, searchurl, success, fails = downloadcsv(baseurl, data, ddate)		# Download the csv
	logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])	# write to logfile

	print('Done searching for ' + data)
	print('_____________________________________________')
	print('')


# Download all the large datasets
for data in search_big:

	print('CSV - split in parts 	|	Record type:', data)

	# Create a folder for the record type
	try:
		os.mkdir(datapath+'/'+data)
		print(data, 'folder created')
	except:
		print(data, 'folder already exists')

	# Split years - 2008 includes most charities, so needs split up
	for year in [2008]:
		if data == grpannreturns:
			# print('grpannreturns')
			for month in range(1,13,1):
				filename, searchurl, success, fails = downloadcsv(baseurl, data, ddate, splityear=year, spliteymonth=month, splitemp=1)		# Get part one csv
				logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])							# record in logfile
				filename, searchurl, success, fails = downloadcsv(baseurl, data, ddate, splityear=year, spliteymonth=month, splitemp=2)		# Get part two csv
				logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])							# record in logfile
		elif data == voff:
			# print('voff')
			for month in range(1,13,1):
				filename, searchurl, success, fails = downloadcsv(baseurl, data, ddate, splityear=year, spliteymonth=month)		# Get csv
				logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])				# record in logfile

	# The remaining years only need split by year
	for year in [2007, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]:
		filename, searchurl, success, fails = downloadcsv(baseurl, data, ddate, splityear=year)				# Get csv
		logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])	# record in logfile

	print('')
	print('Done searching for ' + data)
	print('------------------------------------------------------------------------------')

# Close the logfile and finish
logfile.close()
print('*** All done!')


########################################################################################################

										# Perform diagnostics #

########################################################################################################

# Regroup downloaded files by year

import istr_nz_regroupfilesbyyear
print('istr_nz_regroupfilesbyyear.py')
print('                                             ')
print('---------------------------------------------')
print('                                             ')
sleep(10)

# Check integrity of downloaded files

import istr_nz_checkintegrity
print('istr_nz_checkintegrity.py')
print('                                             ')
print('---------------------------------------------')
print('                                             ')
sleep(10)
'''
# Code area of operations variable

import istr_nz_codeareas # ERROR in this script
print('istr_nz_codeareas.py')
print('                                             ')
print('---------------------------------------------')
print('                                             ')
sleep(10)

# Code deregistration variable

import istr_nz_codederegistration
print('istr_nz_codederegistration.py')
print('                                             ')
print('---------------------------------------------')
print('                                             ')
sleep(10)