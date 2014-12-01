#!/usr/bin/env python

""" Stockholm module for dealing with fields for the IGN Sample Report
"""

import os
from ngi_reports.common import ign_sample_report

class Report(ign_sample_report.CommonReport):
    
    # Initialise the report
    def __init__(self, config, LOG, working_dir):
        
        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir)

        

