""" Module for producing the ONT Project Summary Report
"""
import ngi_reports.reports

class Report(ngi_reports.reports.project_summary.Report):
    def __init__(self, LOG, working_dir, **kwargs):
        super(Report, self).__init__(LOG, working_dir, **kwargs)
        
    def generate_report_template(self, proj, template, support_email):
        #TODO: fill in with useful stuff
        pass