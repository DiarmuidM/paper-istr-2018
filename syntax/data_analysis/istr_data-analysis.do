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


/* Canada */

use $path3\canada_register_20180522.dta, clear	
desc, f
count
notes
label data "Register of all Canadian charities - 20180522"

	
	// Descriptive statistics
	
	tab1 sector charitytype area
	tab depvar
	tab remy depvar if remy>=2007 // Produce a table
	
	local fdate = "01jun2018"

	graph bar , over(depvar) over(sector) stack asyvar percent ylabel(, nogrid labsize(small))
	graph bar , over(depvar) over(charitytype) stack asyvar percent ylabel(, nogrid labsize(small))
	graph bar , over(depvar) over(area) stack asyvar percent ylabel(, nogrid labsize(small))
	
	tab statyear depvar if statyear>=2007
	local numobs:di %6.0fc r(N)
	
	tab depvar if depvar>0 & statyear>=2007 // 62.5% is the average number of vol removals in a given year.
		
	graph bar if statyear>=2007 & depvar!=0, over(depvar) over(statyear) stack asyvar percent ///
		bar(1, color(maroon )) bar(2, color(dknavy)) bar(3, color(erose)) ///
		ylabel(, nogrid labsize(small)) ///
		ytitle("% of charities", size(medsmall)) ///
		yline(37, lpatt(dash) lcolor(gs8)) ///
		title("Charity Removal Reasons - Canada")  ///
		subtitle("by deregistration year")  ///
		note("Source: Canada Revenue Agency (22/05/2018);  n=`numobs'. Produced: $S_DATE.", size(vsmall) span) ///
		scheme(s1color)

	graph export $path6\can_removedreason_`fdate'.png, replace width(4096)


	**bysort depvar: sum revenue
	**bysort depvar: sum expenditure
			
	
/* England & Wales */

use $path3\ew_charityregister_20180522.dta, clear // Data downloaded from Charity Commission data portal
desc, f
count
notes
label data "Register of all England & Wales charities - 20180522"

	
	// Descriptive statistics
	
	tab1 charitysize aootype
	tab depvar
	tab remy depvar if remy>=2007 // Produce a table
	/*
		What's going in 2009 with Other Removal?
	*/	
	
		tab removed_reason if remy==2007
		tab removed_reason if remy==2008
		tab removed_reason if remy==2009 // Accounted for by the large spike in voluntary deregistrations
	
	local fdate = "01jun2018"

	graph bar , over(depvar) over(charitysize) stack asyvar percent ylabel(, nogrid labsize(small))
	graph bar , over(depvar) over(aootype) stack asyvar percent ylabel(, nogrid labsize(small))
	
	tab remy depvar if remy>=2007
	local numobs:di %6.0fc r(N)
	
	tab depvar if depvar>0 & remy>=2007 // 50% is the average number of vol removals in a given year.
		
	graph bar if remy>=2007 & depvar!=0, over(depvar) over(remy) stack asyvar percent ///
		bar(1, color(dknavy )) bar(2, color(erose)) ///
		ylabel(, nogrid labsize(small)) ///
		ytitle("% of charities", size(medsmall)) ///
		yline(50, lpatt(dash) lcolor(gs8)) ///
		title("Charity Removal Reasons - UK")  ///
		subtitle("by deregistration year")  ///
		note("Source: Charity Commission for England & Wales (22/05/2018);  n=`numobs'. Produced: $S_DATE.", size(vsmall) span) ///
		scheme(s1color)

	graph export $path6\ew_removedreason_`fdate'.png, replace width(4096)


	**bysort depvar: sum revenue
	**bysort depvar: sum expenditure
