# MSOrganiser

<!-- badges: start -->

[![License:
MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/SLINGhub/MSOrganiser/blob/master/LICENSE.md)
<!-- badges: end -->

`MSOrganiser` is created to provide users a convenient way to extract
and organise MRM transition names data exported from mass spectrometry
software into an Excel or csv file in a few button clicks.

With the addition of the
[`MSTemplate_Creator`](https://github.com/SLINGhub/MSTemplate_Creator),
the software is also able to normalize the peak area with respect to the
internal standard’s peak area as well as calculate the concentration of
the analytes.

# Table of Content

-   [MSOrganiser](#msorganiser)
-   [Table of Content](#table-of-content)
-   [Meta](#meta)
-   [Starting Up](#starting-up)
-   [Extracting Area And RT](#extracting-area-and-rt)
-   [Calculating Normalised Area And
    Concentration](#calculating-normalised-area-and-concentration)
-   [Output Format](#output-format)
-   [Transpose Output](#transpose-output)
-   [Long Table Output](#long-table-output)
-   [Concatenation Option](#concatenation-option)
-   [Allow Normalisation With Multiple
    ISTD](#allow-normalisation-with-multiple-istd)
-   [Testing Mode](#testing-mode)

# Meta

-   We welcome [contributions](CONTRIBUTING.md) including bug reports.
-   License: MIT
-   Think `MSOrganiser` is useful? Let others discover it, by telling
    them in person, via Twitter or a blog post.
-   If you wish to acknowledge the use of this software in a journal
    paper, please include the version number. For reproducibility, it is
    advisable to use the software from the
    [Releases](https://github.com/SLINGhub/MSOrganiser/releases) section
    in GitHub rather than from the master branch.
-   Please note that this project is released with a [Contributor Code
    of
    Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).
    By participating in this project you agree to abide by its terms.

# Starting Up

Go to the [Releases](https://github.com/SLINGhub/MSOrganiser/releases)
section in GitHub.

![GitHubRelease](docs/figures/README-GitHubRelease.PNG)

Download the zip folder. Unzip the folder, double click on the file
`MSOrganiser.exe` to start

![FindMSOrganiser](docs/figures/README-FindMSOrganiser.PNG)
![OpenMSOrganiser](docs/figures/README-OpenMSOrganiser.PNG)

# Extracting Area And RT

The test csv data file is exported via Agilent MassHunter Quantitative
Analysis in wide table form.

![WideTableForm](docs/figures/README-WideTableForm.PNG)

Fill in the `Required Input` section such as the `MS_Files`,
`MS_FileType` and `Output_Directory`.

![RequiredInput](docs/figures/README-RequiredInput.PNG)

Next, under the `Output_Options` click on `Area` and `RT`

![OutputOptionsArea](docs/figures/README-OutputOptionsArea.PNG)

Click on `Start` and let the program run

![ProgramRun](docs/figures/README-ProgramRun.gif)

Results files are as follows

![ResultsAreaRTFiles](docs/figures/README-ResultsAreaRTFiles.PNG)

![ResultsArea](docs/figures/README-ResultsArea.PNG)

![ResultsRT](docs/figures/README-ResultsRT.PNG)

![ResultsAreaRTPDF](docs/figures/README-ResultsAreaRTPDF.PNG)

# Calculating Normalised Area And Concentration

The concentration value are calculated as follows:

![ConcentrationCalculation](docs/figures/README-ConcentrationCalculation.PNG)

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

![ResultsnormAreaPDF](docs/figures/README-ResultsnormAreaPDF.PNG)

# Output Format

The results are output as an Excel file. User can change the output type
to as follows

![OutputFormat](docs/figures/README-OutputFormat.PNG)

# Transpose Output

By default, the results are represented in a wide table form with Sample
Name as the first columns followed by the Transitions. To make the
Transition Name as the first column followed by the Sample Names, go to
the `Output Settings` section and change the `Transpose_Results` from
`False` to `True` and click `Start`

![TransposeSettings](docs/figures/README-TransposeSettings.PNG)

The results file will now look like this

![TransposeSettings](docs/figures/README-TransposeResultsArea.PNG)

# Long Table Output

There is also an option to output the results in the form of a long
table.

![LongTableOption](docs/figures/README-LongTableOption.PNG)

![ResultsLongTable](docs/figures/README-ResultsLongTable.PNG)

![LongTableAnnotOption](docs/figures/README-LongTableAnnotOption.PNG)

![ResultsLongTableAnnot](docs/figures/README-ResultsLongTableAnnot.PNG)

# Concatenation Option

When there are several input data file with the same transitions but
different sample names in each file, the results can be concatenated by
setting the `Concatenate` settings to
`Concatenate along Sample Name (rows)`

![ConcatenateRowOption](docs/figures/README-ConcatenateRowOption.PNG)

When there are several input data file with the same sample name but
different transitions in each file, the results can be concatenated by
setting the `Concatenate` settings to
`Concatenate along Transition Name (columns)`

Concatenated results are as follows

![ResultsConcatenateRow](docs/figures/README-ResultsConcatenateRow.gif)

# Allow Normalisation With Multiple ISTD

By default, the software will only allow one transition to be normalised
by one ISTD. However, during method development, there may be a need for
one transition to be normalised by multiple ISTD to see which one is the
best one to use. To relax this restriction, ensure that
`Allow_Multiple_ISTD` is set to `True`

![MultipleISTDOption](docs/figures/README-MultipleISTDOption.PNG)

In this example, the following annotation file will be used

![AnnotationMultipleISTD](docs/figures/README-AnnotationMultipleISTD.gif)

Load the annotation file onto `Annot_File` and press `Start`

![OutputOptions\_normArea\_and\_normConc\_MultipleISTD](docs/figures/README-OutputOptions_normArea_and_normConc_MultipleISTD.PNG)

The main changes in the results are as follows

![ResultsnormAreaMultipleISTD](docs/figures/README-ResultsnormAreaMultipleISTD.PNG)

![ResultsnormConcMultipleISTD](docs/figures/README-ResultsnormConcMultipleISTD.PNG)

The output can be transposed to make it suited to be read by a
statistical software.

![TransposeSettings](docs/figures/README-TransposeSettings.PNG)

Here are the transposed output

![ResultsnormAreaMultipleISTDTranspose](docs/figures/README-ResultsnormAreaMultipleISTDTranspose.PNG)

![ResultsnormConcMultipleISTDTranspose](docs/figures/README-ResultsnormConcMultipleISTDTranspose.PNG)

# Testing Mode

`MSOrganiser` by default turns positive and negative infinity to missing
values. However, it is challenging to trace back the reason behind a
missing value in the concentration because of many possibilities.

Below are a list of possible reasons.

-   The peak area of the transition is a missing value.
-   The peak area of the internal standard is a missing value or zero.
-   The sample amount of the sample is a missing value or zero.
-   The volume of the internal standard mixture is a missing value.
-   The concentration of the internal standard is a missing value.

It is harder when there is a need to explain how the concentration
values are calculated to a collaborator who is unfamiliar with your
work. More so when explaining the reason behind the missing values.

The testing mode when activated will provide additional sheets in Excel
or csv files such as `ISTD_Area`, `ISTD_Conc` and
`ISTD_to_Samp_Amt_Ratio` to assist in the explanation.

![TestingMode](docs/figures/README-TestingMode.PNG)

![ResultsISTD\_Area](docs/figures/README-ResultsISTD_Area.PNG)

![ResultsISTD\_Conc](docs/figures/README-ResultsISTD_Conc.PNG)

![ResultsISTD\_to\_Samp\_Amt\_Ratio](docs/figures/README-ResultsISTD_to_Samp_Amt_Ratio.PNG)

It is easier to explain how the values in `ISTD_Area`, `ISTD_Conc` and
`ISTD_to_Samp_Amt_Ratio` are created. With these additional info, we can
simply tell others that the concentration values is calculated as
follows:

-   `normArea by ISTD` = (`Area` / `ISTD_Area`)

-   `normConc by ISTD` = (`Area` / `ISTD_Area`) \*
    `ISTD_to_Samp_Amt_Ratio` \* `ISTD_Conc`
