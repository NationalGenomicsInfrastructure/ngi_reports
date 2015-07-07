#!/usr/bin/env python

""" Common module for dealing with fields for the IGN Aggregate Report
"""

import collections
import csv
import os
from ngi_reports.common import ign_sample_report

class CommonReport(ign_sample_report.CommonReport):

    # Initialise the report
    def __init__(self, config, LOG, working_dir, **kwargs):

        # Initialise the parent class
        super(CommonReport, self).__init__(config, LOG, working_dir, **kwargs)

    # Create CSV files with aggregate stats for samples
    def create_aggregate_statistics (self):

        def create_header (samples):
            # take the union of all keys for the header row
            return sorted(
                list(
                    set(
                        [key \
                        for sample in samples.values() \
                        for key in sample.keys()])))

        def create_rows (samples):
            # return the samples sorted alphabetically on the keys
            for sample in sorted(samples.keys()):
                yield samples[sample]

        output_fn = "{}_aggregate_report.csv".format(self.project['id'])
        output_file = os.path.realpath(os.path.join(self.report_dir, output_fn))

        # Flatten out the dict to make it writable as a csv
        flattened_samples = {}
        for sample in self.samples:
            flattened = self.flatten_dict(self.samples[sample])
            flattened_samples[sample] = collections.OrderedDict(flattened)

        # Parse out the data
        header = create_header(flattened_samples)
        rows = create_rows(flattened_samples)

        self.LOG.debug("Writing aggregate report to: " + output_file)

        # Drop it to a csv
        with open(output_file, 'wb') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=header,
                delimiter="\t")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
