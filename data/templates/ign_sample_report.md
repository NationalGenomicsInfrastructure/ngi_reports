---
title: Sample Report
subtitle: M.Kaller_14_05 - P1170_101
date: 2014-11-19
header: National Genomics Infrastructure - Sample Report
footer_left: genomics_support@scilifelab.se
footer_right: M.Kaller_14_05 - P1170_101
---

# Sample Information

<table>
    <tr>
        <th>Report Date</th>
        <td>2014-11-13</td>
    </tr>
    <tr>
        <th>Recipient</th>
        <td>phil.ewels@scilifelab.se</td>
    </tr>
    <tr>
        <th>Project Name</th>
        <td>M.Kaller_14_05</td>
    </tr>
    <tr>
        <th>User Sample Name</th>
        <td>Test Sample #1290</td>
    </tr>
    <tr>
        <th>NGI Sample Name</th>
        <td>P1170_101</td>
    </tr>
    <tr>
        <th>Library Preparation Method</th>
        <td><strong>A:</strong> All samples were sequenced on HiSeq2500 (HiSeq Control Software 2.0.12.0/RTA 1.17.21.3) with a 2x101 setup.The Bcl to Fastq conversion was performed using bcl2Fastq v1.8.3 from the CASAVA software suite. The quality scale used is Sanger / phred33 / Illumina 1.8+.</td>
    </tr>
    <tr>
        <th>Sequencing Centre</th>
        <td>NGI Stockholm</td>
    </tr>
    <tr>
        <th>Sequencing Platform</th>
        <td>Illumina</td>
    </tr>
    <tr>
        <th>Reference Genome</th>
        <td><code>gatk_bundle/2.8/b37/human_g1k_v37.fasta</code></td>
    </tr>
    <tr>
        <th>Flow Cells</th>
        <td><code>140815_SN1025_0222_BC4HAPACXX</code><br><code>140815_SN1025_0223_BC4HAPACXX</code></td>
    </tr>
</table>

# Library Statistics

<table class="split_page">
        <tr>
            <td>
                <table class="td_rightalign">
                        <tr>
                            <th>Total Reads</th>
                            <td>908,585,160</td>
                        </tr>
                        <tr>
                            <th>Aligned Reads</th>
                            <td>99.47% -  903,806,933</td>
                        </tr>
                        <tr>
                            <th>Duplication Rate</th>
                            <td>1.9%</td>
                        </tr>
                        <tr>
                            <th>Median Insert Size</th>
                            <td>369 bp</td>
                        </tr>
                </table>
            </td>
            <td>
                <table class="td_rightalign">
                        <tr>
                            <th>Av. Autosomal Coverage</th>
                            <td>28.92</td>
                        </tr>
                        <tr>
                            <th>Reference with ≥ 30X Coverage</th>
                            <td>51.72%</td>
                        </tr>
                        <tr>
                            <th>GC Content</th>
                            <td>39.87%</td>
                        </tr>
                </table>
            </td>
        </tr>
</table>

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

<table class="split_page">
        <tr>
            <td>
                <table class="td_rightalign">
                        <tr>
                            <th>Change Rate</th>
                            <td>1 change per 774 bp</td>
                        </tr>
                        <tr>
                            <th>Total SNPs</th>
                            <td>4,004,647</td>
                        </tr>
                        <tr>
                            <th>Homotypic SNPs</th>
                            <td>1,491,592</td>
                        </tr>
                        <tr>
                            <th>Heterotypic SNPs</th>
                            <td>2,513,055</td>
                        </tr>
                        <tr>
                            <th>Transitions / Transversions Ratio</th>
                            <td>1.9895</td>
                        </tr>
                </table>
            </td>
            <td>
                <table class="td_rightalign">
                        <tr>
                            <th>Synonymous / Non-Synonymous</th>
                            <td>35,078 / 30,232</td>
                        </tr>
                        <tr>
                            <th>Stop Gained / Lost</th>
                            <td>273 / 58</td>
                        </tr>
                        <tr>
                            <th>Missense SNPs</th>
                            <td> 46.2%  -  30,366</td>
                        </tr>
                        <tr>
                            <th>Nonsense SNPs</th>
                            <td>0.4%  -  273</td>
                        </tr>
                        <tr>
                            <th>Silent SNPs</th>
                            <td>53.4%  -  35,078</td>
                        </tr>
                </table>
            </td>
        </tr>
</table>

Different effects can be attributed to each SNP depending on where it occurs.
Here we have used the [snpEff](http://snpeff.sourceforge.net/) tool to
categorise and count different effects. The results were plotted with an
[NGI script](https://github.com/SciLifeLab/visualizations).

![Insert Sizes](plots/snpEff_effect_regions.png)

See the `snpEff_summary.html` report in your delivery folder for more details.





