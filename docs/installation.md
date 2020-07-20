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
python setup.py install
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

**Note:** In production, `ngi_reports` is run as the `funk` user by the
Stockholm node.

## Bash Commands
To use `ngi_reports` from the command line easily, there are some bash commands
that you need. These are written into a bash script to make life easy - you need to add
this to your `~/.bashrc` file (`~/.bash_profile` on a mac):

```
source ~/opt/ngi_reports/scripts/start_ngi_reports.sh
```

**note that you need to change the path to point to your ngi_reports directory..**

If you are running `ngi_reports` on Uppmax, use the following script instead:

```
source ~/opt/ngi_reports/scripts/uppmax_ngi_reports.sh
```

## ngi_visualizations
The `ngi_reports` scripts use a separete Python module called `ngi_visualizations`.
You can find this repository along with installation instructions on github:
[ngi_visualizations](https://github.com/NationalGenomicsInfrastructure/ngi_visualizations)

At the time of writing, the package could be installed as follows:

```bash
git clone https://github.com/NationalGenomicsInfrastructure/ngi_visualizations.git
cd ngi_visualizations
python setup.py install
```
