# Script to sort the large NZ Charities files into smaller files by year
# Alasdair Rutherford, Diarmuid McDonnell
# Created: 29 March 2018
# Last edited: 5 April 2018

# Data guide: https://www.charities.govt.nz/charities-in-new-zealand/the-charities-register/open-data/

import csv
import re
import requests
import os
import os.path
import errno
from time import sleep
from downloaddate_function import downloaddate



# Split the downloaded annual return files into calendar years
def splitfilesbyyear(filename, data, ddate,  column, length, width, splityear=0, splitmonth=0, splitday=0, splitemp=0, spliteymonth=0):

	inputfilepath = datapath + ddate + '/' + data + '/' + 'nz_' + data + '_y' + str(splityear) + '_m' + str(spliteymonth) +  '_p' + str(splitemp) + '_' + ddate + '.csv'

	with open(inputfilepath, 'rb') as file:
		filedata = file.read()

		# Replace the target string
	pattern = re.compile(b'[^\x00-\x7F]')
	filedata = re.sub(pattern, b'_', filedata) #filedata.replace('[^\x00-\x7F]', '_')

		# Write the file out again
	with open(datapath + ddate + '/' + 'nz_temp.csv', 'wb') as file:
		file.write(filedata)

	outputfiles = {}

	for year in range(2000,2020):
		outputfiles[str(year)] = open(filename + str(year) + '.csv', 'a', newline='')
		outputfiles[str(year) + 'a'] = csv.writer(outputfiles[str(year)])

	outputfiles['error'] = open(filename + 'error' + '.csv', 'a', newline='')
	outputfiles['errora'] = csv.writer(outputfiles['error'])

	with open(datapath + ddate + '/' + 'nz_temp.csv', 'r', newline='') as inCSVfile:
		reader = csv.reader(inCSVfile)
		print('-')
		print(inputfilepath)

		startrow = 1
		rowcounter=0
		while rowcounter<startrow:
			next(reader)
			rowcounter+=1

		for row in reader:
			if len(row)==width:   # 145 for ann returns:
				try:
					yearend = row[column][len(row[column])-length:]	# Take the year out of the YearEnded column
					year = int(yearend)
					#yearend = yearend[2 - len(yearend):]
					if year>=0 and year <=20: 
						yearend = '20' + yearend
					elif year >20 and year<=99:
						yearend = 2000
				except:
					yearend=0
				#print(inputfilepath, rowcounter)
				#print('		', row[column], '  |  -', yearend, '-')
			else:
				yearend=0

			# Rceode the missing values for Stata
			stata = True
			if stata == True:
				row = [x if x != 'Null' else '.' for x in row]

			if int(yearend) in range(2000, 2020): # ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']:
				outputfiles[str(yearend) + 'a'].writerow(row)
				print('.', end='')
			else:
				outputfiles['errora'].writerow(row)
				print('*', end='')
			rowcounter+=1

	for year in range(2008,2018):
		outputfiles[str(year)].close()

	outputfiles['error'].close()



# Creates the header rows for the files by year
def createannreturnfiles(filename, source):

	with open(source, 'r', newline='') as inCSVfile:
		reader = csv.reader(inCSVfile)
		row = reader.__next__()

	for year in range(2000,2020):
		outputfile = open(filename + str(year) + '.csv', 'w', newline='')
		outputfilew= csv.writer(outputfile)
		outputfilew.writerow(row)
		outputfile.close()

	outputfile = open(filename + 'error' + '.csv', 'w', newline='')
	outputfilew= csv.writer(outputfile)
	outputfilew.writerow(row)
	outputfile.close()

	return len(row)



# Run the downloaddate function to get the date 'benefacts_master.py' was executed.
ddate = '20180330'  #downloaddate()
datapath = './rawdata/' # 'C:/Users/ar34/Dropbox/Academic/Academic-Research-Projects/gitreps/scrapeNZ/rawdata/'


# Variables to store OData endpoint and database tables #

# Add $returnall=true to every url
baseurl = 'http://www.odata.charities.govt.nz/'
register = 'Organisations' # This is returned as xml due to the number of records - $returnall=true
grpannreturns = 'GrpOrgAllReturns'
 #'GrpOrgAllReturns?$returnall=true' # This is returned as xml due to the number of records - $returnall=true
activities = 'Activities'
area = 'AreaOfOperations'
beneficiaries = 'Beneficiaries'
group = 'Groups'
officers = 'Officers'
sectors = 'Sectors'
funds = 'SourceOfFunds'
vorgs = 'vOrganisations'
voff = 'vOfficerOrganisations'

# Create a folder for the download to be saved in #
try:
	os.mkdir(datapath+ddate)
except:
	print('Folder already exists')

########################################################################################################

										# Download data #

########################################################################################################

search = []
search_big = [voff, grpannreturns] # []


for data in search_big:

	filename = datapath + ddate + '/' + data +'/' + data + '_yr'

	# nz_vOfficerOrganisations_y2017_m0_p0_20180330.csv

	filewidth = createannreturnfiles(filename, datapath + ddate + '/' + data + '/' + 'nz_' + data + '_y2017' + '_m0' +  '_p0' + '_' + ddate + '.csv')

	print('Organise', data, 'by year')

	for year in [2008]:
		if data == grpannreturns:
			print('')
			print('grpannreturns', year)
			for month in range(1,13,1):
				splitfilesbyyear(filename, data, ddate, 103, 4, filewidth, splityear=year, spliteymonth=month, splitemp=1)
				splitfilesbyyear(filename, data, ddate, 103, 4, filewidth, splityear=year, spliteymonth=month, splitemp=2)
		elif data == voff:
			print('')
			print('voff')
			for month in range(1,13,1):
				splitfilesbyyear(filename, data, ddate, 14, 2, filewidth, splityear=year, spliteymonth=month)		# Get csv
				#logcsv.writerow([datetime.today().strftime('%Y%m%d %H:%M'), filename, searchurl, success, fails])				# record in logfile

	for year in [2007, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]:
		if data == grpannreturns:
			print('')
			print('grpannreturns', year)
			splitfilesbyyear(filename, data, ddate, 103, 4, filewidth, splityear=year)	
		elif data == voff:
			print('')
			print('voff', year)
			splitfilesbyyear(filename, data, ddate, 14, 2, filewidth, splityear=year)		# Get csv


	print('')
	print('Done sorting ' + data)
	print('------------------------------------------------------------------------------')

print('*** All done!')
