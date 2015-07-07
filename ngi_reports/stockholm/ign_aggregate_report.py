#!/usr/bin/env python

""" Stockholm module for dealing with fields for the IGN Aggregate Report
"""

import os
from ngi_reports.common import ign_aggregate_report

class Report(ign_aggregate_report.CommonReport):

    # Initialise the report
    def __init__(self, config, LOG, working_dir, **kwargs):

        # Set node
        self.ngi_node = 'stockholm'

        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir, **kwargs)

        # Write the aggregate data
        self.LOG.debug('Writing aggregate report')
        self.create_aggregate_statistics()
