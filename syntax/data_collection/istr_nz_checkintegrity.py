# NZ Charity data - Check Integrity
# Alasdair Rutherford
# Created: 5 April 2018
# Last edited: 5 April 2018

# Data guide: https://www.charities.govt.nz/charities-in-new-zealand/the-charities-register/open-data/

# Free text fields in the CSVs have sometimes not been coded properly with string quotes, leading
# to the commas in a freetext field being interpreted as new columns.  This puts some records out
# of sync.

# This script checks all the downloaded files, and records rows where this has occured.
# It does this by comparing the number of columns in a row to the number of columns
# in the first row (the variable names).

import csv
import os
from downloaddate_function import downloaddate


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

# Run the downloaddate function to get the date
ddate = downloaddate()

# Path to save the downloaded data
datapath = 'C:/Users/mcdonndz-local/Dropbox/paper-istr-2018/data_raw/' # Dropbox folder for project

print('_____________________________________________')

########################################################################################################

										# Download data #

########################################################################################################

search = [activities, area, beneficiaries, group, sectors, funds, register, vorgs, officers] #[register] #
search_big = [voff, grpannreturns] #[] #

# Specify this option if you want teh script to generate new datafiles with probelmmatic records removed
cleanup = False


"""
# Open logfile
logfilepath = datapath + 'log_' + ddate + '.csv'
logfile = open(logfilepath, 'w', newline='')
logcsv = csv.writer(logfile)
logcsv.writerow(['timestamp', 'filename', 'url', 'downloaded', 'failedattempts'])
"""

# Check integrity of all listed datasets
for data in search + search_big:

	print('CSV - Whole files 	|	Record type:', data)

	directory = datapath + '/' + data


	with open(os.path.join(directory, 'nz_' + data + '_integrityerrors.txt'), 'w', newline='', encoding='utf-8') as outCSVfile:
		writer = csv.writer(outCSVfile)
		firstpass = 1
		# This for loop goes through all the files in each directory
		for filename in os.listdir(directory):

			if filename.endswith(".csv") and not(filename.endswith("integrity.csv")): 

				with open(os.path.join(directory, filename), 'r', newline='', encoding='utf-8') as inCSVfile:
					print(os.path.join(directory, filename))
					rowcounter = 0
					reader = csv.reader(inCSVfile)
					fieldnames = next(reader)
					checklength = len(fieldnames)
					rowcounter +=1

					# Generate a clean file if option specified
					if cleanup: 
						with open(os.path.join(directory, filename + '_integrity.csv'), 'w', newline='', encoding='utf-8') as integCSVfile:
							writerinteg = csv.writer(integCSVfile)
							writerinteg.writerow(fieldnames)
							for row in reader:
								if len(row) == checklength:
									writerinteg.writerow(row)
									pass #print('.', end='')
								else:
									if firstpass==1:
										writer.writerow(fieldnames)
										firstpass = 0
									writer.writerow(row)	
									print('*', rowcounter, row[2], '| ', end='')							
								rowcounter +=1
					else:
						for row in reader:
								if len(row) == checklength:
									pass #print('.', end='')
								else:
									print('*', rowcounter, row[2], '| ', end='')							
								rowcounter +=1
			else:
				pass
			print(' ')
	print('-------------------------------------')

print('All done')