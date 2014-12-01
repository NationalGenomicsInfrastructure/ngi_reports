#!/usr/bin/env python

""" Main module for dealing with fields for the IGN Sample Report
"""

import jinja2
import os
import re
import xmltodict
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
        self.project['group'] = 'FUBAR'
        self.project['user_sample_id'] = 'FUBAR'
        self.project['sequencing_centre'] = 'NGI {}'.format(ngi_node.title())
        
        self.sample['duplication_rate'] = 'FUBAR'        
        
        # Sample Fields
        self.sample['user_sample_id'] = 'FUBAR'
        self.sample['preps'] = [{'label': 'A', 'description': 'FUBAR'}]
        self.sample['flowcells'] = [{'id': 'FUBAR'}]
        
        # Scrape information from the filesystem
        self.parse_setup_xml()
        self.parse_qualimap()
        self.parse_snpeff()
        
        # Report Fields
        self.info['support_email'] = config.get('ngi_reports', 'support_email')
        self.info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.info['recipient'] = 'FUBAR'
        self.report_dir = os.path.join('delivery', 'reports')
        self.report_fn = self.sample['id'] + '_ign_sample_report'


    def parse_setup_xml(self):
        """ Parses the XML setup file that Piper uses
        """
        xml_fn = os.path.join(self.working_dir, 'project_setup_output_file.xml')
        try:
            with open(os.path.realpath(xml_fn)) as fh:
                run = xmltodict.parse(fh)
        except IOError as e:
            raise IOError("Could not open configuration file \"{}\".".format(xml_fn))
        
        run = run['project']        
        try:
            self.project['id'] = run['metadata']['name']
            self.project['UPPMAXid'] = run['metadata']['uppmaxprojectid']
            self.sample['sequencing_platform'] = run['metadata']['platform']
            self.sample['ref_genome'] = os.path.basename(run['metadata']['reference'])
            self.sample['id'] = run['inputs']['sample']['samplename']
        except KeyError:
            self.LOG.warning('Could not find key in sample XML file')
            pass
        
    
    def parse_qualimap(self):
        """ Looks for qualimap results files and adds to class
        """
        # Build the expected filenames
        qualimap_dirname = self.sample['id']+'.clean.dedup.recal.qc'
        data_dir = os.path.join(self.working_dir, 'delivery', 'quality_control', qualimap_dirname)
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
            
    
    def parse_snpeff(self):
        """ Parse the snpEff output to get information about SNPs
        """
        snpEff = {}
        # Build the expected filenames
        snpEff_csv = os.path.join(self.working_dir, 'snpEff_output', 'snpEff_summary.csv')
        try:
            synonymous_SNPs = 0
            nonsynonymous_SNPs = 0
            
            with open(os.path.realpath(snpEff_csv), 'r') as fh:
                for line in fh:
                    line = line.strip()
                    
                    # Number_of_variants_before_filter, 4004647
                    if line[:33] == 'Number_of_variants_before_filter,':
                        snpEff['total_snps'] = '{:,}'.format(int(line[34:]))
                    
                    # Number_of_variants_before_filter, 4004647
                    if line[:13] == 'Change_rate ,':
                        snpEff['change_rate'] = '1 change per {:,} bp'.format(int(line[14:]))
                    
                    # Type, Total, Homo, Hetero
                    # SNP , 4004647 , 1491592 , 2513055
                    if line[:5] == 'SNP ,':
                        sections = line.split(',')
                        snpEff['homotypic_snps'] = '{:,}'.format(int(sections[2].strip()))
                        snpEff['heterotypic_snps'] = '{:,}'.format(int(sections[3].strip()))
                    
                    # Type , Count , Percent 
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
                    
                    # Ts_Tv_ratio , 1.989511
                    if line[:13] == 'Ts_Tv_ratio ,':
                        snpEff['TsTv_ratio'] = '{:.3f}'.format(float(line[14:]))

        except:
            self.LOG.error("Something went wrong with parsing the snpEff results")
            raise
        
        if synonymous_SNPs > 0:
            snpEff['synonymous_SNPs'] = '{:,}'.format(synonymous_SNPs)
        if nonsynonymous_SNPs > 0:
            snpEff['nonsynonymous_SNPs'] = '{:,}'.format(nonsynonymous_SNPs)

        self.sample['snpeff'] = snpEff


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

    def parse_template(self):
        
        if not self.check_fields():
            self.LOG.error('Some mandatory fields were missing')
            raise
        
        # Load the Jinja2 template
        try:
            # This is not very elegant :)
            templates_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'report_templates'))
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
            template = env.get_template('ign_sample_report.md')
        except:
            self.LOG.error('Could not load the Jinja report template')
            raise
        
        # Parse the template
        try:
            return template.render(report=self.info, project=self.project, sample=self.sample)
        except:
            self.LOG.error('Could not parse the ign_sample_report template')
            raise
