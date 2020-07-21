# Usage

## Report Generation
The usual entry point for report generation is through the `ngi_reports` script.
See the [installation instructions](installation.md) for instructions on how
to add this script to your `PATH`.

If you have an output directory made by Piper, `ngi_reports` will read everything
it needs from the setup XML files. You can run it as so:

```
cd path/to/piper/output
ngi_reports <report_type>
```

Other report types or non-piper directories may need additional command line inputs.

The package will generate a directory called `reports` containing
an HTML report, a Markdown report and a subdirectory called `plots`.
If running from a Piper directory, `reports` will be inside `delivery`.

The package is designed to be run automatically by the processing pipelines.

### Available Report Types
To list the available report types and get additional help, run:

```
ngi_reports -h
```

## Manual Edits
If you need to manually edit any reports, make your changes to the markdown
files and then run the following command:

```
ngi_reports <report_type> --regenerate_html_from_md --markdown_file <path/to/mdfile>
```

The command for regenerating the Project Summary report is aliased as `make_report` on Uppmax.
