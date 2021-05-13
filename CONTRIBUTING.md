# Contributing to `MSOrganiser`

First of all, thanks for considering contributing to `MSOrganiser` 😄! We hope that you have found the tool useful in your work 😀 and we apologise for any mishaps 😣 along the way.

`MSOrganiser` is an open source project, maintained by people who care.

## Code of conduct 👩‍🏫

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Ask a question ❓️

Using `MSOrganiser` and got stuck? 
Browse the [Summary and User Documentation](https://github.com/SLINGhub/MSOrganiser/tree/master/docs) to see if you can find a solution. 

Still stuck? Post your question as an [issue on GitHub](https://github.com/SLINGhub/MSOrganiser/issues). While we cannot offer quick user support, we'll try to do our best to address it, as questions often lead to better documentation 📜 or the discovery of bugs 🐛.

## Improve the documentation 📜

Noticed a typo ? 
Have a better example or dataset to explain a function? Good [documentation](https://github.com/SLINGhub/MSOrganiser/tree/master/docs) makes all the difference, so your help to improve it is very welcome!

If you are just started on it, look at the Summary file. 

If you need a step by step guide, use the User Documentation file.

If you need to understand the source code organisation and details, the Developer Documentation file will be useful.

We apologise that function documentation is not available at this moment and is still a work in progress. Do help us if you can. I manage to create a source folder for [Sphinx](https://www.sphinx-doc.org/en/master/) to create a function documentation.

I understand that some may prefer to have online documentation. Unfortunately, I do not have the expertise to do that..

## Contribute code 📝

Care to fix bugs 🐛 or implement new functionality for `MSOrganiser`? Great👏! Thank you for volunteering your time to help out. Have a look at the [issue list](https://github.com/SLINGhub/MSOrganiser/issues) and leave a comment on the things you want to work on. See also the development guidelines below.

## Development guidelines 👨‍💻

### README Documentation

For the README documentation, [Rmarkdown](https://rmarkdown.rstudio.com/) is used together with [R](https://www.r-project.org/) and [RStudio IDE](https://www.rstudio.com/products/rstudio/download/).

Here are some useful resources.
  * https://www.rstudio.com/resources/webinars/getting-started-with-r-markdown/ 
  * https://rmarkdown.rstudio.com/github_document_format.html

RStudio was used because of its friendly user interface (more button clicks than command lines) to create markdown and html document and to use git. Based on past experiences, it is easier to guide beginners to create html documents and use git using RStudio than pure command line. In addition, most people in the lab uses R. 

With the efforts made by the [R for Data Science Online Learning Community](https://www.rfordatasci.com/), they have created a learning environment via their [Slack account](http://r4ds.io/join) which make beginners more comfortable to ask question and share about R, RStudio, Rmarkdown, Git and GitHub issues. Give it a try to make your learning experience in R, Statistics, Git and GitHub a more fruitful experience that is worth sharing.

### GitHub Workflow

We try to follow the [GitHub flow](https://guides.github.com/introduction/flow/) for development.

1. Fork [this repo](https://github.com/SLINGhub/MSTemplate_Creator) and clone it to your computer. To learn more about this process, see [this guide](https://guides.github.com/activities/forking/).
2. If you have forked and cloned the project before and it has been a while since you worked on it, [pull changes from the original repo](https://help.github.com/articles/merging-an-upstream-repository-into-your-fork/) to your clone by using `git pull upstream master`.
3. Make your changes:
    * Write your code.
    * Test your code (bonus points for adding unit tests) .
    * Document your code so that others can understand.
    * Run the unit test in Python
4. Commit and push your changes.
5. Submit a [pull request](https://guides.github.com/activities/forking/#making-a-pull-request).

