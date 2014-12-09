#!/usr/bin/env python

""" Stockholm module for dealing with fields for the IGN Sample Report
"""

import os
from ngi_reports.common import ign_sample_report
from statusdb.db import connections as statusdb

class Report(ign_sample_report.CommonReport):
    
    # Initialise the report
    def __init__(self, config, LOG, working_dir, **kwargs):
        
        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir, **kwargs)
        
        # Get project fields from statusdb
        p = statusdb.ProjectSummaryConnection()
        proj = p.get_entry(self.project['id'])
        self.info['recipient'] = proj.get('contact')
        self.project['prep'] = proj.get('details', {}).get('library_construction_method')
         
        # Get sample fields from statusdb
        for sid in self.samples.iterkeys():
            try:
                self.samples[sid]['user_sample_id'] = proj['samples'][sid]['customer_name']
                self.samples[sid]['barcode'] = proj['samples'][sid]['library_prep']['A']['reagent_label']
            except KeyError:
                pass
            

