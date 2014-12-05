#!/usr/bin/env python

""" Class for generating project reports
"""

import os
import jinja2
import numpy as np
from collections import OrderedDict
from string import ascii_uppercase as alphabets
from ngi_reports.common import project_summary
from statusdb.db.connections import ProjectSummaryConnection, SampleRunMetricsConnection, FlowcellRunMetricsConnection

class Report(project_summary.CommonReport):
    
    ## initialize class and assign basic variables
    def __init__(self, config, LOG, working_dir, **kwargs):
        
        # Initialise the parent class
        super(Report, self).__init__(config, LOG, working_dir)
        
        # Project name - collect from the command line if we have it
        if kwargs.get('project') is not None:
            self.project_info['ngi_name'] = kwargs['project']
        else:
            # Check to see if the common parent class got it from
            # the file system
            try:
                self.project_info['ngi_name']
            except NameError:
                self.LOG.error("No project name found - please specify using '--project'")
                raise NameError("No project name found - please specify using '--project'")
        
        # Report filename
        self.report_fn = "{}_project_summary".format(self.project_info['ngi_name'])
        
        # Get project information from statusdb
        self.pcon = ProjectSummaryConnection()
        self.scon = SampleRunMetricsConnection()
        try:
            self.proj_db_key = self.pcon.name_view[self.project_info['ngi_name']]
        except KeyError:
            self.LOG.error("Project <project_name> not found in statusdb")
            raise
        self.proj = self.pcon.get_entry(self.project_info['ngi_name'])
        
        self.proj_samples = self.proj.get('samples',{})
        self.proj_details = self.proj.get('details',{})
        
        ## Get information for the reports from statusdb
        self.project_info['ngi_id'] = self.proj.get('project_id');
        self.project_info['contact'] = self.proj.get('contact');
        self.project_info['dates'] = self.get_order_dates();
        self.project_info['application'] = self.proj.get('application');
        self.project_info['num_samples'] = self.proj.get('no_of_samples');
        self.project_info['reference'] = self.get_ref_genome();
        self.project_info['user_ID'] = self.proj_details.get('customer_project_reference');
        self.project_info['num_lanes'] = self.proj_details.get('sequence_units_ordered_(lanes)');
        self.project_info['UPPMAX_path'] = self.get_uppmax_path(kwargs.get('uppmax_id'));
        self.project_info['UPPMAX_id'] = kwargs.get('uppmax_id') if kwargs.get('uppmax_id') else self.proj.get('uppnex_id');
        self.project_info['ordered_reads'] = kwargs.get('reads_minimum') if kwargs.get('reads_minimum') else self.get_ordered_reads();
        self.project_info['best_practice'] = False if self.proj_details.get('best_practice_bioinformatics','No')=="No" else True;
        self.project_info['status'] = "Sequencing done" if self.proj.get('project_summary', {}).get('all_samples_sequenced') else "Sequencing ongoing";
        
        # Get the methods information for the report
        self.methods_info['library_construction'] = self.get_libprep_method()
        

    
    ## get uppmax path where project data is delivered
    def get_uppmax_path(self,uppmax):
        upp_id = uppmax if uppmax else self.proj.get('uppnex_id')
        return "/proj/{}/INBOX/{}".format(upp_id, self.project_info['ngi_name'])
    
    ## get reference organism and genome if its supported by NGI
    # TODO: organism is not always available in DB, fix or remove
    def get_ref_genome(self):
        ref_info = {}
        ref_info['genome'] = self.proj.get('reference_genome',"other")
        if ref_info['genome'] != "other":
            ref_info['organism'] = self.proj_details.get("organism")
        else:
            ref_info['genome'] = None
            ref_info['organism'] = None
        return ref_info
    
    ## get minimal ordered reads for that project
    def get_ordered_reads(self):
        reads_min = []
        # on rare cases there might be different ordered amnt for different pools
        for sample in self.proj_samples:
            try:
                reads_min.append("{}M".format(self.proj_samples[sample]['details']['reads_min']))
            except KeyError:
                continue
        return ", ".join(list(set(reads_min)))
    
    ## get order dates and dates not show if info unavilable in status DB
    def get_order_dates(self):
        dates = []
        if self.proj_details.get('order_received'):
            dates.append("_Order received:_ {}".format(self.proj_details.get('order_received')))
        if self.proj_details.get('contract_received'):
            dates.append("_Contract received:_ {}".format(self.proj_details.get('contract_received')))
        if self.proj_details.get('samples_received'):
            dates.append("Samples received:_ {}".format(self.proj_details.get('samples_received')))
        if self.proj_details.get('queue_date'):
            dates.append("_Queue date:_ {}".format(self.proj_details.get('queue_date')))
        if self.proj.get('project_summary',{}).get('all_samples_sequenced'):
            dates.append("_All data delivered:_ {}".format(self.proj.get('project_summary',{}).get('all_samples_sequenced')))
        if self.creation_date:
            dates.append("_Report date:_ {}".format(self.creation_date))
        return ", ".join(dates)
    
    ## get library preps and add alphabets accordingly for different preps
    ## TODO: Having the text is not so pretty, we can confirm with lab people
    ## if one project can have only one librarby prep for certain, than we can
    ## add this text to mark down template
    def get_libprep_method(self):
        libPrep_template = '{}) Library was prepared using "{}" protocol'
        prep_methods = [self.proj_details.get("library_construction_method")]
        all_methods = []
        for cnt in range(len(prep_methods)):
            all_methods.append(libPrep_template.format(alphabets[cnt],prep_methods[cnt]))
#            self.accredit_info["Library preparation"] = "|{}|".format("Yes" if prep_methods[cnt] in self.accredited_libMethods else "No")
        return "\n\n".join(all_methods)
    
    def parse_template(self):
        # Load the Jinja2 template
        try:
            # This is not very elegant :)
            templates_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'report_templates'))
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
            template = env.get_template('project_summary.md')
        except:
            self.LOG.error('Could not load the Jinja report template')
            raise
        
        # Parse the template
        try:
            return template.render(project=self.project_info, methods=self.methods_info)
        except:
            self.LOG.error('Could not parse the ign_sample_report template')
            raise