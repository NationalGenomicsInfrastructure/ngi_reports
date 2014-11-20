# NGI Reports Documentation

This documentation describes the code in the
[ngi_reports](https://github.com/SciLifeLab/ngi_reports)
github repository.

## Introduction
A common task within NGI is to create user reports. These can range from
delivery reports containing basic sample information through to Best Practice
reports with in-depth analysis.

The `ngi_reports` package is a common framework for generating reports
with consistent styling.  It's designed to work for both NGI Stockholm and
Uppsala nodes. To facilitate this, code is divided into three modules:
`common`, `stockholm` and `uppsala`.

Where possible, report scripts should be as minimal as possible. All analysis
and plotting should be done before this script is called. Here, we just want to
scoop up results and plots from the file structure and assemble them into a
report. Any scripts to generate plots should be added to the
[visualizations](https://github.com/SciLifeLab/visualizations) repository.


## Documentation
As each report script will be quite diverse (expecting different input files
and so on), good documentation is critical. You must state all file
dependencies and how these files should be formatted / generated.

Documentation should be written in MarkDown `.md` files and placed
in the `/docs` folder. See the [Contributing](contributing.md) page for more
instructions.
