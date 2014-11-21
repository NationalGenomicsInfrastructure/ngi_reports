---
title: Sample Report
subtitle: {{ project.id }} - {{ sample.id }}
date: {{ report.date }}
support_email: genomics_support@scilifelab.se
---

# Sample Information

Report Date
:  {{ report.date }}

Recipient
:   {{ report.recipient }}

Project Name
:   {{ project.id }}

User Sample Name
:   {{ sample.user_id }}

NGI Sample Name
:   {{ sample.id }}

Library Preparation Method
:   {% for prep in sample.preps %}**{{ prep.label }}:** {{ prep.description }}
    
    {% endblock %}

Sequencing Centre
:   {{ project.sequencing_centre }}

Sequencing Platform
:   {{ sample.sequencing_platform }}

Reference Genome
:   ` {{ sample.ref_genome }}`

Flow Cells
:   {% for fc in sample.flowcells %}`{{ fc.id }}`
    
    {% endblock %}


# Library Statistics

Total Reads
:   {{ sample.total_reads }}

Aligned Reads
:  {{ sample.percent_aligned }} -  {{ sample.aligned_reads }}

Duplication Rate
:   {{ sample.duplication_rate }}

Median Insert Size
:   {{ sample.median_insert_size }}

Av. Autosomal Coverage
:  {{ sample.automsomal_coverage }}

Reference with at least 30X Coverage
:   {{ sample.ref_above_30X }}

GC Content
:   {{ sample.percent_gc }}

See below for more information about coverage and insert size. The
`qualimapReport.html` report in your delivery folder contains additional library
statistics. Note that the duplication rate above is calculated using
[Picard Mark Duplicates](http://broadinstitute.github.io/picard/command-line-overview.html#MarkDuplicates).
Qualimap calculates duplicates differently and the figure in
the report will be different to the Picard result..

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

![Sequencing Coverage](plots/qualimap_coverage.png)

## Proportion of library with increasing coverage depths
Another way to assess coverage is to look at the proportion of the reference
genome with a certain coverage. The plot below shows what percentage of the
reference genome is covered with increasing coverage thresholds. As above, this
data was calculated using [QualiMap](http://qualimap.bioinfo.cipf.es/) and plotted
with an [NGI script](https://github.com/SciLifeLab/visualizations).

![Genome Fractional Coverage](plots/genome_fraction.png)

## Library fragment insert sizes
By inspecting where each read pair maps to in the reference genome, we can
reconstruct the reads that were present in the library and calculate the range
of insert sizes. This gives an insight into the quality of the sequencing
library. We counted how many reads with each insert size were seen and plotted
this in the histogram below. This was done using the
[QualiMap](http://qualimap.bioinfo.cipf.es/) tool and plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![Insert Sizes](plots/qualimap_insertsize.png)

## Distribution of reads by GC content
Library preparation and sequencing alignment can be affected by differences in
GC content. Here, we plot the proportions of the library reads at each GC
content. The red dotted line shows the profile for the reference genome. 
This data was calculated using [QualiMap](http://qualimap.bioinfo.cipf.es/)
and plotted with an [NGI script](https://github.com/SciLifeLab/visualizations).

![GC Content Distribution](plots/gc_distribution.png)

# Variants

Change Rate
:   {{ sample.snpeff.change_rate }}

Total SNPs
:    {{ sample.snpeff.total_snps }}

Homotypic SNPs
:    {{ sample.snpeff.homotypic_snps }}

Heterotypic SNPs
:    {{ sample.snpeff.heterotypic_snps }}

Transitions / Transversions Ratio
:    {{ sample.snpeff.TsTv_ratio }}

Synonymous / Non-Synonymous
:    {{ sample.snpeff.synonymous_SNPs }} / {{ sample.snpeff.nonsynonymous_SNPs }} 

Stop Gained / Lost
:   {{ sample.snpeff.stops_gained }} / {{ sample.snpeff.stops_lost }}

Missense SNPs
:    {{ sample.snpeff.percent_missense_SNPs }}  -   {{ sample.snpeff.missense_SNPs }}

Nonsense SNPs
:    {{ sample.snpeff.percent_nonsense_SNPs }}  -   {{ sample.snpeff.nonsense_SNPs }}

Silent SNPs
:    {{ sample.snpeff.percent_silent_SNPs }}  -   {{ sample.snpeff.silent_SNPs }}

Different effects can be attributed to each SNP depending on where it occurs.
Here we have used the [snpEff](http://snpeff.sourceforge.net/) tool to
categorise and count different effects. The results were plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![Insert Sizes](plots/snpEff_effect_regions.png)

See the `snpEff_summary.html` report in your delivery folder for more details.





