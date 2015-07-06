---
title: Project Overview
subtitle: {{ project.ngi_name }}
date: {{ project.report_date }}
support_email: {{ project.support_email }}
swedac: true
---

# Project Information

User Project Name
:   {{ project.user_ID }}

NGI Project Name
:   {{ project.ngi_name }}

NGI Project ID
:   {{ project.ngi_id }}

{% if project.ngi_facility -%}
NGI Facility
:   {{ project.ngi_facility }}
{%- endif %}

User Contact
:   [{{ project.contact }}](mailto:{{ project.contact }})

NGI Application Type
:   {{ project.application }} _({% if project.best_practice %}including best practice analysis{% else %}no best practice analysis{% endif %})_

{% if project.num_samples -%}
Samples &amp; Lanes
:   {{ project.num_samples }} sample{% if project.num_samples > 1 %}s{% endif %}{% if project.num_lanes -%}, {{ project.num_lanes }} lane{% if project.num_lanes > 1 %}s{% endif %}{% endif %}
{%- endif %}

Order Dates
:   {{ project.dates }}

UPPMAX Project ID
:   `{{ project.UPPMAX_id }}`

UPPNEX project path
:   `{{ project.UPPMAX_path }}`

{% if project.reference.genome -%}
Reference Genome
:   {{ project.reference.organism}} ({{ project.reference.genome }})
{%- endif %}

{% if project.ordered_reads -%}
Minimum ordered reads
:   {{ project.ordered_reads }}
{%- endif %}
 
# Methods

{% if project.library_construction -%}
### Library construction
{{ project.library_construction }}
{%- endif %}

{% if project.sequencing_methods -%}
### Sequencing
{{ project.sequencing_methods }}
{%- endif %}

### Data Flow
Raw sequencing data is demultiplexed and converted to FastQ on site before 
being transferred securely to [UPPMAX](http://www.uppmax.uu.se/) for delivery.

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

Sequencing
:   {{ project.accredit.sequencing }}

Data Processing
:   {{ project.accredit.data_processing }}

Data Analysis
:   {{ project.accredit.data_analysis }}

# Sample Information
{% if not samples %}
No sample information to be displayed.
{% elif samples|length > project.display_limit %}
Sample information table can be viewed tab-separated text file, please click [here]({{ project.ngi_name }}_sample_info.txt) (table hidden due to number of samples). Below you can find an explanation of the header column used in the table.

{{ tables.sample_info }}
{% else %}
NGI ID | User ID | Mreads | >=Q30(%) {% if project.ordered_reads %}| Status {% endif %}
-------|---------|--------|----------{% if project.ordered_reads %}|-------- {% endif %}
{% for sample in samples.values() -%}
{{ sample.ngi_id }} | {{ sample.customer_name }} | `{{ sample.total_reads }}` | {{ sample.qscore }} {% if project.ordered_reads %} | {{ sample.seq_status }} {% endif %}
{% endfor %}

The table is also saved as parseable tab-separated text [file]({{ project.ngi_name }}_sample_info.txt) for convenience. Below you can find an explanation of the header column used in the table.
{{ tables.sample_info }}
{% endif %}


# Library Information
{% if project.missing_prep == samples|length %}
No library information to be displayed.
{% elif samples|length > project.display_limit %}
Library information table can be viewed tab-separated text file, please click [here]({{ project.ngi_name }}_library_info.txt) (table hidden due to number of samples). Below you can find an explanation of the header column used in the table.

{{ tables.library_info }}
{% else %}
NGI ID | Index | Lib Prep | Avg. FS | Lib QC
-------|-------|----------|---------|--------
{% for sample in samples.values()  -%}
{% if sample.preps -%}
{% for prep in sample.preps.values() -%}
{{ sample.ngi_id }} | `{{ prep.barcode }}` | {{ prep.label }} | {{ prep.avg_size }} | {{ prep.qc_status }}
{% endfor -%}
{% endif -%}
{%- endfor %}

The table is also saved as parseable tab-separated text [file]({{ project.ngi_name }}_library_info.txt) for convenience. Below you can find an explanation of the header column used in the table.
{{ tables.library_info }}
{% endif %}


# Lanes Information
{% if project.missing_fc %}
No lanes information to be displayed.
{% elif project.total_lanes > project.display_limit %}
Lanes information table can be viewed tab-separated text file, please click [here]({{ project.ngi_name }}_lanes_info.txt) (table hidden due to number of lanes). Below you can find an explanation of the header column used in the table.

{{ tables.lanes_info }}
{% else %}
Date | Flowcell | Lane | Clusters(M) | PhiX | >=Q30(%) | Method
-----|----------|------|-------------|------|----------|--------
{% for fc in flowcells.values() -%}
{% for lane in fc.lanes.values() -%}
{{ fc.date }} | `{{ fc.name }}` | {{ lane.id }} | {{ lane.cluster }} | {{ lane.phix }} | {{ lane.avg_qval }} | {{ fc.seq_meth }}
{% endfor -%}
{%- endfor %}

The table is also saved as parseable tab-separated text [file]({{ project.ngi_name }}_lanes_info.txt) for convenience. Below you can find an explanation of the header column used in the table.
{{ tables.lanes_info }}
{% endif %}

{% if project.aborted_samples %}
# Aborted/Not Sequenced samples

NGI ID | User ID | Status
-------|---------|-------
{% for sample, info in project.aborted_samples.iteritems() -%}
{{ sample }} | {{ info.user_id }} | {{ info.status }}
{% endfor -%}
{% endif %}

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

If you have problems accessing your data, please contact NGI
[{{ project.support_email }}](mailto:{{ project.support_email }}).
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
[{{ project.support_email }}](mailto:{{ project.support_email }}).
