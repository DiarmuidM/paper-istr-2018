import csv

projectPath = "./rawdata/20180330/"

arealookup = projectPath + "AreaOfOperations/nz_AreaOfOperations_coded.csv"

with open(arealookup, 'r', newline='') as arealookup_file:

	reader_area = csv.reader(arealookup_file)

	areadict={}

	for row in reader_area:
		areadict[row[1]] = row[3]
		print(row[1], row[2])

print(areadict)

for year in range(2007, 2018):

	print(year)

	infilename = projectPath + "GrpOrgAllReturns/GrpOrgAllReturns_yr" + str(year) + ".csv_integrity.csv"

	with open(infilename, 'r', newline='') as returnforcoding_file:

		reader = csv.reader(returnforcoding_file)

		outfilename = projectPath + "GrpOrgAllReturns/GrpOrgAllReturns_yr" + str(year) + ".csv_integrity_geog.csv"

		with open(outfilename, 'w', newline='') as outputcoded_file:

			writer = csv.writer(outputcoded_file)
			writer.writerow(reader.__next__() + ['geog1', 'geog2', 'geog3', 'geog4', 'geog5', 'geog6', 'geog7', 'geog8', 'geog9', 'geog10'])

			for row in reader:
				areas = row[52].split(",")
				geoglist = []
				for place in areas:
					geog = place.strip()
					if geog == 'Korea':
						geog = geog + ',' + areas[areas.index(place)+1]
					if geog == 'Congo':
						geog = geog + ', ' + 'Democratic Republic of'				
					if geog == 'South' or geog == 'North' or geog=='Democratic Republic of' or geog=='.':
						pass
					else:
						#print(geog, end='')
						#print('					', areadict[geog])
						geoglist.append(areadict[geog])
				writer.writerow(row + geoglist)
				#print('.', end='')


					

