---
title: Sample Report
subtitle: {{ project.id }} - {{ sample.id }}
date: {{ report.date }}
support_email: {{ report.support_email }}
---

# Sample Information

{% if report.date %}Report Date
:   {{ report.date }}
{% endif %}{% if report.recipient %}
User Contact
:   [{{ report.recipient }}](mailto:{{ report.recipient }})
{% endif %}{% if project.id %}
Project Name
:   {{ project.id }} {% if report.group %}({{ project.group }}){% endif %}
{% endif %}{% if sample.user_sample_id %}
User Sample Name
:   {{ sample.user_sample_id }}
{% endif %}{% if sample.id %}
NGI Sample Name
:   {{ sample.id }}
{% endif %}{% if project.UPPMAXid %}
UPPMAX Project ID
:   `{{ project.UPPMAXid }}`
{% endif %}{% if project.sequencing_platform %}
Sequencing Platform
:   {{ project.sequencing_platform }}
{% endif %}{% if project.prep %}
Library Prep Method
:   {{ project.prep }}
{% endif %}{% if project.sequencing_centre %}
Sequencing Centre
:   {{ project.sequencing_centre }}
{% endif %}{% if project.ref_genome %}
Reference Genome
:   `{{ project.ref_genome }}`
{% endif %}{% if sample.barcode %}
Pooling Reagent
:   `{{ sample.barcode }}`
{% endif %}{% if sample.flowcells %}
Flow Cells
:   {% for fc in sample.flowcells %}`{{ fc.id }}`

    {% endfor %}
{% endif %}

{% if sample.automsomal_coverage %}
# Library Statistics

Total Reads
:   {{ sample.total_reads }}

Aligned Reads
:   {{ sample.percent_aligned }} - {{ sample.aligned_reads }}
{% if sample.duplication_rate %}
Duplication Rate
:   {{ sample.duplication_rate }}
{% endif %}
Median Insert Size
:   {{ sample.median_insert_size }} bp

Av. Autosomal Coverage
:   {{ sample.automsomal_coverage }}X

&ge; 30X Coverage
:   {{ sample.ref_above_30X }} of reference

GC Content
:   {{ sample.percent_gc }}

See below for more information about coverage and insert size. The
`qualimapReport.html` report in your delivery folder contains additional library
statistics.
{% if sample.duplication_rate %}Note that the duplication rate above is calculated using
[Picard Mark Duplicates](http://broadinstitute.github.io/picard/command-line-overview.html#MarkDuplicates).
Qualimap calculates duplicates differently and the figure in
the report will be different to the Picard result..
{% endif %}

## Distribution of sequencing coverage
Calculating the coverage of a genome tells you how much information you have
about the sequence content of any given position. More coverage means more data
and so greater confidence in your results. A specific locus with 30X coverage
will have 30 unique reads covering that location. Different positions in the
genome may have different coverages due to variations in how well reads map to
the underlying sequence. Other factors such as GC bias in library preparation
may also have an effect.

To calculate the plot below, we create rolling windows across the genome and
count the frequencies of the different coverages observed. This was done using
the [QualiMap](http://qualimap.bioinfo.cipf.es/) tool and plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![Sequencing Coverage]({{ plots.coverage_plot }})\


## Proportion of library with increasing coverage depths
Another way to assess coverage is to look at the proportion of the reference
genome with a certain coverage. The plot below shows what percentage of the
reference genome is covered with increasing coverage thresholds. As above, this
data was calculated using [QualiMap](http://qualimap.bioinfo.cipf.es/) and plotted
with an [NGI script](https://github.com/SciLifeLab/visualizations).

![Genome Fractional Coverage]({{ plots.cov_frac_plot }})\


## Library fragment insert sizes
By inspecting where each read pair maps to in the reference genome, we can
reconstruct the reads that were present in the library and calculate the range
of insert sizes. This gives an insight into the quality of the sequencing
library. We counted how many reads with each insert size were seen and plotted
this in the histogram below. This was done using the
[QualiMap](http://qualimap.bioinfo.cipf.es/) tool and plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![Insert Sizes]({{ plots.insert_size_plot }})\


## Distribution of reads by GC content
Library preparation and sequencing alignment can be affected by differences in
GC content. Here, we plot the proportions of the library reads at each GC
content. The red dotted line shows the profile for the reference genome.
This data was calculated using [QualiMap](http://qualimap.bioinfo.cipf.es/)
and plotted with an [NGI script](https://github.com/SciLifeLab/visualizations).

![GC Content Distribution]({{ plots.gc_dist_plot }})\

{% endif %}

{% if sample.snpeff %}
# Variants
{% if sample.snpeff.change_rate %}
Change Rate
:   {{ sample.snpeff.change_rate }}
{% endif %}{% if sample.snpeff.total_snps %}
Total SNPs
:   {{ sample.snpeff.total_snps }}
{% endif %}{% if sample.snpeff.homotypic_snps %}
Homotypic SNPs
:   {{ sample.snpeff.homotypic_snps }}
{% endif %}{% if sample.snpeff.heterotypic_snps %}
Heterotypic SNPs
:   {{ sample.snpeff.heterotypic_snps }}
{% endif %}{% if sample.snpeff.TsTv_ratio %}
Ts/Tv Ratio
:   {{ sample.snpeff.TsTv_ratio }}
{% endif %}{% if sample.snpeff.synonymous_SNPs %}
Synonymous SNPs
:   {{ sample.snpeff.synonymous_SNPs }}
{% endif %}{% if sample.snpeff.nonsynonymous_SNPs %}
Non-Synonymous SNPs
:   {{ sample.snpeff.nonsynonymous_SNPs }}
{% endif %}{% if sample.snpeff.stops_gained and sample.snpeff.stops_lost %}
Stop Gained / Lost
:   {{ sample.snpeff.stops_gained }} / {{ sample.snpeff.stops_lost }}
{% endif %}{% if sample.snpeff.percent_missense_SNPs and sample.snpeff.missense_SNPs %}
Missense SNPs
:   {{ sample.snpeff.percent_missense_SNPs }}  -   {{ sample.snpeff.missense_SNPs }}
{% endif %}{% if sample.snpeff.percent_nonsense_SNPs and sample.snpeff.nonsense_SNPs %}
Nonsense SNPs
:   {{ sample.snpeff.percent_nonsense_SNPs }}  -   {{ sample.snpeff.nonsense_SNPs }}
{% endif %}{% if sample.snpeff.percent_silent_SNPs and sample.snpeff.silent_SNPs %}
Silent SNPs
:   {{ sample.snpeff.percent_silent_SNPs }}  -   {{ sample.snpeff.silent_SNPs }}
{% endif %}
Different effects can be attributed to each SNP depending on where it occurs.
Here we have used the [snpEff](http://snpeff.sourceforge.net/) tool to
categorise and count different effects. The results were plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![snpEff - Effect Regions]({{ plots.snpEFf_plot }})\

See the `snpEff_summary.html` report in your delivery folder for more details.

{% endif %}
