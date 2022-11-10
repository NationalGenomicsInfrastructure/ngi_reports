# Installation

## ngi_reports Python Package
To create reports you need to install the `ngi_reports` package.
First, either download or clone the [repository](https://github.com/NationalGenomicsInfrastructure/ngi_reports).
Make sure that you include the `--recursive` flag:

```
git clone --recursive https://github.com/NationalGenomicsInfrastructure/ngi_reports.git
```
_(remember to fork instead if you intend to make changes to the code)_

Next, install the package by running:

```
cd ngi_reports
pip install -e .
```

These commands should install all dependencies so that the python code is ready to run.
If you're intending to make changes to the code, use `develop` instead of `install`
so that you don't need to run the setup script each time you make a change.

Next, you need a config file in your home directory called
`~/.ngi_config/ngi_reports.conf`. This file should be formatted for
[Python ConfigParser](https://docs.python.org/2/library/configparser.html)
and look like this:

```ini
[ngi_reports]
support_email: genomics_support@scilifelab.se

[organism_names]
hg19: Human
hg18: Human
mm10: Mouse
mm9: Mouse
canFam3: Dog
canFam2: Dog
sacCer2: Saccharomyces cerevisiae
TAIR9: Arabidopsis
rn5: Rat
rn4: Rat
WS210: C. elegans
xenTro2: Xenopus
dm3: Drosophila
```

The `organism_names` section should have
reference id key - text pairs. This is used to make the report more verbose.
