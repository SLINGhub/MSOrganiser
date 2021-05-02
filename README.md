# MSOrganiser

MSOrganiser is created to provide users a convenient way to extract and
organise MRM transition names data exported from mass spectrometry
software into an Excel or csv file in a few button clicks.

With the addition of the MSTemplate\_Creator, the software is also able
to normalize the peak area with respect to the internal standard’s peak
area as well as calculate the concentration of the analytes.

It is currently distributed as platform independent source code under
the MIT license.

## Starting Up

Download the repository and open the dist folder. Inside the dist
folder, double click on the file `MSOrganiser.exe` to start

![FindMSOrganiser](docs/figures/README-FindMSOrganiser.PNG)
![OpenMSOrganiser](docs/figures/README-OpenMSOrganiser.PNG)

## Extracting Area and RT

The test csv data file is exported via Agilent MassHunter Quantitative
Analysis in wide table form.

![WideTableForm](docs/figures/README-WideTableForm.PNG)

Fill in the `Required Input` section such as the `MS_Files`,
`MS_FileType` and `Output_Directory`.

![RequiredInput](docs/figures/README-RequiredInput.PNG)

Next, under the `Output_Options` click on `Area` and `RT`

![OutputOptionsArea](docs/figures/README-OutputOptionsArea.PNG)

Ensure the `Output_Settings` is as follows.

![OutputOptionsArea](docs/figures/README-DefaultOutputSettings.PNG)

Click on `Start` and let the program run

![ProgramRun](docs/figures/README-ProgramRun.gif)

Results files are as follows

![ResultsAreaRTFiles](docs/figures/README-ResultsAreaRTFiles.PNG)

![ResultsArea](docs/figures/README-ResultsArea.PNG)

![ResultsRT](docs/figures/README-ResultsRT.PNG)

![ResultsAreaRTPDF](docs/figures/README-ResultsAreaRTPDF.PNG)

## Calculating normalised Area and Concentration

To do this, a corresponding annotation file is required.

The content in the annotation file are as follows:

![Annotation](docs/figures/README-Annotation.gif)

In the `Data_extraction` section, click on `normArea by ISTD` and
`normConc by ISTD`. Load the annotation file onto `Annot_File` and press
`Start` to let the program run.

![OutputOptions\_normArea\_and\_normConc](docs/figures/README-OutputOptions_normArea_and_normConc.PNG)

When the program has finished running, the results will contain the
following sheets including the normalised area and concentration.

![ResultsTransitionAnnot](docs/figures/README-ResultsTransitionAnnot.PNG)

![ResultsnormArea](docs/figures/README-ResultsnormArea.PNG)

![ResultsSampleAnnot](docs/figures/README-ResultsSampleAnnot.PNG)

![ResultsnormConc](docs/figures/README-ResultsnormConc.PNG)
