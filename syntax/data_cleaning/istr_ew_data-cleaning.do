// File: ew_datamanagement_20180419.do
// Creator: Diarmuid McDonnell
// Created: 19/04/2018

******* England & Wales Register of Charities data cleaning *******

/* This DO file performs the following tasks:
	- imports raw data in csv format
	- cleans these datasets
	- links these datasets together to form a comprehensive Register of Charities and a financial panel dataset
	- saves these datasets in Stata and CSV formats
   
	The files associated with this project can be accessed via the Github repository: https://github.com/DiarmuidM/regno
*/


/* Define paths */

include "C:\Users\mcdonndz-local\Desktop\github\ew_charity_data\stata\do_files\ew_paths_20180419.doi"
di "$path1"
di "$path2"
di "$path3"
di "$path4"
di "$path5"
di "$path6"
di "$path7"
di "$path8"


/* 1. Open the raw data in csv format */

/* Base dataset - extract_charity */

import delimited using $path3\extract_charity.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact
**codebook *, problems

/*
		- remove problematic variables/cases e.g. duplicate records, missing values etc
		- sort data by unique identifier
		- explore invalid values for each variable
		- label variables/values/dataset
*/


	/* Missing or duplicate values */
	
	capture ssc install mdesc
	mdesc
	missings dropvars, force
	
	duplicates report // Lots of duplicates
	duplicates list // Look to be data entry errors: every variable is blank except regno, which is a string (e.g. "AS AMENDED ON 27/11/2011&#x0D;").
	duplicates drop
	
	duplicates report regno
	duplicates list regno // Looks like a combination of data entry errors (strings again) and duplicate numbers. Delete strings first.
	
		list regno if missing(real(regno))
		replace regno = "" if missing(real(regno)) // Set nonnumeric instances of regno as missing
		destring regno, replace
		drop if regno==. // Drop instances where regno is missing.
		
		duplicates report regno
		duplicates list regno in 1/2000
		duplicates tag regno, gen(dupregno)
		
			duplicates report regno subno
			duplicates list regno subno
		
			list regno subno if regno==200027
			list regno subno if regno==201415
			list regno subno if dupregno!=0
			codebook subno
			codebook subno if dupregno!=0
			/*
				Ok, it looks as if the remaining instances of duplicate regno is accounted for by each subsidiary of a charity having its parent
				charity's regno.
				
				Create a variable that counts the number of subsidiaries per charity, and drop observations where subno > 0.
			*/
			
			destring subno, replace
			bysort regno: egen subsidiaries = max(subno)
			list regno subno subsidiaries in 1/1000
			
			keep if subno==0
			drop dupregno
			/*
				Think about keeping subsidiaries later on, as we can track their registration and removal dates.
			*/
		
		duplicates report regno name
		/*
			I think some of the issues with regno stem from how the csv file is built using NCVO scripts; it might be worth raising this with them.
		*/
	
	
	/* Remove unnecessary variables */
	
	drop add1 add2 add3 add4 add5 phone fax
	codebook corr // Looks like the name of the principal contact; drop.
	drop corr
	
		
	/* 	Sort data */
	
	sort regno
	list regno in 1/1000
	notes: use regno for linking with other datasets containing charity numbers

	
	/* Invalid values for each variable */
		
	codebook name
	list name in 1/1000 // There are some dummy charities (e.g. TestCharity, DELETED) that need to be removed.
	preserve
		gsort name
		list name in 1/1000
	restore
	/*
		There are some minor issues with name (invalid values e.g. TestCharity, DELETED).
		I'll just assume that all of the values for regno are valid and ignore this variable.
	*/
	
	
	codebook subno // Is a constant i.e. no subsidiary orgs in the dataset; drop
	drop subno
	
	
	codebook orgtype
	tab orgtype // RM=removed, R=registered i.e. active
	encode orgtype, gen(charitystatus)
	tab charitystatus
	recode charitystatus 1=1 2=2 3/max=. // Recode anything above 2 (the highest valid value) as missing data.
	label define charitystatus_label 1 "Active" 2 "Removed"
	label values charitystatus charitystatus_label
	tab charitystatus
	drop orgtype
	
	
	codebook aob aob_defined // Both are free-text fields that we can do nothing with at this moment; drop.
	drop aob aob_defined 
	
	
	codebook gd // Statement from governing document; keep.

	
	codebook nhs
	tab nhs // Should have two values: T=true, F=false. Only has false, missing and incorrect string values.
	drop nhs

	
	codebook ha_no
	drop ha_no // Should be a charity's Housing Association number; only contains the value "F", the rest is missing; drop.
	
	
