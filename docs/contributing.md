# Contributing

## Different functions, different repositories..

Where possible, report scripts should be as minimal as possible. Try to keep
functionality limited to things which can only be useful in the context of making
reports (eg. parsing text files to extract specific information).

All analysis and plotting should be handled by code in different repositories.
Specifically, any scripts to generate plots should be added to the
[visualizations](https://github.com/NationalGenomicsInfrastructure/visualizations) repository and
then imported as a python package.

## Documentation
As each report script will be quite diverse (expecting different input files
and so on), good documentation is critical. You must state all file
dependencies and how these files should be formatted / generated.

Documentation should be written in MarkDown `.md` files and placed
in the `/docs` folder.

## File Formats
All reports should be generated as Markdown `.md` files. These are then
converted to HTML.

All figures should be plotted as `.png` files. When setting the file names
for the markdown, write the file name without an extension.

If you can't make `png` for whatever reason, just
specify the full file name with extension and this will be used for
everything.

## Information Flow
The general structure of the package is intended to allow easy use of
the package by the Stockholm NGI node. There is an entrance script
(`/scripts/ngi_reports`) which reads your config file (`~/.ngi_reports/ngi_reports.conf`).
It also takes the report type from the command line. Using these two pieces of information,
it dynamically loads a common module which has common functions (eg. checking the required fields)
The object is passed back and report-specific fields are filled in. Finally, the main script
calls the `Report.parse_template()` function to get the Markdown output
and writes this to `Report.report_fn`. Jinja2 is then called to convert
this file to HTML.

### Example
The following describes the order of execution when creating a Project summary report.

* The main `/scripts/ngi_report` script is executed
    * Command line report type = `project_summary`
* module `/ngi_reports/reports/project_summary.py` loaded
* `Report` object created
* `__init__` def first initialises the `reports.project_summary.Report` object.
* The `__init__` gets all of the fields that it can using methods available by mainly scraping information from the file system
* It then continues and grabs node-specific fields
    * This is mainly information from statusdb / the LIMS
* The main `ngi_report` script then calls the `Report.parse_template()` function to get the markdown output
    * The  `common.check_fields()` method is called to make sure that we has everything
    * A markdown template called `/data/report_templates/project_summary.md` is used
    * Jinja2 is used to replace the fields in the template with real data
* This markdown string is written to a markdown output file by the main `ngi_reports` script
* `ngi_reports` then calls Jinja2 to insert this data into the report template.
