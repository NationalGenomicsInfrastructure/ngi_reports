#!/usr/bin/env python

""" Common module for producing the Project Summary Report
"""

from datetime import datetime
import os
import xmltodict

class CommonReport(object):
    
    def __init__(self, config, LOG, working_dir):
        
        # Incoming handles
        self.config = config
        self.LOG = LOG
        self.working_dir = working_dir
        
        # general initialization
        self.date_format = "%Y-%m-%d"
        self.creation_date = datetime.now().strftime(self.date_format)
        
        # report name and directory to be created
        self.report_dir = os.path.join(working_dir, 'reports')
        
        # Find the project name from the XML file if we have one
        xml_fn = os.path.realpath(os.path.join(self.working_dir, 'project_setup_output_file.xml'))
        if os.path.isfile(xml_fn):
            try:
                with open(xml_fn) as fh:
                    run = xmltodict.parse(fh)
            except IOError as e:
                raise IOError("Could not open configuration file \"{}\".".format(xml_fn))
        
            run = run['project']        
            try:
                self.proj_name = run['metadata']['name']
                self.report_dir = os.path.join(working_dir, 'delivery', 'reports')
            except KeyError:
                self.LOG.warning('Could not find Project Name key in XML file')
                pass