#!/usr/bin/env python

""" 
Report class to extend if you don't care about the center
TODO Can probably be removed in the future, but useful
     for scripts which just need to parse the basic 
     data
"""

import os
import json
from ngi_reports.common import ign_sample_report

class Report(ign_sample_report.CommonReport):

    # Initialise the report
    def __init__(self, config, LOG, working_dir, **kwargs):

        print(json.dumps(kwargs, 1))
        # Set node
        self.ngi_node = kwargs.get("ngi_node")

        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir)
