# Contributing

## Different functions, different repositories..

Where possible, report scripts should be as minimal as possible. Try to keep
functionality limited to things which can only be useful in the context of making
reports (eg. parsing text files to extract specific information).

All analysis and plotting should be handled by code in different repositories.
Specifically, any scripts to generate plots should be added to the
[visualizations](https://github.com/NationalGenomicsInfrastructure/visualizations) repository and
then imported as a python package. Code involved in retrieving information
from Stockholm's StatusDB should use the
[statusdb](https://github.com/SciLifeLab/statusdb) repository.

Keeping the code separate in this way should enable us to reuse scripts
in different scenarios (eg. the `statusdb` wrapper) and make the
organisation logical for easier maintenance.


## Documentation
As each report script will be quite diverse (expecting different input files
and so on), good documentation is critical. You must state all file
dependencies and how these files should be formatted / generated.

Documentation should be written in MarkDown `.md` files and placed
in the `/docs` folder.

## File Formats
All reports should be generated as Markdown `.md` files. We can then
use [Pandoc](http://johnmacfarlane.net/pandoc/) to convert these into
whatever file format we like (PDF initially, probably HTML later).

All figures should be plotted as both `.png` files (for HTML reports)
and `.pdf` (for PDF reports). When setting the file names for the
markdown, write the file name without an extension. The pandoc
conversion will automatically use the correct file type for the report
that it's making.

If you can't make `png` and `pdf` for whatever reaason, just
specify the full file name with extension and this will be used for
everything.

## Information Flow
The general structure of the package is intended to allow easy use of
the package by both Stockholm and Uppsala NGI nodes. There is a
common entrance script (`/scripts/ngi_reports`) which reads
your config file (`~/.ngi_reports/ngi_reports.conf`) to determine
which NGI node you're at. It also takes the report type from the command
line. Using these two pieces of information, it dynamically loads the
appropriate module. This NGI node - specific module loads a common
module of the same report type as a dependency. This grabs all of the
information that is shared between both sites ans has common functions
(eg. checking the required fields). The object is passed back and node-
specific fields are filled in. Finally, the main script calls the
`Report.parse_template()` function to get the Markdown output
and writes this to `Report.report_fn`. Pandoc is then called to convert
this file to HTML and PDF.

### Example
The following describes the order of execution when creating and IGN Sample
Report at the Stockholm NGI node.

* The main `/scripts/ngi_report` script is executed
    * Conf: NGI node = `stockholm`
    * Command line report type = `ign_sample_report`
* module `/ngi_reports/stockholm/ign_sample_report.py` loaded
    * This loads `/ngi_reports/common/ign_sample_report.py` as a dependency
* `Report` object created
* `__init__` def first initialises the `common.ign_sample_report.Report` object.
* The common `__init__` gets all of the fields that it can using methods availble to both NGI nodes
    * This is mainly scraping information from the file system
* The `stockholm.__init__` then continues and grabs and node-specific fields
    * This is mainly information from statusdb / the LIMS
* The main `ngi_report` script then calls the `Report.parse_template()` function to get the markdown output
    * The  `common.check_fields()` method is called to make sure that we has everything
    * A markdown template called `/data/report_templates/ign_sample_report.md` is used
    * Jinja2 is used to replace the fields in the template with real data
* This markdown string is written to a markdown output file by the main `ngi_reports` script
* `ngi_reports` then calls `pandoc` to convert this file into HTML and PDF.
