NGI is an accredited facility. However, the workflows used for this project is not under accreditation.

# Methods

{% if project.library_construction -%}
### Library construction
{{ project.library_construction }}
{%- endif %}

{% if report_info.sequencing_methods -%}
### Sequencing
{{ report_info.sequencing_methods }}
{%- endif %}

### Data Processing
To ensure that all sequenced data meets our guarantee of data quality and quantity,
a number of standardised bioinformatics quality control checks are performed before
delivery. These include checking the yield, sequence read quality and average read length.


# Sample Information
{% if not project.samples %}
No sample information to be displayed.
{% else %}
NGI ID | User ID | {{ project.samples_unit }}| Avg.read length passed
-------|---------|----------|----------
{% for sample in project.samples.values()|sort(attribute='ngi_id') -%}
{{ sample.ngi_id }} | `{{ sample.customer_name }}` | {{ sample.total_reads }}| {{ sample.read_length }}
{% endfor %}


Below you can find an explanation of the header column used in the table.

{{ tables.sample_info }}
{% endif %}


# Library Information
{% if not project.samples %}
No library information to be displayed.
{% else %}
NGI ID | Index | Lib. Prep | Avg. FS (bp) | Lib. QC
-------|-------|-------------|--------------|--------
{% for sample in project.samples.values()|sort(attribute='ngi_id') -%}
{% if sample.preps -%}
{% for prep in sample.preps.values() -%}
{{ sample.ngi_id }} | `{{ prep.barcode }}` | {{ prep.label }} |{{ prep.avg_size }} | {{ prep.qc_status }}
{% endfor -%}
{% endif -%}
{%- endfor %}


Below you can find an explanation of the header column used in the table.

{{ tables.library_info }}
{% endif %}


# Flow cell Information
{% if project.missing_fc %}
No flow cell information to be displayed.
{% else %}
Date | Flow cell | Reads (M) | N50 
-----|----------|-------|----
{% for fc in project.flowcells.values()|sort(attribute='date') -%}
{{ fc.date }} | `{{ fc.run_name }}` | {{ fc.total_reads }} | {{ fc.n50 }} 
{% endfor %}

Below you can find an explanation of the header column used in the table.

{{ tables.lanes_info }}
{% endif %}

# Flow cell-Sample Information
{% if project.missing_fc %}
No flow cell information to be displayed.
{% else %}
Date | Flow cell | Samples
-----|----------|-------
{% for fc in project.flowcells.values()|sort(attribute='date') -%}
{{ fc.date }} | `{{ fc.run_name }}` | `{{ fc.samples_run }}`
{% endfor %}

Below you can find an explanation of the header column used in the table.

{{ tables.fc_info }}
{% endif %}

# Additions to, deviations or exclusions from the accredited method(s)

None have been reported for this project.

{% if project.aborted_samples %}
# Aborted/Not Sequenced samples

NGI ID | User ID | Status
-------|---------|-------
{% for sample, info in project.aborted_samples.items() -%}
{{ sample }} | {{ info.customer_name }} | {{ info.status }}
{% endfor -%}
{% endif %}
