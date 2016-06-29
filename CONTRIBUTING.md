# Contributing to NGI Reports

When contribution to this package please have the following things in mind:

__NOTE__: _Please make sure that there are no exisiting [issues]((https://github.com/NationalGenomicsInfrastructure/ngi_reports/issues)) relating to whatever you want to report._

#### To contribute:
1. Create an issue describing the bug / suggestion / improvement / ... [here](https://github.com/NationalGenomicsInfrastructure/ngi_reports/issues).
2. Fork this repository to your GitHub account
3. Make the necessary changes / additions to your forked repository
4. Please *make sure* that you've documented your code using [MkDocs](http://www.mkdocs.org/) MarkDown syntax and deployed using `mkdocs gh-deploy`
5. Update the version number in `ngi_reports/__init__.py`
6. Pull Request and wait for the PR responsible to review and merge the code

#### Setting the correct version number

Version numbers follow the typical `MAJOR.MINOR.REVISION` system. If you suspect another pull requests will be merged before yours, simply ask the PR responsible to suggest a number as part of their review. 

###### Version numbers in brief

Revision - Small sized updates such as addressing a logic error or changing what version of a dependency is required
Minor - Medium sized updates such as adding a new functionality or optimizing an existing feature
Major - Large sized updates that either add a big bundle of functionality, or optimization that required a large section of the repository to be refactored.

You can find more detailed instructions in the ngi_reports documentation:
http://nationalgenomicsinfrastructure.github.io/ngi_reports/contributing/

Thanks!
