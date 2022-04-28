# MSOrganiser 1.1.1.9000 (development version)

## TODO

* Find a way to make the documentation of the functions of `MSOrganiser` online.

# MSOrganiser 1.1.1 

* Updated code to work in the pandas version 1.4.2
* Checked that the program works with GTK3 Version 3.24.31
* Add a warning message when user has ISTDs in the ISTD_Annot sheet that is not in the Transition_Name_Annot sheet. Resulting merged sheet between Transition_Name_Annot and ISTD_Annot will not have these excess ISTDs
* Updated documentation to include an updated version for ISTD concentration calculation.

# MSOrganiser 1.1.0

* Added a logo.
* Add warning message during concentration calculation when user input a sample that is found in the raw data but not found in the sample annotation file.
* Add warning message when user input a sample annotation file with missing data file name or sample name.
* Add warning message when user input a raw data file that has duplicate sample names or transition names with or without concatenation.
* Update MSTemplate_Creator changes to the Concentration Unit.

# MSOrganiser 1.0.0

* Added some Github related markdown files like issue templates, contributing guidelines and code of conduct.

# MSOrganiser 0.0.2

* Changed output excel sheet font to "Consolas" so that the number "0" and the letter "O" can be differentiated easily.
* Add error message to encourage users to use a later version of `MSTemplate_Creator` (above 0.0.1)
* Allow normalisation of multiple ISTD
* Allow concentration calculation of multiple ISTD
* Change positive and negative infinitiy values to NaN

# MSOrganiser 0.0.1

* Added a `NEWS.md` file to track changes to the package.
* Aim to create a git tag version of this
