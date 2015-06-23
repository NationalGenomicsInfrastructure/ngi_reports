
#!/usr/bin/env python

""" Main module for dealing with fields for the IGN Sample Report
"""

import csv
import collections
import jinja2
import os
import re
from datetime import datetime
import re

import ngi_reports.common
from ngi_visualizations.qualimap import coverage_histogram, genome_fraction_coverage, insert_size, gc_distribution
from ngi_visualizations.snpEff import snpEff_plots

class CommonReport(ngi_reports.common.BaseReport):

    def __init__(self, config, LOG, working_dir, **kwargs):

        # Initialise the parent class
        super(CommonReport, self).__init__(config, LOG, working_dir, **kwargs)

        # Initialise empty dictionaries
        self.info = {}
        self.project = {}
        self.samples = {}
        self.plots = {}

        # Scrape information from the filesystem
        # This function is in the common BaseReport class in __init__.py
        xml = self.parse_piper_xml()
        self.project = xml['project']
        self.samples = {k:v for k,v in xml['samples'].items() \
            if not kwargs.get('samples') or v['id'] in kwargs.get('samples')}

        # Self-sufficient Fields
        self.report_dir = os.path.join('delivery', 'reports')
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        self.info['support_email'] = config.get('ngi_reports', 'support_email')
        self.info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.project['sequencing_centre'] = 'NGI {}'.format(self.ngi_node.title())

        # Sanity check - make sure that we have some samples
        if len(self.samples) == 0:
            raise IOError ('No samples found!')

        # Get more info from the filesystem
        self.LOG.debug('Parsing QC files')
        self.parse_qualimap()
        self.parse_snpeff()
        self.parse_picard_metrics()

        self.create_aggregate_statistics()

        self.LOG.debug('Plotting graphs')
        self.make_plots()




    def parse_qualimap(self):
        """ Looks for qualimap results files and adds to class
        """
        for sample_id in self.samples.iterkeys():
            # Build the expected filenames
            qualimap_data_dir = os.path.join(self.working_dir, '06_final_alignment_qc',
                '{}.clean.dedup.recal.qc'.format(sample_id))
            genome_results = os.path.join(qualimap_data_dir, 'genome_results.txt')
            qualimap_report = os.path.join(qualimap_data_dir, 'qualimapReport.html')
            try:
                cov_per_contig = False
                autosomal_cov_length = 0
                autosomal_cov_bases = 0
                with open(os.path.realpath(genome_results), 'r') as fh:
                    for line in fh:
                        line = line.strip()

                        def get_after_equals(s):
                            return s.split("=", 1)[1].strip()

                        # number of reads = 908,585,160
                        if line[:17] == 'number of reads =':
                            self.samples[sample_id]['total_reads'] = get_after_equals(line)

                        # number of mapped reads = 903,806,933 (99.47%)
                        if line[:24] == 'number of mapped reads =':
                            pattern = re.compile(".*=(.*)\s\((.*)\)")
                            self.samples[sample_id]['percent_aligned'] = pattern.match(line).group(2).strip()
                            self.samples[sample_id]['aligned_reads'] = pattern.match(line).group(1).strip()

                        # GC percentage = 39.87%
                        if line[:15] == 'GC percentage =':
                            self.samples[sample_id]['percent_gc'] = get_after_equals(line)

                        # mean coverageData = 29.04X
                        if line[:19] == 'mean coverageData =':
                            self.samples[sample_id]['mean_coverage'] = get_after_equals(line)

                        # There is a 51.72% of reference with a coverageData >= 30X
                        if line[-39:] == 'of reference with a coverageData >= 30X':
                            self.samples[sample_id]['ref_above_30X'] = line[11:17]

                        # >>>>>>> Coverage per contig
                        if line == '>>>>>>> Coverage per contig':
                            cov_per_contig = True
                        elif line[:7] == '>>>>>>>':
                            cov_per_contig = False
                        if cov_per_contig and line:
                            sections = line.split()
                            if sections[0].isdigit() and int(sections[0]) <= 22:
                                autosomal_cov_length += float(sections[1])
                                autosomal_cov_bases += float(sections[2])

                if autosomal_cov_length > 0 and autosomal_cov_bases > 0:
                    autosomal_cov = autosomal_cov_bases / autosomal_cov_length
                    self.samples[sample_id]['automsomal_coverage'] = '{:.2f}'.format(autosomal_cov)


                # Why is this not in the text file? This makes me a sad panda.
                with open(os.path.realpath(qualimap_report), 'r') as fh:
                    for line in fh:
                        line = line.strip()

                        # <td class=column1>P25/Median/P75</td>
                        # <td class=column2>318 / 369 / 422</td>
                        if line == '<td class=column1>P25/Median/P75</td>':
                            line = next(fh)
                            quartiles = line[18:-5].split('/',3)
                            self.samples[sample_id]['median_insert_size'] = quartiles[1].strip()

            except Exception as e:
                self.LOG.error("Something went wrong with parsing the Qualimap results for sample {}:\n{}".format(sample_id, e))





    def parse_snpeff(self):
        """ Parse the snpEff output to get information about SNPs
        """

        for sample_id in self.samples.iterkeys():

            snpEff = {}
            # Build the expected filenames
            snpEff_csv = os.path.realpath(os.path.join(self.working_dir, '07_variant_calls',
                '{}.clean.dedup.recal.bam.raw.annotated.vcf.snpEff.summary.csv'.format(sample_id)))
            try:
                synonymous_SNPs = 0
                nonsynonymous_SNPs = 0

                with open(os.path.realpath(snpEff_csv), 'r') as fh:
                    for line in fh:
                        line = line.strip()

                        if line[:33] == 'Number_of_variants_before_filter,':
                            snpEff['total_snps'] = '{:,}'.format(int(line[34:]))

                        if line[:13] == 'Change_rate ,':
                            snpEff['change_rate'] = '1 change per {:,} bp'.format(int(line[14:]))

                        if line[:5] == 'Het ,':
                            snpEff['heterotypic_snps'] = '{:,}'.format(int(line[6:]))

                        if line[:5] == 'Hom ,':
                            snpEff['homotypic_snps'] = '{:,}'.format(int(line[6:]))

                        if line[:10] == 'MISSENSE ,':
                            sections = line.split(',')
                            pc = sections[2].strip()
                            pc = float(pc[:-1])
                            snpEff['percent_missense_SNPs'] = '{:.1f}%'.format(pc)
                            snpEff['missense_SNPs'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:10] == 'NONSENSE ,':
                            sections = line.split(',')
                            pc = sections[2].strip()
                            pc = float(pc[:-1])
                            snpEff['percent_nonsense_SNPs'] = '{:.1f}%'.format(pc)
                            snpEff['nonsense_SNPs'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:8] == 'SILENT ,':
                            sections = line.split(',')
                            pc = sections[2].strip()
                            pc = float(pc[:-1])
                            snpEff['percent_silent_SNPs'] = '{:.1f}%'.format(pc)
                            snpEff['silent_SNPs'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:20] == 'synonymous_variant ,':
                            sections = line.split(',')
                            synonymous_SNPs += int(sections[1].strip())

                        if line[:13] == 'stop_gained ,':
                            sections = line.split(',')
                            snpEff['stops_gained'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:11] == 'stop_lost ,':
                            sections = line.split(',')
                            snpEff['stops_lost'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:13] == 'Ts_Tv_ratio ,':
                            snpEff['TsTv_ratio'] = '{:.3f}'.format(float(line[14:]))


                        # ALTERNATIVE BLOCKS FOR OLDER VERSION OF SNPEFF
                        # Type, Total, Homo, Hetero
                        # SNP , 4004647 , 1491592 , 2513055
                        if line[:5] == 'SNP ,':
                            sections = line.split(',')
                            snpEff['homotypic_snps'] = '{:,}'.format(int(sections[2].strip()))
                            snpEff['heterotypic_snps'] = '{:,}'.format(int(sections[3].strip()))

                        if line[:10] == 'SYNONYMOUS':
                            sections = line.split(',')
                            synonymous_SNPs += int(sections[1].strip())

                        if line[:14] == 'NON_SYNONYMOUS':
                            sections = line.split(',')
                            nonsynonymous_SNPs += int(sections[1].strip())

                        if line[:13] == 'STOP_GAINED ,':
                            sections = line.split(',')
                            snpEff['stops_gained'] = '{:,}'.format(int(sections[1].strip()))

                        if line[:11] == 'STOP_LOST ,':
                            sections = line.split(',')
                            snpEff['stops_lost'] = '{:,}'.format(int(sections[1].strip()))


            except:
                self.LOG.error("Something went wrong with parsing the snpEff results for sample {}, {}".format(sample_id, snpEff_csv))

            if synonymous_SNPs > 0:
                snpEff['synonymous_SNPs'] = '{:,}'.format(synonymous_SNPs)
            if nonsynonymous_SNPs > 0:
                snpEff['nonsynonymous_SNPs'] = '{:,}'.format(nonsynonymous_SNPs)

            self.samples[sample_id]['snpeff'] = snpEff



    def parse_picard_metrics(self):
        """ Parse the picard metrics file to get the duplication rates
        """
        for sample_id in self.samples.iterkeys():

            # Build the expected filenames
            picard_metrics_fn = os.path.realpath(os.path.join(self.working_dir,
                '05_processed_alignments', '{}.metrics'.format(sample_id)))
            try:
                with open(os.path.realpath(picard_metrics_fn), 'r') as fh:
                    nextLine = False
                    for line in fh:
                        line = line.strip()
                        if nextLine is True:
                            parts = line.split("\t")
                            percentDup = float(parts[7]) * 100
                            self.samples[sample_id]['duplication_rate'] = '{:.2f}%'.format(percentDup)
                            nextLine = False
                        if line == 'LIBRARY	UNPAIRED_READS_EXAMINED	READ_PAIRS_EXAMINED	UNMAPPED_READS	UNPAIRED_READ_DUPLICATES	READ_PAIR_DUPLICATES	READ_PAIR_OPTICAL_DUPLICATES	PERCENT_DUPLICATION	ESTIMATED_LIBRARY_SIZE':
                            nextLine = True

            except IOError:
                self.LOG.warning("Warning: Could not find Picard metrics file for {}".format(sample_id))
            except:
                self.LOG.error("Something went wrong with parsing the picard metrics file")



    # Create CSV files with aggregate stats for samples
    def create_aggregate_statistics (self):

        def create_header (samples):
            # take the union of all keys for the header row
            return sorted(
                list(
                    set(
                        [key \
                        for sample in samples.values() \
                        for key in sample.keys()])))

        def create_rows (samples):
            for sample in samples.keys():
                yield samples[sample]

        output_fn = "{}_aggregate_report.csv".format(self.project['id'])
        output_file = os.path.realpath(os.path.join(self.report_dir, output_fn))

        # Flatten out the dict to make it writable as a csv
        flattened_samples = {}
        for sample in self.samples:
            flattened = self.flatten_dict(self.samples[sample])
            flattened_samples[sample] = collections.OrderedDict(flattened)

        # Parse out the data
        header = create_header(flattened_samples)
        rows = create_rows(flattened_samples)

        self.LOG.debug("Writing aggregate report to: " + output_file)

        # Drop it to a csv
        with open(output_file, 'wb') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=header,
                delimiter="\t")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    # Plot the parsed data for the reports
    def make_plots(self):
        """ Plot the visualizations for the IGN sample report
        """
        for sample_id in self.samples.iterkeys():

            # Avoid crashing the entire package for all samples if some files not found
            try:

                # Create plots sample dict
                self.plots[sample_id] = {}

                # Create the plots subdirectory
                plots_dir_rel = os.path.join('plots', sample_id)
                plots_dir = os.path.realpath(os.path.join(self.report_dir, plots_dir_rel))
                if not os.path.exists(plots_dir):
                    os.makedirs(plots_dir)

                # Work out source directories
                qualimap_raw_dir = os.path.realpath(os.path.join(self.working_dir, '06_final_alignment_qc',
                    '{}.clean.dedup.recal.qc'.format(sample_id), 'raw_data_qualimapReport'))
                snpeff_data_dir = os.path.realpath(os.path.join(self.working_dir, '07_variant_calls'))

                # Qualimap coverage plot
                cov_fn = os.path.realpath(os.path.join(qualimap_raw_dir, 'coverage_histogram.txt'))
                cov_output_rel = os.path.join(plots_dir_rel, '{}_coverage'.format(sample_id))
                cov_output = os.path.join(plots_dir, '{}_coverage'.format(sample_id))
                coverage_histogram.plot_coverage_histogram(cov_fn, cov_output)
                self.plots[sample_id]['coverage_plot'] = cov_output_rel

                # Qualimap genome fraction coverage plot
                cov_frac_fn = os.path.realpath(os.path.join(qualimap_raw_dir, 'genome_fraction_coverage.txt'))
                cov_frac_output_rel = os.path.join(plots_dir_rel, '{}_genome_fraction'.format(sample_id))
                cov_frac_output = os.path.join(plots_dir, '{}_genome_fraction'.format(sample_id))
                genome_fraction_coverage.plot_genome_fraction_coverage(cov_frac_fn, cov_frac_output)
                self.plots[sample_id]['cov_frac_plot'] = cov_frac_output_rel

                # Qualimap insert size plot
                insert_size_fn = os.path.realpath(os.path.join(qualimap_raw_dir, 'insert_size_histogram.txt'))
                insert_size_output_rel = os.path.join(plots_dir_rel, '{}_insert_size'.format(sample_id))
                insert_size_output = os.path.join(plots_dir, '{}_insert_size'.format(sample_id))
                insert_size.plot_insert_size_histogram(insert_size_fn, insert_size_output)
                self.plots[sample_id]['insert_size_plot'] = insert_size_output_rel

                # Qualimap GC distribution plot
                gc_fn = os.path.realpath(os.path.join(qualimap_raw_dir, 'mapped_reads_gc-content_distribution.txt'))
                gc_output_rel = os.path.join(plots_dir_rel, '{}_gc_distribution'.format(sample_id))
                gc_output = os.path.join(plots_dir, '{}_gc_distribution'.format(sample_id))
                gc_distribution.plot_genome_fraction_coverage(gc_fn, gc_output)
                self.plots[sample_id]['gc_dist_plot'] = gc_output_rel

                # snpEff plot
                snpEFf_fn = os.path.realpath(os.path.join(snpeff_data_dir, '{}.clean.dedup.recal.bam.raw.annotated.vcf.snpEff.summary.csv'.format(sample_id)))
                snpEFf_output_rel = os.path.join(plots_dir_rel, '{}_snpEff_effect'.format(sample_id))
                snpEFf_output = os.path.join(plots_dir, '{}_snpEff_effect'.format(sample_id))
                snpEff_plots.plot_snpEff(snpEFf_fn, snpEFf_output)
                self.plots[sample_id]['snpEFf_plot'] = '{}_regions'.format(snpEFf_output_rel)

            except IOError:
                self.LOG.error('Error whilst plotting {} - skipping sample..'.format(sample_id))







    def check_project_fields(self):
        """ Check that the object has all required fields. Returns True / False.
        """
        missing_fields = []
        report_fields = []
        project_fields = ['id', 'sequencing_centre', 'sequencing_platform', 'ref_genome']

        for f in report_fields:
            if f not in self.info:
                missing_fields.append(f)
        for f in project_fields:
            if f not in self.project:
                missing_fields.append(f)
        if len(missing_fields) > 0:
            self.LOG.error('Mandatory project-level field(s) missing: {}'.format(", ".join(missing_fields)))
            return False
        return True

    def check_sample_fields(self, sample_id):
        """ Check that the object has all required fields. Returns True / False.
        """
        missing_fields = []
        sample_fields = ['total_reads',  'percent_aligned', 'aligned_reads', 'median_insert_size',
            'automsomal_coverage', 'ref_above_30X', 'percent_gc']
        plot_fields = ['coverage_plot', 'cov_frac_plot', 'insert_size_plot', 'gc_dist_plot', 'snpEFf_plot']

        for f in sample_fields:
            if f not in self.samples[sample_id]:
                missing_fields.append(f)
        for f in plot_fields:
            if f not in self.plots[sample_id]:
                missing_fields.append(f)
        if len(missing_fields) > 0:
            self.LOG.error('Mandatory sample-level field(s) missing for {}: {}'.format(sample_id, ", ".join(missing_fields)))
            return False
        return True



    # Return the parsed markdown
    def parse_template(self, template):

        output_mds = {}

        self.LOG.debug('Processing reports')

        # Check that we have mandatory project-level fields
        if not self.check_project_fields():
            self.LOG.error("Missing mandatory project-level fields, exiting..")
            raise KeyError

        # Go through each sample making the report
        for sample_id, sample in sorted(self.samples.iteritems()):

            self.LOG.debug("Generating report for {}".format(sample_id))

            # Make the file basename
            report_fn = sample_id + '_ign_sample_report'
            output_bn = os.path.realpath(os.path.join(self.working_dir, self.report_dir, report_fn))

            # check that we have everything (errors thrown by def)
            if not self.check_sample_fields(sample_id):
                continue

            # Parse the template
            try:
                md = template.render(report=self.info, project=self.project, sample=sample, plots=self.plots[sample_id])
                output_mds[output_bn] = md
            except:
                self.LOG.error('Could not parse the ign_sample_report template for sample {} - skipping'.format(sample_id))
                continue

        return output_mds
