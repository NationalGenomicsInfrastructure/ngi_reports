#!/usr/bin/env python

""" Common module for producing the Project Summary Report
"""

from datetime import datetime
import jinja2
import os

import ngi_reports.common

class CommonReport(ngi_reports.common.BaseReport):
    
    def __init__(self, config, LOG, working_dir, **kwargs):
        
        # Initialise the parent class
        super(CommonReport, self).__init__(config, LOG, working_dir, **kwargs)
        
        # general initialization
        self.project_info = {}
        self.samples_info = {}
        
        # report name and directory to be created
        self.report_dir = os.path.join(working_dir, 'reports')
        
        # Scrape information from the filesystem
        # This function is in the common BaseReport class in __init__.py
        xml = self.parse_piper_xml()
        self.project_info = xml['project']
        self.samples_info = xml['samples']
        if len(xml['project']) > 0:
            self.report_dir = os.path.join(working_dir, 'delivery', 'reports')
    
    
    # Return the parsed markdown
    def parse_template(self, template):
        # Make the file basename
        output_bn = os.path.realpath(os.path.join(self.working_dir, self.report_dir, self.report_fn))
        
        # Parse the template
        try:
            md = template.render(project=self.project_info, samples=self.samples_info)
            return {output_bn: md}
        except:
            self.LOG.error('Could not parse the ign_sample_report template')
            raise
                