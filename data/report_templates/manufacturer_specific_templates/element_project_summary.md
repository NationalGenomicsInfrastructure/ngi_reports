
# Methods

{% if project.library_construction -%}
### Library preparation
{{ project.library_construction }}
{%- endif %}

{% if report_info.sequencing_methods -%}
### Sequencing
{{ report_info.sequencing_methods }}
{%- endif %}

### Data Processing
{% if report_info.demultiplexing_methods -%}
{{ report_info.demultiplexing_methods }}
{%- endif %}

Output FastQ files are transferred securely to [UPPMAX](http://www.uppmax.uu.se/),
where a number of standardised bioinformatics quality control checks are performed
to ensure that data meets our guarantee of data quality and quantity before delivery.

Data delivery is done via the SciLifeLab **Data Delivery System (DDS)**, from which users may download the data.

### Data Analysis
When Best Practice analysis is applicable, information about the pipeline that has been used (version etc.) can be found in the corresponding MultiQC report.

### Workflow
NGI is an accredited facility. However, the workflows used for this project is not under accreditation.

# Sample Information
{% if not project.samples %}
No sample information to be displayed.
{% else %}
NGI ID | User ID | RC | {{ project.samples_unit }} | >=Q30(%)
:-------|:---------|:----|:----------------------------|:---------
{% for sample in project.samples.values()|sort(attribute='ngi_id') -%}
{{ sample.ngi_id }} | `{{ sample.customer_name }}` | {{ sample.initial_qc.initial_qc_status }} | {{ sample.total_reads }} | {{ sample.qscore }}
{% endfor %}

Below you can find an explanation of the header column used in the table.

{{ tables.sample_info }}
{% endif %}


# Library Information
{% if not project.samples %}
No library information to be displayed.
{% else %}
NGI ID | Index | Lib. Prep | Avg. FS(bp) | Lib. QC
:-------|:-------|:-----------|:-------------|:---------
{% for sample in project.samples.values()|sort(attribute='ngi_id') -%}
{% if sample.preps -%}
{% for prep in sample.preps.values() -%}
{{ sample.ngi_id }} | `{{ prep.barcode }}` | {{ prep.label }} | {{ prep.avg_size }} | {{ prep.qc_status }}
{% endfor -%}
{% endif -%}
{%- endfor %}

Below you can find an explanation of the header column used in the table.

{{ tables.library_info }}
{% endif %}


# Lanes Information
{% if project.missing_fc %}
No lanes information to be displayed.
{% else %}
Date | Flowcell | Lane | Polonies(M) | >=Q30(%) | PhiX | Method
:-----|:----------|:------|:-------------|:----------|:------|:-------
{% for fc in project.flowcells.values()|sort(attribute='date') -%}
{% for lane in fc.lanes.values() -%}
{{ fc.date }} | `{{ fc.name }}` | {{ lane.id }} | {{ lane.total_reads_proj }} | {{ lane.weighted_avg_qval_proj }} | {{ lane.phix }} | Seq. {{ fc.seq_meth }}
{% endfor -%}
{%- endfor %}

Below you can find an explanation of the header column used in the table.

{{ tables.lanes_info }}
{% endif %}

# Additions to, deviations or exclusions from the accredited method(s)

None have been reported for this project.

{% if project.aborted_samples %}
# Aborted/Not Sequenced samples

NGI ID | User ID | Status
:-------|:---------|:-------
{% for sample, info in project.aborted_samples.items() -%}
{{ sample }} | {{ info.user_id }} | {{ info.status }}
{% endfor -%}
{% endif %}