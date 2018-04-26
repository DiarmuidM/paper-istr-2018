# NZ code deregistartion reasons
# Alasdair Rutherford
# Created: 3 April 2018
# Edited: 3 April 2018

# This code takes a list of free text deregistration reasons and returns tuple
# of [Act Section, Reason Category] for each reason. 


import re
import csv


def reasoncoding(reason):

	pattern32 = re.compile('(32)(\s)?(\(.\)(\s)?\((.)\))') # Match act references
	pattern40 = re.compile('(40)(\s)?(\(.\)(\s)?\((.)\))') # Match act references

	reasondict={}
	reasondict['windup'] = 0
	reasondict['parent'] = 0
	reasondict['failedfile'] = 0
	reasondict['merger'] = 0
	reasondict['duplicate'] = 0
	reasondict['request'] = 0	
	reasondict['section'] = 0	
	reasondict['act32']=''
	reasondict['act40']=''

	# Look for mentions of Section 32
	match32 = re.search(pattern32, reason)
	if match32:
		reasondict['act32'] = match32.group().replace(' ', '')

	# Look for mentions of Section 40
	match40 = re.search(pattern40, reason)
	if match40:
		reasondict['act40'] = match40.group().replace(' ', '')

	# Look for mergers
	for term in ['merg', 'Merg' 'Amalgamated', 'amalgamated']:
		reasondict['merger'] += reason.find(term)>=0

	# Look for duplicate records
	for term in ['duplicat', 'Duplicat']:
		reasondict['duplicate'] += reason.find(term)>=0

	# Look for voluntary removal requests
	for term in ['request', 'Request', 'no longer wish', 'voluntary', 'Voluntary']:
		reasondict['request'] += reason.find(term)>=0			

	# Look for winding up / cease to operate / dissolution
	for term in ['liquid', 'wound up', 'wind up', 'winding up', 'wound-up', 'no longer operat', 'no longer active', 'cease', 'closed', 'never operate', 'dissolved', 'no longer functioning']:
		reasondict['windup'] += reason.find(term)>=0

	# Look for parent / umbrella transfers
	for term in ['parent', 'umbrella']:
		reasondict['parent'] += reason.find(term)>=0

	# Look for less structured mentions of the Act
	for term in ['section', 'Section']:
		reasondict['section'] += reason.find(term)>=0			

	# Look for failures to file or comply
	for term in ['failed to file', 'Failed to file', 'failure to file', 'failure  to file', 'meet its obligations', ]:
		reasondict['failedfile'] += reason.find(term)>=0

	# List all reasons that are uncoded
	if reasondict['windup']==0 and reasondict['parent']==0 and reasondict['merger']==False and reasondict['failedfile']==0 and reasondict['request']==0 and reasondict['duplicate']==0 and reasondict['section']==0 and reasondict['act32']=='' and reasondict['act40']=='':
		print(reason)


	# Create flags for analysis file

	actsection = 'Unspecified'
	if reasondict['act32'] != '':
		actsection = reasondict['act32']
	elif reasondict['act40'] != '':
		actsection = reasondict['act40']			
	elif reasondict['section']>0:
		actsection = 'Section' 

	deregreason = 'No further detail'
	if reasondict['windup']>0:
		deregreason = 'Wound up'
	elif reasondict['failedfile']>0:
		deregreason = 'Failed to file'	
	elif reasondict['merger']>0:
		deregreason = 'Merger'
	elif reasondict['request']>0:
		deregreason = 'Removed by Request'
	elif reasondict['parent']>0:
		deregreason = 'Parent'
	elif reasondict['duplicate']>0:
		deregreason = 'Removed due to Duplicate'											

	return [actsection, deregreason]	


# Specify the source file for the deregistration reasons
inputfilepath = './rawdata/20180330/Organisations/' + 'nz_Organisations_y0_m0_p0_20180330.csv_integrity.csv'

# Output file to save the appended reasons
outputfilepath = './rawdata/20180330/Organisations/' + 'nz_orgs_deregreasons_integrity.csv' 

with open(inputfilepath, 'r', newline='', encoding='utf-8') as inCSVfile:

	reader = csv.reader(inCSVfile)

	with open(outputfilepath, 'w', newline='', encoding='utf-8') as outCSVfile:

		writer = csv.writer(outCSVfile)
		fieldnames = next(reader)
		writer.writerow(fieldnames + ['dereg_act', 'dereg_reason'])

		for row in reader:
			if row[12] !='null':	# Column 12 is dregistration reason field
				# Reason is coded as a tuple of Act and text reason
				codetuple = reasoncoding(row[12])
			else:
				codetuple = ['.', '.']
			#print(codetuple)	
			writer.writerow(row + codetuple)