sav $path1\ew_charityregister_apr2018_v1.dta, replace	
	
	
/* Charitable purposes classification dataset */

import delimited using $path3\extract_class.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact
	
	duplicates report
	duplicates list
	
	duplicates report regno // Huge number of duplicate charity numbers, which is probably accounted for by a charity having more than one purpose.
	*duplicates list regno

		
	codebook regno
	list regno in 1/1000
	notes: use regno for linking with other datasets containing charity numbers

	
	codebook class
	tab class
	rename class classno // To match the class reference dataset
	
	sort classno
	
sav $path1\ew_class_apr2018_v1.dta, replace


/* Charitable purposes classification reference dataset */

import delimited using $path3\extract_class_ref.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact
	
	duplicates report
	duplicates list
	
	codebook classno
	sort classno
	
	codebook classtext
	tab classtext
	
sav $path1\ew_class_ref_apr2018.dta, replace

	
/* extract_main_charity dataset */

import delimited using $path3\extract_main_charity.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact
**codebook *, problems

/*
		- remove problematic variables/cases e.g. duplicate records, missing values etc
		- sort data by unique identifier
		- explore invalid values for each variable
		- label variables/values/dataset
*/


	/* Missing or duplicate values */
	
	capture ssc install mdesc
	mdesc
	missings dropvars, force
	
	duplicates report
	duplicates list
	duplicates drop
	
	duplicates report regno
	duplicates list regno
	
	
	/* Remove unnecessary variables */
	
	drop email web
	
		
	/* 	Sort data */
	
	sort regno
	list regno in 1/1000
	notes: use regno for linking with other datasets containing charity numbers

	
	/* Invalid values for each variable */
		
	codebook coyno // Companies House number
	list coyno if ~missing(real(coyno)) in 1/1000
	list coyno if regex(coyno, "OC")
	replace coyno = "" if missing(real(coyno)) // Set nonnumeric instances (including blanks) of coyno as missing
	
		capture drop length_coyno
		gen length_coyno = strlen(coyno)
		tab length_coyno // 0=missing and lots of varying lengths.
		drop length_coyno
		
	destring coyno, replace
	
	duplicates report regno coyno
	
	gen company = 1 if coyno!=. 
	recode company 1=1 .=0
	tab company
	/*
		It's difficult to trust this field as we do not know if the company numbers themselves are valid e.g. they are of varying length.
	*/

	
	codebook trustees
	tab trustees
	encode trustees, gen(trustee_incorp)
	tab trustee_incorp
	recode trustee_incorp 1=1 2=2 3/max=. // Recode anything above 2 (the highest valid value) as missing data.
	label define trustee_incorp_label 1 "False" 2 "True"
	label values trustee_incorp trustee_incorp_label
	tab trustee_incorp
	drop trustees
	
	
	codebook welsh // Captures whether the Commission communicates with the charity via Welsh language; drop.
	drop welsh
	
	
	codebook fyend // Financial year end - DD/MM. Keep for now but it is probably not needed.
	
	
	codebook incomedate // Date latest income figure refers to- currently a string.
	rename incomedate str_incomedate
	replace str_incomedate = substr(str_incomedate, 1, 10) // Capture first 10 characters of string.
	replace str_incomedate = subinstr(str_incomedate, "-", "", .)
	tab str_incomedate, sort
	
	gen incomedate = date(str_incomedate, "YMD")
	format incomedate %td
	codebook incomedate
	
	gen incomeyr = year(incomedate) // Identify the year the latest gross income refers to
	tab incomeyr
	drop str_incomedate
	
	
	codebook grouptype // No explanation in the data dictionary as to what this represents; drop.
	drop grouptype
	
	
	codebook income
	inspect income
	sum income, detail
	
	sort regno
	
sav $path1\ew_mcdataset_apr2018_v1.dta, replace	
	
	
/* extract_registration dataset */	

