---
title: Project Overview
subtitle: J.Lundeberg_14_01
date: 2014-12-02
support_email: genomics_support@scilifelab.se
---

# Project Information

User Project Name
:   {{ project.user_ID }}

NGI Project Name
:   {{ project.ngi_name }}

NGI Project ID
:   {{ project.id }}

User Contact
:   [{{ project.contact }}](mailto:{{ project.contact }})

NGI Application Type
:   {{ project.application_type }} ({% if project.best_practice %}With best practice analysis{% else %}No best practice analysis{% endif %})

Samples &amp; Lanes
:   {{ project.num_samples }} sample{% if project.num_samples > 1 %}s{% endif %}, {{ project.num_lanes }} lane{% if project.num_lanes > 1 %}s{% endif %}

Project Status
:   {{ project.status }}

Order Dates
:   _Order received:_ {{ project.dates.order_received }},  _Contract received:_ {{ project.dates.contract_received }}, 
    _Samples received:_ {{ project.dates.samples_received }},  _Queue date:_ {{ project.dates.queue_date }},
    _All data delivered:_ {{ project.dates.all_data_delivered }}, _Report Date:_ {{ project.dates.report_date }}

UPPMAX Project ID
:   `{{ project.UPPMAX_id }}`

UPPNEX project path
:   `{{ project.UPPMAX_path }}`
{% if project.ref_genome %}
Reference Genome
:   {{ project.ref_genome }}
{% endif %}{% if project.ordered_reads %}
Minimum ordered reads
:   {{ project.ordered_reads }}
{% endif %}
 
# Methods

### Library construction

A) Library was prepared using the "650 bp insert standard DNA (Illumina TruSeq DNA)" 
    protocol and clustering was done by cBot.

### Sequencing
A) All samples were sequenced on HiSeq2500 (HiSeq Control
    Software 2.0.12.0/RTA 1.17.21.3) with a 2x101 setup.The Bcl to
    Fastq conversion was performed using bcl2Fastq v1.8.3 from the
    CASAVA software suite. The quality scale used is Sanger /
    phred33 / Illumina 1.8+.

### Data Flow
All data (demultiplexed) from the instrument are collected and transfered securely
to a storage server with well established pipeline.

### Data Processing:
A set of standard quality checks were performed to assure that all sequenced data
meet NGI guaranteed quality / quantity. All analysis are carried out in UPPMAX servers
before delivering the raw data.

### Swedac Accreditation
The National Genomics Infrastructure is accredited by [Swedac](http://www.swedac.se).
This means that our services are subject to highly stringent quality control procedures,
so that you can be sure that your data is of excellent quality.

Library preparation
:   ![cross] Not Swedac Accredited

Sequencing data
:   ![tick] Swedac Accredited

Data flow
:   ![tick] Swedac Accredited

Data processing
:   ![tick] Swedac Accredited

# Sample Info

NGI ID | User ID | Index | Lib Prep
-------|---------|-------|---------
{% for s in samples %}
{{s.id}} | {{s.u_id}} | {{s.index}} (`{{s.barcode}}`) | {{s.lib_prep}}
{% endfor %}

+-----------------+--------------------------+-------------------+---------------+
| NGI ID          | User ID                  | Index             | Lib Prep      |
+=================+==========================+===================+===============+
| P955_101        | 140117_Rapid_Ventana_TdT | Index 8 (`ACTTGA`)| A             |
+-----------------+--------------------------+-------------------+---------------+

# Yield Overview

+---------------+------------+----------------+------------+---------------+------------+
| Sample        | Lib QC     | Avg. FS        | &ge; Q30   | # Reads       | Status     |
+===============+============+================+============+===============+============+
| P955_101b     | Passed     | 350 bp         | 59.34%     | 105.66 M      | Passed     |
+---------------+------------+----------------+------------+---------------+------------+

* _Lib QC:_ Reception control library quality control step
* _Avg. FS:_ Average fragment size.
* _&ge; Q30:_ Percentage of bases above quality score Q30 for the sample.
* _# Reads:_ Millions of reads sequenced.

# Run Info
+---------+---------------+--------+------------+----------+----------+-------------+----------+
| Date    | FC id         | Lane   | Clusters   | % PhiX   | &ge; Q30 | % Unique    | Method   |
+=========+===============+========+============+==========+==========+=============+==========+
| 140123  | `B-H8A63ADXX` | 1      | 66.88 M    | 0.52%     | 58.70%  | 80.51%      | A        |
+---------+---------------+--------+------------+----------+----------+-------------+----------+
| 140123  | `B-H8A63ADXX` | 2      | 65.89 M    | 0.56%     | 57.15%  | 78.32%      | A        |
+---------+---------------+--------+------------+----------+----------+-------------+----------+

* _FC id:_ Position on flowcell - Flowcell ID.
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
/proj/b2011007/INBOX/J.Lundberg_14
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

[tick]: tick.png
[cross]: cross.png