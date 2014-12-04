---
title: Project Overview
subtitle: J.Lundeberg_14_01
date: 2014-12-02
support_email: genomics_support@scilifelab.se
---

# Project Information

User Project Name
:   140117_Rapid_Ventana_TdT

NGI Project Name
:   J.Lundeberg_14_01

NGI Project ID
:   P955

User Contact
:   [jlundberg@ki.se](mailto:jlundberg@ki.se)

NGI Application Type
:   Finished Library (No best practice analysis)

Samples &amp; Lanes
:   1 sample, 2 lanes

Project Status
:   Sequencing Finished

Order Dates
:   _Order received:_ 2014-01-10,  _Contract received:_ 2014-01-15, 
    _Samples received:_ 2014-01-20,  _Queue date:_ 2014-01-23,
    _All data delivered:_ 2014-04-02, _Report Date:_ 2014-12-02

UPPMAX Project ID
:   `b2011007`

UPPNEX project path
:   `/proj/b2011007/INBOX/J.Lundberg_14`

Reference Genome
:   Human, hg19

Minimum ordered reads
:   200 million
 
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
:   [cross] Not Swedac Accredited

Sequencing data
:   [tick] Swedac Accredited

Data flow
:   [tick] Swedac Accredited

Data processing
:   [tick] Swedac Accredited

# Sample Info

NGI ID | User ID | Index | Lib Prep
-------|---------|-------|---------
P955_101 | 140117_Rapid_Ventana_TdT | Index 8 (`ACTTGA`) | A

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