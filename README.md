# MSTemplate\_Creator

MSTemplate\_Creator is an excel macro file created to provide users a
more friendly interface to take in MRM transition names data exported
directly from mass spectrometry software to create several annotation
templates suited for automated data processing and statistical analysis.

It is currently distributed as platform independent source code under
the MIT license.

## Starting Up

Download the repository and open the excel macro file
`MSTemplate_Creator.xlsm`

![OpenMSTemplate\_Creator](figures/OpenMSTemplate_Creator.JPG)

Upon opening you may encounter this security warning. Click on **Enable
Content** so that the macro in the file will be activated.

![EnableContent](figures/EnableContentWarning.jpg)

## Using Transition\_Annot Sheet

Load transition names from Agilent MRM data in csv file with **Load
Transition\_Name from Raw Data**

![Load Transition\_Name from Raw Data](figures/trial.gif)

Load transition names from tabular data in csv file with **Load
Transition\_Name from Table Data**

![Load Transition\_Name from Table Data](figures/trial2.gif)

Check the internal standards with **Validate ISTD**. Once validated,
transfer the internal standards to sheet `ISTD_Annot` with **Load ISTD
to ISTD\_Table**

![Validate ISTD](figures/trial3.gif)

Once validated, transfer the internal standards to sheet `ISTD_Annot`
with **Load ISTD to ISTD\_Table**

![Load ISTD to ISTD\_Table](figures/trial4.gif)

## Using ISTD\_Annot Sheet

Key in the concentration of the internal standard and convert to nM or
other units to verify. Unit values under the column `Custom_Unit` can be
used later to obtain the sample unit of concentration.

![Convert to nM](figures/trial5.gif)

## Using Sample\_Annot Sheet

Load sample names from Agilent MRM data in csv file with **Load Sample
Annotation from Raw Data**. Use **Autofill ‘Sample’ in Sample\_Type** to
fill empty cells under the `Sample_Type` column with “SPL”

![Load Sample Annotation from Raw Data](figures/trial7.gif)

It is possible to merge Agilent MRM data with a sample annotation file
in csv.

![Merge Raw Data with Sample Annotation](figures/trial10.gif)

Load sample names from tabular data in csv file with **Load Sample
Annotation from Table Data**. Use **Autofill ‘Sample’ in Sample\_Type**
to fill empty cells under the `Sample_Type` column with “SPL”

![Load Sample Annotation from Table Data](figures/trial6.gif)

On the `Sample_Annot` sheet, fill in the sample amount unit for each
sample. Next, on the `ISTD_Annot` sheet, select the concentration unit
of the internal standard to use under the `Custom_Unit` column. Return
to the `Sample_Annot` sheet and use **Autofill Concentration\_Unit** to
obtain each sample’s unit of concentration

![Autofill Concentration\_Unit](figures/trial8.gif)

Transfer Sample with QC sample type of “RQC” to `Dilution_Annot` sheet
with **Load RQC Samples to Dilution\_Table**

![Autofill Concentration\_Unit](figures/trial9.gif)
