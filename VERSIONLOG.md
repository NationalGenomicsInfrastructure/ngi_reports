# ngi_reports Version Log

## 20250403.1
Refactor entities.py by populating Sample and Prep objects in their classes instead

## 20250326.1
Refactor entities.py by populating Flowcell objects in Flowcell class instead

## 20240926.1
Fix issue with empty owner under order_details

## 20240809.1
Try fixing the extra empty line between fcs in html report

## 20240702.2
Improve method for fetching lane yield and Q30

## 20240702.1
Fix bug that the lane yield and Q30 values are inconsistent in the html and txt files

## 20240228.1
Remove GRUS and reference to NGI UPPMAX ID from report

## 20231017.1
Refactor delivery report to harmonize with project agreement

## 20230802.1
Minor refactor on NovaSeqXPlus mode in ngi_reports

## 20230609.1
Add support for NovaSeqXPlus

## 20230214.1
Fix bug that RC flag is not shown in sample_info.txt

## 20220822.2
Change URL of DDS web interface

## 20220822.1
Support DDS in project_summary

## 20220615.1
Update statusdb URL to use https

## 20220607.1
Support NextSeq 2000 P1

## 20220319.1
Refactor logic for removing sample from the aborted_samples list

## 20220318.1
Initiate total_reads as float

## 20210412.2
Also include library prep option in the report

## 20210412.1
Support the recently updated library construction methods in LIMS

## 20210319.2
Fix bug with seq_software of NextSeq2000

## 20210319.1
Setup VERSIONLOG.md
