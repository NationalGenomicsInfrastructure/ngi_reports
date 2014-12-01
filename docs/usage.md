# Usage

## Report Generation
The usual entry point for report generation is through the `ngi_reports` script.
You can make it easier to run this script by adding it's location to your `PATH`
in your `.bash_rc` script (`.bash_profile` if using a Mac):

```bash
echo "PATH=path/to/ngi_reports/scripts:$PATH" >> ~/.bashrc
```

Then you can run the ngi_reports script in the pipeline output directory:

```bash
cd path/to/output
ngi_reports <report_type>
```

If you are in the correct output directory and select a relevant report
type, the script should generate a directory called `reports` containing 
a PDF report, an HTML report, a Markdown report and a subdirectory called `plots`.

The package is designed to be run automatically by the processing pipelines.

## Available Report Types
To list the available report types, run:

```
ngi_reports -h
```

## Manual Edits
If you need to manually edit any reports, make your changes to the markdown
file and then run the following two commands:

```bash
pandoc report.md -o report.html --template=pandoc_templates/html_pandoc.html
pandoc report.md -o report.pdf --template=pandoc_templates/latex_pandoc.tex --latex-engine=xelatex
```

***Note:*** Replace `pandoc_templates/` with the correct relative or absolute
path to this directory on your machine; eg:

```bash
/Users/philewels/Work/ngi_reports/data/pandoc_templates/
```

To make these commands easier to run, you can create functions in your `.bashrc` file
(`.bash_profile` on Mac). Add the following:

```bash
function make_report {
  pandoc ${1}.md -o ${1}.html --template=pandoc_templates/html_pandoc.html
  pandoc ${1}.md -o ${1}.pdf --template=pandoc_templates/latex_pandoc.tex --latex-engine=xelatex
}
export -f make_report
```

Again, make sure that you update the `pandoc_templates/` path.
You can then create reports by running:

```
make_report report_fn
```
_(note - do not include the `.md` extension)_