#!/usr/bin/env python

""" Main module for dealing with fields for the IGN Sample Report
"""

import os

def get_fields(config, working_dir=os.getcwd()):
    
    # Setup
    ngi_node = config.get('ngi_reports', 'ngi_node')
    
    # Initialise empty dict
    fields = {}
    fields['report'] = fields['project'] = fields['sample'] = {}
    
    # Scrape information from the filesystem
    
    # Report Fields
    fields['report']['recipient'] = 'FUBAR'
    
    # Project Fields
    fields['project']['id'] = 'FUBAR'
    fields['project']['group'] = 'FUBAR'
    fields['project']['user_sample_id'] = 'FUBAR'
    fields['project']['UPPMAXid'] = 'FUBAR'
    fields['project']['sequencing_centre'] = 'NGI {}'.format(ngi_node).title()

    # Sample Fields
    fields['sample']['id'] = 'FUBAR'
    fields['sample']['sequencing_platform'] = 'FUBAR'
    fields['sample']['user_sample_id'] = 'FUBAR'
    fields['sample']['ref_genome'] = 'FUBAR'
    fields['sample']['total_reads'] = 'FUBAR'
    fields['sample']['percent_aligned'] = 'FUBAR'
    fields['sample']['aligned_reads'] = 'FUBAR'
    fields['sample']['duplication_rate'] = 'FUBAR'
    fields['sample']['median_insert_size'] = 'FUBAR'
    fields['sample']['automsomal_coverage'] = 'FUBAR'
    fields['sample']['ref_above_30X'] = 'FUBAR'
    fields['sample']['percent_gc'] = 'FUBAR'
    fields['sample']['snpeff'] = {}
    fields['sample']['snpeff']['change_rate'] = 'FUBAR'
    fields['sample']['snpeff']['total_snps'] = 'FUBAR'
    fields['sample']['snpeff']['homotypic_snps'] = 'FUBAR'
    fields['sample']['snpeff']['heterotypic_snps'] = 'FUBAR'
    fields['sample']['snpeff']['TsTv_ratio'] = 'FUBAR'
    fields['sample']['snpeff']['synonymous_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['nonsynonymous_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['stops_gained'] = 'FUBAR'
    fields['sample']['snpeff']['stops_lost'] = 'FUBAR'
    fields['sample']['snpeff']['percent_missense_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['missense_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['percent_nonsense_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['nonsense_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['percent_silent_SNPs'] = 'FUBAR'
    fields['sample']['snpeff']['silent_SNPs'] = 'FUBAR'
    fields['sample']['preps'] = [{'label': 'FUBAR', 'description': 'FUBAR'}]
    fields['sample']['flowcells'] = [{'id': 'FUBAR'}]
    
    # Import the NGI node-specific module
    node_mod = __import__('ngi_reports.{}.ign_sample_report'.format(ngi_node), fromlist=['ngi_reports.{}'.format(ngi_node)])
    
    # Pull the node-specific fields
    fields = dict(fields.items() + node_mod.get_fields(working_dir, config).items())
    
    # Retun everything
    return fields
