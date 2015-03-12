---
title: Project Overview
subtitle: {{ project.ngi_name }}
date: {{ project.report_date }}
support_email: genomics_support@scilifelab.se
swedac: true
---

# Project Information

User Project Name
:   {{ project.user_ID }}

NGI Project Name
:   {{ project.ngi_name }}

NGI Project ID
:   {{ project.ngi_id }}

User Contact
:   [{{ project.contact }}](mailto:{{ project.contact }})

NGI Application Type
:   {{ project.application }} _({% if project.best_practice %}including best practice analysis{% else %}no best practice analysis{% endif %})_

Samples &amp; Lanes
:   {{ project.num_samples }} sample{% if project.num_samples > 1 %}s{% endif %}, {{ project.num_lanes }} lane{% if project.num_lanes > 1 %}s{% endif %}

Project Status
:   {{ project.status }}

Order Dates
:   {{ project.dates }}

UPPMAX Project ID
:   `{{ project.UPPMAX_id }}`

UPPNEX project path
:   `{{ project.UPPMAX_path }}`
{% if project.reference.genome %}
Reference Genome
:   {{ project.reference.organism}} ({{ project.reference.genome }})
{% endif %}{% if project.ordered_reads %}
Minimum ordered reads
:   {{ project.ordered_reads }}
{% endif %}
 
# Methods

### Library construction

{{ project.library_construction }}. Clustering was done using an [Illumina cBot](http://products.illumina.com/products/cbot.html).

### Sequencing
{{ project.sequencing_methods }}

### Data Flow
Raw sequencing data is demultiplexed and converted to FastQ on site before 
being transferred securely to [UPPMAX](http://www.uppmax.uu.se/) for delivery.
Raw data is also transferred to [SNIC SweStore](http://www.snic.vr.se/projects/swestore)
for long term data security.

### Data Processing
To ensure that all sequenced data meets our guarantee of data quality and quantity,
a number of standardised bioinformatics quality control checks are performed before
delivery. These include checking the yield, sequence read quality and cross-sample contamination.

### Swedac Accreditation
The National Genomics Infrastructure is accredited by [Swedac](http://www.swedac.se).
This means that our services are subject to highly stringent quality control procedures,
so that you can be sure that your data is of excellent quality.

Library preparation
:   [cross] Not Swedac Accredited

Sequencing data
:   [tick] Swedac Accredited

Data flow
:   [tick] Swedac Accredited

Data processing
:   [tick] Swedac Accredited

# Sample Info

NGI ID | User ID | Index | Lib Prep | Lib QC
-------|---------|-------|----------|--------
{% for sample in samples.values()  -%}
{% for prep in sample.preps.values() -%}
{{ sample.ngi_id }} | {{ sample.customer_name }} | `{{ prep.barcode }}` | {{ prep.label }} | {{ prep.qc_status }}
{% endfor -%}
{%- endfor %}

* _Lib QC:_ Reception control library quality control step

# Yield Overview

Sample | Avg. FS | &ge; Q30 | # Reads | Status
-------|--------:|---------:|--------:|-------
P955_101b | 350 bp | 59.34% | 105.66 M | Passed

* _Avg. FS:_ Average fragment size.
* _&ge; Q30:_ Percentage of bases above quality score Q30 for the sample.
* _# Reads:_ Millions of reads sequenced.

# Run Info
Date | FC id | Lane | Clusters | % PhiX | &ge; Q30| % Unique | Method
-----|-------|------|---------:|-------:|--------:|---------:|--------
2014-01-23 | `B-H8A63ADXX` | 1 | 66.88 M | 0.52% | 58.70% | 80.51% | A
2014-01-23 | `B-H8A63ADXX` | 2 | 65.89 M | 0.56% | 57.15% | 78.32% | A

* _FC id:_ Flow cell position and ID.
* _&ge; Q30:_ Percentage of bases above quality score Q30 on the lane.
* _Unique:_ Percentage of reads recovered after demultiplexing.
* _Method:_ Sequencing method used. See above for description.

# General Information

## Naming conventions

The data is delivered in FastQ format using Illumina 1.8 quality scores.
There will be one file for the forward reads and one file for the
reverse reads (if the run was a paired-end run).

The naming of the files follow the convention:

```
[LANE]_[DATE]_[POSITION][FLOWCELL]_[NGI-NAME]_[READ].fastq.gz
```

## Data access at UPPMAX

Data from the sequencing will be uploaded to the UPPNEX (UPPMAX Next
Generation sequence Cluster Storage, [uppmax.uu.se](http://www.uppmax.uu.se)),
from which the user can access it. You can find the data in the INBOX folder of the
UPPNEX project, which was created for you when your order was placed: 

```
{{ project.UPPMAX_path }}
```


If you have problems accessing your data, please contact SciLifeLab
[genomics_support@scilifelab.se](mailto: genomics_support@scilifelab.se).
If you have questions regarding UPPNEX, please contact
[support@uppmax.uu.se](mailto:support@uppmax.uu.se).

## Acknowledgements

In publications based on data from the work covered by this contract,
the authors must acknowledge SciLifeLab, NGI and Uppmax:

> The authors would like to acknowledge support from Science for Life Laboratory,
> the National Genomics Infrastructure, NGI, and Uppmax for providing
> assistance in massive parallel sequencing and computational infrastructure.

# Further Help
If you have any queries, please get in touch at
[genomics_support@scilifelab.se](mailto: genomics_support@scilifelab.se).
