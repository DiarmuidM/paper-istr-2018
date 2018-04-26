// File: istr_data-analysis.do
// Creator: Diarmuid McDonnell
// Created: 25/04/2018

******* Charity Removal - Cross-national comparisons *******

/* 
	
*/


******* Preliminaries *******

// These are all handled by profile.do

/*
clear
capture clear matrix
set mem 400m // not necessary in recent versions of Stata
set more off, perm
set scrollbufsize 2048000
exit
*/

/* Define paths */

/* Define paths */

include "C:\Users\mcdonndz-local\Desktop\github\paper-istr-2018\syntax\project_paths.doi"
di "$path1"
di "$path2"
di "$path3"
di "$path4"
di "$path5"
di "$path6"
di "$path7"
di "$path8"


/* Empty figures folder */
/*
	
	**shell rmdir $path1 /s /q
	
	pwd
	
	local workdir "C:\Users\mcdonndz-local\Desktop\github\a-tale-of-four-cities\figures\"
	cd `workdir'
	
	local datafiles: dir "`workdir'" files "*.gph"
	
	foreach datafile of local datafiles {
		rm `datafile'
	}
	
	local datafiles: dir "`workdir'" files "*.png"
	
	foreach datafile of local datafiles {
		rm `datafile'
	}

*/

/* 1. Open the clean datasets */

capture log close
**log using $path9\rqone_`tdate'.log, text replace

/* Australia */

use $path3\aus_annret_2014-16.dta, clear
capture datasignature report
count
desc, f
notes

	/* Create dependent variables */
	
	// Removed
	
	capture drop dremoved
	gen dremoved = charitystatus
	recode dremoved 1=0 2 3=1
	tab dremoved charitystatus
	label variable dremoved "Organisation no longer registered as a charity"
	
	// Multinomial measure of removed reason
	
	capture drop removed
	gen removed = .
	replace removed = 0 if charitystatus==1
	replace removed = 1 if charitystatus==2
	replace removed = 2 if charitystatus==3
	tab removed
	tab charitystatus removed
	tab removed charitystatus
	label define rem_label 0 "Active" 1 "Failed" 2 "Vol Removal"
	label values removed rem_label
	label variable removed "Indicates whether a charity has been de-registered and for what reason"
	
	
	/* Create independent variables */
	
	// Company legal form
	/*
		Not possible using Australia data.
	*/
	
	codebook sector charsize international, compact
	tab1 sector charsize international


		
**********************************************************************************************************************************
	
	
**********************************************************************************************************************************	
	
		
	/* 3. Regression analysis */
	
	/*
		Regression models for our two survival-related dependent variables: charityage (of removed charities) and removed multinomial variable.
		Independent variables: icnpo_ncvo_category period aob_classified charitysize company charityage (for removed).
	*/
	
	// Multinomial logistic regression of whether a charity is removed
					
	mdesc sector charsize international
	/*
		A quarter of the sample has missing data for charityage (24%).
	*/
		
	// Create a variable that identifies cases with no missing values for independent variables
			
	capture drop nomiss_model
	gen nomiss_model = 1
	replace nomiss_model = 0 if missing(sector) | missing(charsize) | missing(international)
	tab nomiss_model // 1,878 observations with no missing data for all of the independent variables.
	keep if nomiss_model==1
			
	// Create a variable that captures the baseline odds in a logit model - must be used in conjunction with noconstant option
			
	capture drop baseline
	gen baseline = 1
	/*
		I can see `baseline' only being useful if there are few explanatory variables with not many categories.
	*/
			
	
	/* Descriptive statistics */
	
	/* 2. Descriptive statistics */
	
	/* Sample description */
	/*
		Overall statistics for our independent variables.
	*/
		
	
	tab removed
	
	tab1 sector charsize international

	local fdate = "25apr2018"

	graph hbar if removed > 0, over(removed) over(sector) stack asyvar percent
	graph bar if removed > 0, over(removed) over(charsize) stack asyvar percent
	graph bar if removed > 0, over(removed) over(international) stack asyvar percent
	
	tab aryear removed
	local numobs:di %6.0fc r(N)
		
	graph bar if removed > 0, over(removed) over(aryear) stack asyvar percent ///
		bar(1, color(maroon )) bar(2, color(dknavy)) bar(3, color(erose)) ///
		ylabel(, nogrid labsize(small)) ///
		ytitle("% of charities", size(medsmall)) ///
		title("Charity Removal Reasons - Australia")  ///
		subtitle("by annual return year")  ///
		note("Source: Charity Commission Register of Charities (31/12/2016);  n=`numobs'. Produced: $S_DATE.", size(vsmall) span) ///
		scheme(s1color)

	graph export $path6\aus_removedreason_`fdate'.png, replace width(4096)
		
	
	/* Model building */

	// Decide on reference categories
	
	tab1 sector charitysize_ais2016 international
	/*
		The base category for sector is 6, charitysize_ais2016 is 3.
	*/
	
	// Model 1 - null model
		
	mlogit removed
	est store null
		
	// Model 2 - main effects
			
	regress removed sector charitysize_ais2016 international, robust
	est store linr
	fitstat
			
	tab removed
	
	mlogit removed ib6.sector ib3.charitysize_ais2016 i.international, vce(robust) nolog
	est store logr
	fitstat
	ereturn list

	
	*est save $path3\uk_removed_mlogit_20180419, replace
	*est use $path3\uk_removed_mlogit_20180419.ster

		/*
		// Save results in a matrix and then as variables
		/*
			There is an issue with the zero for the first variable in the model.
		*/
		*preserve
		
			matrix effect=e(b)
			*matrix variance=e(V)
			*matrix outcome=e(out)
			*scalar r2=e(r2_p)	
			
			clear 
			
			svmat effect, names(beta)
			*svmat variance, names(varian)
			*svmat outcome, names(out)
			
			list beta1
			l beta*
			
			drop beta1-beta34 // Drop first 35 variables as they are the values for the base outcome i.e. "Active".
			drop if missing(beta35-beta140) // Drop observations with missing data for the coefficient variables.
			l
			
			expand 3 // Create two extra rows for the other outcomes: vol removal and other removal.
			/*
				The first 35 variables correspond to the coeffients for the first outcome; the next 35 to the second outcome, and the final
				35 to the thrid outcome.
			*/
			
			forvalues i = 2(1)3 {
				forvalues num = 36(1)70 {
					local nextnum = `num' + 35*(`i'-1)
					replace beta`num' = beta`nextnum' if _n==`i'
				}
			}
			
			gen dataset = "UK"
			gen outcome = "Failed" if _n==1
			replace outcome = "Voluntary Removal" if _n==2
			replace outcome = "Other Removal" if _n==3
			tab outcome
			l			
			
			// rename variables and drop unnecessary ones
			
			drop beta71-beta140
			/*
			local varlist = "" 
			
			foreach var in beta36-beta70 {
				rename `var' 
			
			rename beta36 Cultureandrecreation
			*/
			
			// Graph results
			
			twoway (line 
			
		*/	
			
	
			
		
		/* See regression diagnostics from Leverhulme and Notif Events projects */
