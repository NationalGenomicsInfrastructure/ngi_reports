#!/usr/bin/env python

""" Uppsala module for dealing with fields for the IGN Sample Report
"""

import os
from ngi_reports.common import ign_sample_report
from statusdb.db import connections as statusdb

class Report(ign_sample_report.CommonReport):
    
    # Initialise the report
    def __init__(self, config, LOG, working_dir, **kwargs):
        
        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir)
        
        #### Missing Fields
        # self.info['recipient']
        # self.sample['user_sample_id']
        # self.sample['prep']
