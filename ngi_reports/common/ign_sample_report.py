#!/usr/bin/env python

""" Main module for dealing with fields for the IGN Sample Report
"""

import os
import re
from datetime import datetime

class CommonReport(object):
    
    def __init__(self, config, LOG, working_dir):
        
        # Incoming handles
        self.config = config
        self.LOG = LOG
        self.working_dir = working_dir
    
        # Setup
        ngi_node = config.get('ngi_reports', 'ngi_node')
    
        # Initialise empty dictionaries
        self.info = {}
        self.project = {}
        self.sample = {}
    
        # Project Fields
        self.project['id'] = 'M.Kaller_14_05'
        self.project['group'] = 'FUBAR'
        self.project['user_sample_id'] = 'FUBAR'
        self.project['UPPMAXid'] = 'FUBAR'
        self.project['sequencing_centre'] = 'NGI {}'.format(ngi_node.title())
        
        self.sample['duplication_rate'] = 'FUBAR'        
        
        # Sample Fields
        self.sample['id'] = 'P1170_101'
        self.sample['sequencing_platform'] = 'FUBAR'
        self.sample['user_sample_id'] = 'FUBAR'
        self.sample['ref_genome'] = 'FUBAR'

        self.sample['snpeff'] = {}
        self.sample['snpeff']['change_rate'] = 'FUBAR'
        self.sample['snpeff']['total_snps'] = 'FUBAR'
        self.sample['snpeff']['homotypic_snps'] = 'FUBAR'
        self.sample['snpeff']['heterotypic_snps'] = 'FUBAR'
        self.sample['snpeff']['TsTv_ratio'] = 'FUBAR'
        self.sample['snpeff']['synonymous_SNPs'] = 'FUBAR'
        self.sample['snpeff']['nonsynonymous_SNPs'] = 'FUBAR'
        self.sample['snpeff']['stops_gained'] = 'FUBAR'
        self.sample['snpeff']['stops_lost'] = 'FUBAR'
        self.sample['snpeff']['percent_missense_SNPs'] = 'FUBAR'
        self.sample['snpeff']['missense_SNPs'] = 'FUBAR'
        self.sample['snpeff']['percent_nonsense_SNPs'] = 'FUBAR'
        self.sample['snpeff']['nonsense_SNPs'] = 'FUBAR'
        self.sample['snpeff']['percent_silent_SNPs'] = 'FUBAR'
        self.sample['snpeff']['silent_SNPs'] = 'FUBAR'
        self.sample['preps'] = [{'label': 'FUBAR', 'description': 'FUBAR'}]
        self.sample['flowcells'] = [{'id': 'FUBAR'}]
        
        # Scrape information from the filesystem
        self.parse_qualimap()
        
        
        
        # Report Fields
        self.info['support_email'] = config.get('ngi_reports', 'support_email')
        self.info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.info['recipient'] = 'FUBAR'
        self.report_fn = self.sample['id'] + '_ign_sample_report.md'


    def parse_qualimap(self):
        """ Looks for qualimap results files and adds to class
        """
        # Build the expected filenames
        qualimap_dirname = self.sample['id']+'.clean.dedup.recal.qc'
        data_dir = os.path.join(self.working_dir, 'quality_control', qualimap_dirname)
        genome_results = os.path.join(data_dir, 'genome_results.txt')
        qualimap_report = os.path.join(data_dir, 'qualimapReport.html')
        try:
            cov_per_contig = False
            autosomal_cov_length = 0
            autosomal_cov_bases = 0
            with open(os.path.realpath(genome_results), 'r') as fh:
                for line in fh:
                    line = line.strip()
                    
                    # number of reads = 908,585,160
                    if line[:17] == 'number of reads =':
                        self.sample['total_reads'] = line[18:]
                    
                    # number of mapped reads = 903,806,933 (99.47%)
                    if line[:24] == 'number of mapped reads =':
                        self.sample['percent_aligned'] = line[-7:-1]
                        self.sample['aligned_reads'] = line[25:-9]
                        
                    # GC percentage = 39.87%
                    if line[:15] == 'GC percentage =':
                        self.sample['percent_gc'] = line[-6:]
                    
                    # mean coverageData = 29.04X
                    if line[:19] == 'mean coverageData =':
                        self.sample['mean_coverage'] = line[20:-1]
                    
                    # There is a 51.72% of reference with a coverageData >= 30X
                    if line[-39:] == 'of reference with a coverageData >= 30X':
                        self.sample['ref_above_30X'] = line[11:17]
                    
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
                self.sample['automsomal_coverage'] = '{:.2f}'.format(autosomal_cov)
            
            
            # Why is this not in the text file? I'm a sad panda.
            with open(os.path.realpath(qualimap_report), 'r') as fh:
                for line in fh:
                    line = line.strip()
                    
                    # <td class=column1>P25/Median/P75</td>
                    # <td class=column2>318 / 369 / 422</td>
                    if line == '<td class=column1>P25/Median/P75</td>':
                        line = next(fh)
                        quartiles = line[18:-5].split('/',3)
                        self.sample['median_insert_size'] = quartiles[1].strip()
                        
        except:
            self.LOG.error("Something went wrong with parsing the Qualimap results")
            raise


    def check_fields(self):
        """ Check that the object has all required fields. Returns True / False.
        """
        report_fields = ['recipient']
        project_fields = ['id', 'UPPMAXid', 'sequencing_centre']
        sample_fields = ['id', 'sequencing_platform', 'user_sample_id', 
            'ref_genome', 'total_reads', 'percent_aligned', 'aligned_reads', 
            'duplication_rate', 'median_insert_size', 'automsomal_coverage',
            'ref_above_30X', 'percent_gc']

        for f in report_fields:
            if f not in self.info.keys():
                return False

        for f in project_fields:
            if f not in self.project.keys():
                return False

        for f in sample_fields:
            if f not in self.sample.keys():
                return False

        return True

