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

{% if project.ngi_facility %}
NGI Facility
:   Genomics {{ project.ngi_facility }} Stockholm
{% endif %}

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

{{ project.library_construction }}

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
:   {{ project.accredit.library_preparation }}

Sequencing data
:   {{ project.accredit.sequencing }}

Data Processing
:   {{ project.accredit.data_processing }}

Data Analysis
:   {{ project.accredit.data_analysis }}

# Sample Info

NGI ID | User ID | Mreads | >=Q30(%) | Status
-------|---------|--------|----------|--------
{% for sample in samples.values()  -%}
{{ sample.ngi_id }} | {{ sample.customer_name }} | `{{ sample.total_reads }}` | {{ sample.qscore }} | {{ sample.seq_status }}
{%- endfor %}

* _NGI ID:_ Internal id used within NGI to refer a sample
* _User ID:_ User submitted name for a sample
* _Mreads:_ Total million reads (or pairs) for a sample
* _>=Q30:_ Aggregated percentage of bases that have quality score more the Q30
* _Status:_ Sequencing status of sample based on the total reads

# Library Info

NGI ID | Index | Lib Prep | Avg. FS | Lib QC
-------|-------|----------|---------|--------
{% for sample in samples.values()  -%}
{% for prep in sample.preps.values() -%}
{{ sample.ngi_id }} | `{{ prep.barcode }}` | {{ prep.label }} | {{ prep.avg_size }} | {{ prep.qc_status }}
{% endfor -%}
{%- endfor %}

* _NGI ID:_ Internal id used within NGI to refer a sample
* _Index:_ Barcode sequence used for the sample
* _Lib Prep:_ ID (alphabatical number) of library prep made.
* _Avg. FS:_ Average fragment size of the library.
* _Lib QC:_ Reception control library quality control step

# Lanes Info

Date | FC id | Lane | Cluster(M) | >=Q30(%) | Phix | Method
-----|-------|------|------------|----------|------|--------
{% for fc in flowcells.values() -%}
{% for lane in fc.lanes.values() -%}
{{ fc.date }} | `{{ fc.name }}` | {{ lane.id }} | {{ lane.cluster }} | {{ lane.phix }} | {{ lane.avg_qval }} | {{ fc.seq_meth }}
{% endfor -%}
{%- endfor %}

* _Date:_ Date of sequencing
* _FC id:_ Name/id of flowcell sequenced
* _Lane:_ Lane id for the flowcell
* _Clusters:_ Number of clusters in million for passed filter reads.
* _>=Q30:_ Aggregated percentage of bases that have quality score more the Q30
* _Phix:_ Average Phix error rate for the lane
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

In publications based on data from the work covered by this agreement,
the authors must acknowledge SciLifeLab, NGI and Uppmax:

> The authors would like to acknowledge support from Science for Life Laboratory,
> the National Genomics Infrastructure, NGI, and Uppmax for providing
> assistance in massive parallel sequencing and computational infrastructure.

# Further Help
If you have any queries, please get in touch at
[genomics_support@scilifelab.se](mailto: genomics_support@scilifelab.se).
