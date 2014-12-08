#!/usr/bin/env python

""" Common module for producing the Project Summary Report
"""

from datetime import datetime
import jinja2
import os
import xmltodict

class CommonReport(object):
    
    def __init__(self, config, LOG, working_dir, **kwargs):
        
        # Incoming handles
        self.config = config
        self.LOG = LOG
        self.working_dir = working_dir
        
        # general initialization
        self.project_info = {}
        self.methods_info = {}
        self.accredit_info = {}
        
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
            # First, try to grab the project name. This is the most important  
            try:
                self.project_info['ngi_name'] = run['metadata']['name']
                self.report_dir = os.path.join(working_dir, 'delivery', 'reports')
            except KeyError:
                self.LOG.warning('Could not find Project Name key in XML file')
                pass
            
            # TODO - Get other fields from the XML files if we can.
            # These will be over-written by statusDB information in
            # Stockholm but will give a helping-hand to Uppsala.
            # As they're less critical we can do it in a separate
            # try / except block
    
    
    # Return the parsed markdown
    def parse_template(self, template):
        # Parse the template
        try:
            return template.render(project=self.project_info, methods=self.methods_info)
        except:
            self.LOG.error('Could not parse the ign_sample_report template')
            raise
                