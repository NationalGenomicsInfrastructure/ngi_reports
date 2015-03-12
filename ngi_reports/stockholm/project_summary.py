#!/usr/bin/env python

""" Class for generating project reports
Note: Much of this code was written by Pontus and lifted from
the SciLifeLab repo - see
https://github.com/senthil10/scilifelab/blob/edit_report/scilifelab/report/sequencing_report.py
"""

import os
import numpy as np
from collections import OrderedDict
from string import ascii_uppercase as alphabets
from ngi_reports.common import project_summary
from statusdb.db import connections as statusdb

class Report(project_summary.CommonReport):

    ## initialize class and assign basic variables
    def __init__(self, config, LOG, working_dir, **kwargs):

        # Initialise the parent class
        # This will grab info from the Piper XML files if found
        super(Report, self).__init__(config, LOG, working_dir, **kwargs)

        # Project name - collect from the command line if we have it
        if kwargs.get('project') is not None:
            self.project_info['ngi_name'] = kwargs['project']
        else:
            # Check to see if we have the project ID yet
            try:
                self.project_name = self.project_info['ngi_name']
            except KeyError:
                self.LOG.error("No project name found - please specify using '--project'")
                raise KeyError("No project name found - please specify using '--project'")

        # Report filename
        self.report_fn = "{}_project_summary".format(self.project_info['ngi_name'])

        # Get connections to the databases in StatusDB
        self.LOG.info("Connecting to statusDB...")
        pcon = statusdb.ProjectSummaryConnection(**kwargs)
        assert pcon, "Could not connect to {} database in StatusDB".format("project")
        fcon = statusdb.FlowcellRunMetricsConnection(**kwargs)
        assert fcon, "Could not connect to {} database in StatusDB".format("flowcell")
        scon = statusdb.SampleRunMetricsConnection(**kwargs)
        assert scon, "Could not connect to {} database in StatusDB".format("samples")
        self.LOG.info("...connected")

        # Get the project from statusdb
        self.proj = pcon.get_entry(self.project_info['ngi_name'])
        if not self.proj:
            self.LOG.error("No such project '{}'".format(self.project_info['ngi_name']))
            raise KeyError

        # Bail If the data source is not lims (old projects)
        if self.proj.get('source') != 'lims':
            self.LOG.error("The source for data for project {} is not LIMS.".format(self.project_info['ngi_name']))
            raise BaseException

        # Helper vars
        self.proj_details = self.proj.get('details',{})

        ## Get information for the reports from statusdb
        self.project_info['ngi_id'] = self.proj.get('project_id')
        self.project_info['contact'] = self.proj.get('contact')
        self.project_info['dates'] = self.get_order_dates()
        self.project_info['application'] = self.proj.get('application')
        self.project_info['num_samples'] = self.proj.get('no_of_samples')
        self.project_info['reference'] = {}
        self.project_info['reference']['genome'] = None if self.proj.get('reference_genome') == 'other' else self.proj.get('reference_genome')
        self.project_info['reference']['organism'] = self.organism_names.get(self.project_info['reference']['genome'], '')
        self.project_info['user_ID'] = self.proj_details.get('customer_project_reference')
        self.project_info['num_lanes'] = self.proj_details.get('sequence_units_ordered_(lanes)')
        self.project_info['UPPMAX_id'] = kwargs.get('uppmax_id') if kwargs.get('uppmax_id') else self.proj.get('uppnex_id')
        self.project_info['UPPMAX_path'] = "/proj/{}/INBOX/{}".format(self.project_info['UPPMAX_id'], self.project_info['ngi_name'])
        self.project_info['ordered_reads'] = self.get_ordered_reads()
        self.project_info['best_practice'] = False if self.proj_details.get('best_practice_bioinformatics','No') == "No" else True
        self.project_info['status'] = "Sequencing done" if self.proj.get('project_summary', {}).get('all_samples_sequenced') else "Sequencing ongoing"
        self.project_info['library_construction'] = self.proj_details.get('library_construction_method')
        self.project_info['flowcells_run'] = []

        # Collect information about the sample preps
        for sample_id, sample in sorted(self.proj.get('samples', {}).iteritems()):
            self.LOG.info('Processing sample {}'.format(sample_id))
            # Basic fields from Project database
            self.samples_info[sample_id] = {'ngi_id': sample_id}
            self.samples_info[sample_id]['customer_name'] = sample.get('customer_name')
            self.samples_info[sample_id]['total_reads'] = sample.get('details',{}).get('total_reads_(m)')
            self.samples_info[sample_id]['preps'] = {}
            self.samples_info[sample_id]['flowcell'] = []

            ## Get sample objects from statusdb
            s_ids = []
            for sample_run_doc in scon.get_project_sample(sample_id, sample_prj=self.project_info['ngi_name']):
                fc = "{}_{}".format(sample_run_doc.get('date'), sample_run_doc.get('flowcell'))
                if fc not in self.samples_info[sample_id]['flowcell']:
                    self.samples_info[sample_id]['flowcell'].append(fc)
                if fc not in self.project_info['flowcells_run']:
                    self.project_info['flowcells_run'].append(fc)
                s_ids.append(sample_run_doc.get("_id"))

            # Go through each prep in the Projects database
            for prep_id, prep in sample.get('library_prep', {}).iteritems():
                for fc_name, lane in prep.get('sample_run_metrics', {}).iteritems():
                    # If we have sample_run_metrics then it should have
                    # been sequenced
                    try:
                        doc_id = lane.get('sample_run_metrics_id')
                    except AttributeError:
                        pass # There are a bunch of other text fields
                    else:
                        if doc_id is not None:
                            self.samples_info[sample_id]['preps'][prep_id] = {'label': prep_id }
                            self.samples_info[sample_id]['preps'][prep_id]['barcode'] = prep.get('reagent_label')
                            self.samples_info[sample_id]['preps'][prep_id]['qc_status'] = prep.get('prep_status')
                            try:
                                s_ids.remove(doc_id)
                            except ValueError:
                                self.LOG.warn('Project DB sample_run_metrics document id {} for run {} not found in the samples database!'.format(doc_id, fc_name))
                        else:
                            self.LOG.warn("No sample_run_metrics document for run {} with id {} found in samples database!".format(fc_name, doc_id))

            ## Warn if any aren't also mentioned in the statusdb project
            for s_id in s_ids:
                self.LOG.error("sample_run_metrics document ({}) found for sample {} but no corresponding entry in project database. \
                         Please check for inconsistencies!".format(s_id, sample_id))

        # Collect information for all flowcell run for the project
        seq_method_info = []
        for fc in self.project_info['flowcells_run']:
            seq_template = "{}) Samples were sequenced on {} ({}) with a {} setup. The Bcl to Fastq conversion was performed using {} \
                            from the CASAVA software suite. The quality scale used is Sanger / phred33 / Illumina 1.8+."
            fc_obj = fcon.get_entry(fc)
            run_setup = fc_obj.get("run_setup")
            fc_runp = fc_obj.get('RunParameters',{})
            seq_plat = ["HiSeq2500","MiSeq"]["MCSVersion" in fc_runp.keys()]
            casava = fc_obj.get('DemultiplexConfig',{}).values()[0].get('Software',{}).get('Version')
            if seq_plat == "MiSeq":
                seq_software = "MSC {}/RTA {}".format(fc_runp.get("MCSVersion"),fc_runp.get("RTAVersion"))
            else:
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName"),fc_runp.get("ApplicationVersion"),fc_runp.get("RTAVersion"))
            tmp_method = seq_template.format("SECTION", seq_plat, seq_software, run_setup,casava)
            ## to make sure the sequencing methods are uniq
            if tmp_method not in seq_method_info:
                seq_method_info.append(tmp_method)

        ## give proper section name for the methods
        seq_method_info = [seq_method_info[c].replace("SECTION",alphabets[c]) for c in range(len(seq_method_info))]
        self.project_info['sequencing_methods'] = "\n\n".join(seq_method_info)


















    def get_ordered_reads(self):
        """ Get the minimum ordered reads for this project or return None
        """
        reads_min = []
        # in rare cases there might be different amounts ordered
        # for different pools
        for sample in self.proj.get('samples',{}):
            try:
                reads_min.append("{}M".format(self.proj['samples'][sample]['details']['reads_min']))
            except KeyError:
                continue
        if len(reads_min) > 0:
            return ", ".join(list(set(reads_min)))
        else:
            return None


    def get_order_dates(self):
        """ Get order dates as a markdown string. Ignore if unavilable in status DB
        """
        dates = []
        if self.proj_details.get('order_received'):
            dates.append("_Order received:_ {}".format(self.proj_details.get('order_received')))
        if self.proj_details.get('contract_received'):
            dates.append("_Contract received:_ {}".format(self.proj_details.get('contract_received')))
        if self.proj_details.get('samples_received'):
            dates.append("_Samples received:_ {}".format(self.proj_details.get('samples_received')))
        if self.proj_details.get('queue_date'):
            dates.append("_Queue date:_ {}".format(self.proj_details.get('queue_date')))
        if self.proj.get('project_summary',{}).get('all_samples_sequenced'):
            dates.append("_All data delivered:_ {}".format(self.proj.get('project_summary',{}).get('all_samples_sequenced')))
        if self.creation_date:
            dates.append("_Report date:_ {}".format(self.creation_date))
        return ", ".join(dates)