import delimited using $path3\extract_registration.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact

	/* Missing or duplicate values */
	
	capture ssc install mdesc
	mdesc
	missings dropvars, force
	
	duplicates report
	duplicates list
	duplicates drop
	
	duplicates report regno
	duplicates list regno
	duplicates tag regno, gen(dupregno)
		
		list regno subno if regno==1175809
		list regno subno if regno==1176305
		list regno subno if dupregno!=0
		codebook subno
		codebook subno if dupregno!=0
		/*
			Ok, it looks as if the remaining instances of duplicate regno is accounted for by each subsidiary of a charity having its parent
			charity's regno.
			
			Create a variable that counts the number of subsidiaries per charity, and drop observations where subno > 0.
		*/
			
		bysort regno: egen subsidiaries = max(subno)
		list regno subno subsidiaries in 1/1000
			
		keep if subno==0
		drop dupregno
		/*
			Think about keeping subsidiaries later on, as we can track their registration and removal dates.
		*/
	
	notes: use regno for linking with other datasets containing charity numbers

	
	codebook regdate remdate // Variables are currently strings, need to extract info in YYYYMMDD format.
	*tab1 regdate remdate
	foreach var of varlist regdate remdate {
		rename `var' str_`var'
		replace str_`var' = substr(str_`var', 1, 10) // Capture first 10 characters of string.
		replace str_`var' = subinstr(str_`var', "-", "", .) // Remove hyphen from date information.
		
		gen `var' = date(str_`var', "YMD")
		format `var' %td
		codebook `var'
		
		gen `var'yr = year(`var')
		drop str_`var'
	}
	
	rename regdateyr regy
	rename remdateyr remy
	codebook regy remy
	tab1 regy remy, sort
	
	
	codebook remcode
	tab remcode // Need to merge with extract_remove_ref to understand the codes.
	
	sort remcode
	
sav $path1\ew_rem_apr2018_v1.dta, replace


/* extract_remove_ref dataset */	

import delimited using $path3\extract_remove_ref.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact

	duplicates report
	duplicates list
	
	list , clean

	rename code remcode
	
	sort remcode
	
sav $path1\ew_rem_ref_apr2018.dta, replace


/* extract_trustee dataset */

import delimited using $path3\extract_trustee.csv, varnames(1) clear
count
desc, f
notes
codebook *, compact

	/* Missing or duplicate values */
	
	capture ssc install mdesc
	mdesc
	missings dropvars, force
	tab v3
	drop v3
	
	duplicates report
	duplicates list
	duplicates drop
	
	
	codebook regno
	sort regno
	
	
	codebook trustee
	list trustee in 1/1000 // We don't need the names, just a count of trustees per charity.
	bysort regno: egen trustees = count(trustee)
	sum trustees
	
	drop trustee

sav $path1\ew_trustees_apr1018.dta, replace



	
	
/* Merge supplementary datasets with Charity Register */	
	
	// Merge class datasets
	
	use $path1\ew_class_apr2018_v1.dta, clear
	
	merge m:1 classno using $path1\ew_class_ref_apr2018.dta, keep(match master using)
	tab _merge
	drop _merge
	
	sort regno
	
	sav $path1\ew_class_apr2018.dta, replace
	
	
	// Merge rem datasets
	
	use $path1\ew_rem_apr2018_v1.dta, clear
	
	merge m:1 remcode using $path1\ew_rem_ref_apr2018.dta, keep(match master using)
	tab _merge
	drop _merge
	
	rename text removed_reason
	codebook removed_reason
	tab removed_reason
	rename removed_reason oldvar
	
	encode oldvar, gen(removed_reason)
	tab removed_reason
	tab removed_reason, nolab
	drop oldvar
	notes: Only use two categories of removed_reason to measure demise/closure: CEASED TO EXIST (3) and DOES NOT OPERATE (4).
	
	sort regno
	
	sav $path1\ew_rem_apr2018.dta, replace
	
	
	
	
	
	
	
	
	
	

	
	
	codebook coyno // Companies House number
	list coyno if coyno!=""
	
		capture drop length_coyno
		gen length_coyno = strlen(coyno)
		tab length_coyno // 0=missing and lots of varying lengths.
		
	destring coyno, replace // Non-numeric characters (e.g. "RC"). Leave as string for now.	

	
	/* Merge Bethnal Green information to create area variable */
	
	merge 1:1 regno using $path1\bethnalgreen_20180306.dta, keep(match master using)
	tab _merge
	list if _merge==2 // 1 observation with all missing values; drop
	drop if _merge==2
	rename _merge bethmerge
	
	notes: The code for Birmingham charities is E08000025 - geog_la variable.
	notes: The code for Burnley charities is E07000117 - geog_la variable.
	notes: The code for Bolton charities is E08000001 - geog_la variable.
	notes: The code for Bethnal Green charities is E09000030 - geog_la variable.
	codebook geog*, compact
	codebook geog*
	count if geog_la=="E08000025"
	count if geog_la=="E07000117"
	count if geog_la=="E08000001"
	count if geog_la=="E09000030"
	
		capture drop area
		gen area = 1 if geog_la=="E08000025"
		replace area = 2 if beth==1
		replace area = 3 if geog_la=="E08000001"
		replace area = 4 if geog_la=="E07000117"
		replace area = 5 if geog_la!="E08000025" & geog_la!="E07000117" & geog_la!="E08000001" & geog_la!="E09000030" & geog_la!=""
		label define area_label 1 "Birmingham" 2 "Bethnal Green" 3 "Bolton" 4 "Burnley" 5 "Rest of UK"
		label values area area_label
		tab area
		
		// Do a quick test to see if aob field contains 'bethnal green'
		
		list aob in 1/500 if aob!=""
		count if strpos(aob, "BETHNALGREEN")
		di r(N) " observations mentioning Bethnal Green
		tab beth if strpos(aob, "BETHNALGREEN")
			
		notes: 4,291 Birmingham charities.
		notes: 236 Burnley charities.
		notes: 790 Bolton charities.
		notes: 320 Bethnal Green charities.
	
	
	notes: geog_ccg geog_lep are not neccessary for analysis.
	notes: geog_oa is output area from census (~10,000 people in each area); also not neccessary for analysis.
	drop geog_ccg geog_lep geog_oa
	
			
			/* Create a dataset of postcodes and emails for our four areas */
			
			preserve
				codebook email postcode
				keep if area < 5
				keep regno name area postcode email web phone regy remy
				export excel using $path2\leverhulme_postcodeandemail_4b.xlsx, firstrow(var) replace
			restore	

	
	
	codebook latest_fye latest_activity
	tab latest_fye, sort miss // Need to extract the year.
	tab latest_activity, sort miss
	
		capture drop latest_repyr
		gen latest_repyr = substr(latest_fye, 7, .)
		tab latest_repyr
		destring latest_repyr, replace
	
		// Are latest_repyr and latest_activity different? If so, in what way?
		
		list latest_repyr latest_activity in 1/1000 // They look to be different for certain charities.
		capture drop diff_repyractivity
		gen diff_repyractivity = latest_activity - latest_repyr
		sum diff_repyractivity, detail
		histogram diff_repyractivity, norm freq
		/*
			Range of differences: sometimes latest_activity is later than fye, sometimes earlier.
			
			I'm going to go with latest_fye as the indicator of most recent year of charitable activity, at least
			until I see how latest_activity is constructed.
		*/
		
		
	
	codebook removed_reason
	tab removed_reason // Need the codebook!
	tab removed_reason charitystatus, miss
	notes: 24,630 removed charities without a reason for removal
	rename removed_reason oldvar
	
	encode oldvar, gen(removed_reason)
	tab removed_reason
	tab removed_reason, nolab
	label define removed_reason_label 1 "AMALGAMATED" 2 "CEASED TO BE CHARITABLE" 3 "CEASED TO EXIST" 4 "REMOVED BY APPLICATION" 5 "DUPLICATE REGISTRATION" ///
		6 "EXCEPTED CHARITY" 7 "REMOVED IN ERROR" 8 "EXEMPT CHARITY" 9 "FUNDS TRANSFERRED (GI)" 10 "FUNDS TRANSFERRED (INCOR)" 11 "DOES NOT OPERATE" ///
		12 "POLICY REMOVAL" 13 "REGISTERED IN ERROR" 14 "FUNDS TRANSFERRED (S.74)" 15 "FUNDS SPENT UP (S.75)" 16 "UNITING DIRECTION (S96) M" ///
		17 "TRANSFER OF FUNDS" 18 "FUNDS SPENT (BY TRUSTEES)" 19 "TRANSFERRED TO EXEMPT CHY" 20 "VOLUNTARY REMOVAL"
	label values removed_reason removed_reason_label
	tab removed_reason
	drop oldvar
	notes: Only use two categories of removed_reason to measure demise/closure: CEASED TO EXIST (3) and DOES NOT OPERATE (11).

	
	
	codebook latest_income latest_expend latest_assets latest_employees trustees
	inspect latest_income latest_expend latest_assets latest_employees trustees
	sum latest_income latest_expend latest_assets latest_employees trustees, detail // Lots of zeroes; I take it I can treat these as valid values.
	notes: 366 charities with negative values for latest_assets.
	
		count if latest_income==0 // 29,952
		count if latest_expend==0 // 40,168
		count if latest_employees==0 // 1,448
		count if latest_assets==0 // 121
		count if trustees==0 // 190,8888

		// Create alternative functional forms of these variables
		/*
		ladder latest_income 
		ladder latest_employees
		ladder latest_expend 
		ladder latest_assets
		ladder trustees
		*/
		/*
			Not producing any statistics for these variables? The issue appears to be with -sktest-.
			It can break down for large sample sizes and/or large deviations from Gaussianity.
			
			Oh well, the variables should be transformed to log functional form and we take it from there.
		*/
		
		foreach var in latest_income latest_expend latest_employees latest_assets trustees {
			gen ln_`var' = ln(`var' + 1) // Should it be .5?
			histogram ln_`var', normal freq
		}
		sum ln_latest_income ln_latest_expend ln_latest_employees ln_latest_assets ln_trustees, detail
		/*
			Need to do something with these zeroes: exclude them from analyses? I suppose they are fine for now.
		*/
		
		
	**twoway (scatter latest_income latest_expend, jitter(20) mcolor(%50)) (lfit latest_income latest_expend)

		
	codebook latest_strata latest_strata_code
	/*
		latest_strata is a categorical variable of org size. latest_strata_code is ambiguous but doesn't need transforming.
	*/	
	
	tab1 latest_strata
	encode latest_strata, gen(charitysize)
	tab charitysize
	tab charitysize, nolab
		recode charitysize 7=1 9=2 2=3 5=4 1=5 6=6 4=7 3=8 8=9
		tab charitysize
	label define charitysize_label 1 "No income" 2 "Under 10k" 3 "10k - 25k" 4 "25k - 100k" 5 "100k - 500k" 6 "500k - 1m" ///
		7 "1m - 10m" 8 "10m - 100m" 9 "Over 100m"
	label values charitysize charitysize_label
	tab charitysize
	drop latest_strata
	
	
	codebook almanac_strata
	encode almanac_strata, gen(charitysize_almanac)
	tab charitysize_almanac
	tab charitysize_almanac, nolab
		recode charitysize_almanac 7=1 9=2 2=3 5=4 1=5 6=6 4=7 3=8 8=9
		tab charitysize_almanac
	label define charitysize_almanac_label 1 "No income" 2 "Under 10k" 3 "10k - 25k" 4 "25k - 100k" 5 "100k - 500k" 6 "500k - 1m" ///
		7 "1m - 10m" 8 "10m - 100m" 9 "Over 100m"
	label values charitysize_almanac charitysize_almanac_label
	tab charitysize_almanac
	drop almanac_strata
	
		tab charitysize charitysize_almanac
		list latest_fye almanac_fye in 1/500
		/*
			Plenty of differences between the two, most likely due to different comparison years.
		*/
		

	
	codebook objects
	
	
	codebook icnpo* // Use this to track changes in types of charities over time.
	tab1 icnpo_code icnpo_category
	tab1 icnpo_ncvo_code icnpo_ncvo_category
	/*
		I'll use the NCVO version of ICNPO categorisation.
	*/
		
		
	codebook date_registered date_removed		
	codebook regy remy // Year values extracted from date_registered date_removed respectively.
	// check scottish registration years
	
		list regno if missing(regy)
		count if missing(regy) // Who are these charities? I think they might be Scottish charities.
		tab scot if missing(regy)
		/*
			21,528 of 21,665 missing values for regy are accounted for by Scottish charities.
			
			I need to link to Scottish Charity Register.
		*/
	
	
		// Create variable capturing period in which charities were registered:
		
		tab1 regy remy
		/*
			There appear to be some problematic values for regy e.g. 9 14. Need to get rid of these before I destring and recode.
			
			I need to calculate string length, set observations with strlen==3 to missing, and then destring.
		*/
		
			capture drop length_regy
			gen length_regy = strlen(regy)
			tab length_regy // 0=missing
			/*
				158 observations with invalid values for period i.e. 3-character string.
				
				This is due to the timestamp on some of the values for date_registered; see if I can extract it properly.
			*/

			
				list date_registered regy if length_regy==3 // No way to extract the year from these values e.g. 0000-00-0314:00:00.
				
			notes: 158 observations with invalid values for registered year i.e. 3-character string, due to missing components of "date" variables.
			
			replace regy = "" if length_regy==3
			tab regy, sort miss
			
		destring regy, replace
		destring remy, replace
		
		capture drop period
		gen period = regy
		tab period, sort miss
		count if period < 1945
		recode period min/1944=1 1945/1965=2 1966/1978=3 1979/1992=4 1993/max=5 *=.
		label define period_label 1 "Pre-1945" 2 "1945-1965" 3 "1966-1978" 4 "1979-1992" 5 "Post-1993"
		label values period period_label
		tab period, miss
		count if regy==.
		
		tab charitysize period, all row nofreq
		
		// Period when a charity was removed
		
		capture drop remperiod
		gen remperiod = remy
		tab remperiod, sort miss
		count if remperiod < 1945
		recode remperiod min/1944=1 1945/1965=2 1966/1978=3 1979/1992=4 1993/max=5 *=.
		label values remperiod period_label
		tab remperiod, miss
		count if remy==.
		
		// Create a charity age variable: charity age = latest_repyr - regy
		
		capture drop charityage
		gen charityage = latest_repyr - regy if ~missing(latest_repyr) & ~missing(regy)
		sum charityage, detail // Some extreme values; explore in more detail.
		histogram charityage, norm freq
		notes: charityage is derived from latest_repyr - regy
		
			count if charityage < 1 // 1,514 charities younger than 1.
			count if charityage <= 0 // Same as above. Who are all these -1 charities?
			list regno charitystatus latest_repyr regy if charityage <= 0
			/*
				Look to be a whole variety of charities here:
					- ~half are removed and relate to older years (1995/96)
					- some are Scottish charities from 2015/16
			*/
		
			capture drop ln_charityage
			gen ln_charityage = ln(charityage + 1) if charityage >= 0
			histogram ln_charityage, norm freq
			/*
				What do I do about charityage==0 (ln_charityage <=1)? Just exclude them from analyses I suppose.
			*/
	
	
	/* Produce some line graphs of registrations and removals over time */
	/*
	preserve
		capture drop freq
		gen freq = 1
		collapse (count) freq, by(regy)
		line freq regy
	restore
	
	preserve
		capture drop freq
		gen freq = 1
		collapse (count) freq, by(remy)
		line freq remy, ylabel(10 100 1000 10000) yscale(r(0 10000))
	restore
	*/
		
		
	/* 3. Label and order variables */
	/*
		The dataset is not currently documented in full. Do my best to label the variables and speak to John about the remainder.
	*/
	
	label variable regno "Charity number of organisation"
	label variable aob_classified "Geographical scale of activity i.e. local, national"
	label variable coyno "Companies House number"
	label variable geog_la "Area charity is based"
	label variable removed_reason "Reason for removal from Charity Register"
	label variable regy "Year charity was founded"
	label variable remy "Year charity was removed from Charity Register"
	label variable scot "Charity registered with OSCR in Scotland"
	label variable charity_wales "Charity is based in Wales"
	label variable charitystatus "Whether charity is active or removed from Charity Register"
	label variable uniqueid "Unique id of record"
	label variable latest_repyr "Most recent reporting year - derived from latest_fye"
	label variable charitysize "Categorical measure of charity income - derived from latest_income"
	label variable period "Era charity was founded in - derived from key policy and political changes"
	label variable charityage "Length of time - in years - since charity was founded"
	label variable ln_charityage "Length of time - in years - since charity was founded (log)"

	
	sav $path1\ncvo_charitydata_20171115_v2.dta, replace
