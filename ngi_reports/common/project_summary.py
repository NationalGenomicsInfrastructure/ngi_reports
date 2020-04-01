#!/usr/bin/env python

""" Common module for producing the Project Summary Report
"""

from collections import defaultdict
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
        self.flowcell_info = {}
        self.tables_info = defaultdict(dict)

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
            md = template.render(project=self.project_info, samples=self.samples_info,
                                 flowcells=self.flowcell_info, tables=self.tables_info['header_explanation'])
            return {output_bn: md}
        except:
            self.LOG.error('Could not parse the project_summary template')
            raise

    # Generate CSV files for the tables
    def create_txt_files(self, op_dir=None):
        """ Generate the CSV files for mentioned tables i.e. a dictionary with table name as key,
            which will be used as file name and the content of file in single string as value to
            put in the TXT file

            :param str op_dir: Path where the TXT files should be created, current dir is default
        """
        for tb_nm, tb_cont in self.tables_info['tables'].items():
            op_fl = "{}_{}.txt".format(self.project_name, tb_nm)
            if op_dir:
                op_fl = os.path.join(op_dir, op_fl)
            with open(op_fl, 'w') as TXT:
                TXT.write(tb_cont)
