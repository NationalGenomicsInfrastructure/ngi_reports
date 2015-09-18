#!/usr/bin/env python

""" Class for generating project reports
Note: Much of this code was written by Pontus and lifted from
the SciLifeLab repo - see
https://github.com/senthil10/scilifelab/blob/edit_report/scilifelab/report/sequencing_report.py
"""

import os
import re
import numpy as np
from datetime import datetime
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

        ## Project name - collect from the command line if we have it
        if kwargs.get('project') is not None:
            self.project_info['ngi_name'] = kwargs['project']
            self.project_name = self.project_info['ngi_name']
        else:
            ## Check to see if we have the project ID yet
            try:
                self.project_name = self.project_info['ngi_name']
            except KeyError:
                self.LOG.error("No project name found - please specify using '--project'")
                raise KeyError("No project name found - please specify using '--project'")
        
        ## Report filename
        self.report_fn = "{}_project_summary".format(self.project_name)

        ## Get connections to the databases in StatusDB
        self.LOG.info("Connecting to statusDB...")
        pcon = statusdb.ProjectSummaryConnection(**kwargs)
        assert pcon, "Could not connect to {} database in StatusDB".format("project")
        fcon = statusdb.FlowcellRunMetricsConnection(**kwargs)
        assert fcon, "Could not connect to {} database in StatusDB".format("flowcell")
        scon = statusdb.SampleRunMetricsConnection(**kwargs)
        assert scon, "Could not connect to {} database in StatusDB".format("samples")
        self.LOG.info("...connected")
        
        ## Get the project from statusdb
        self.proj = pcon.get_entry(self.project_name)
        if not self.proj:
            self.LOG.error("No such project '{}'".format(self.project_name))
            raise KeyError

        ## Bail If the data source is not lims (old projects)
        if self.proj.get('source') != 'lims':
            self.LOG.error("The source for data for project {} is not LIMS.".format(self.project_name))
            raise BaseException

        ## Helper vars
        seq_methods, sample_qval = (OrderedDict(), {})
        self.proj_details = self.proj.get('details',{})
        
        ## Check if it is an aborted project before proceding
        if "aborted" in self.proj_details:
            self.LOG.warn("Project {} was aborted, so not proceeding.".format(self.project_name))
            raise SystemExit
        
        ## Assign person creating the report
        if kwargs.get('signature'):
            self.project_info['signature'] = kwargs.get('signature')
        else:
            self.LOG.warn("Signature not given while generating report.")
        
        ## Get information for the reports from statusdb
        self.project_info['ngi_id'] = self.proj.get('project_id')
        self.project_info['ngi_facility'] = "Genomics {} Stockholm".format(self.proj_details.get('type')) if self.proj_details.get('type') else None 
        self.project_info['contact'] = self.proj.get('contact')
        self.project_info['support_email'] = config.get('ngi_reports','support_email')
        self.project_info['dates'] = self.get_order_dates()
        self.project_info['report_date'] = datetime.now().strftime("%Y-%m-%d")
        self.project_info['application'] = self.proj.get('application')
        self.project_info['num_samples'] = self.proj.get('no_of_samples')
        self.project_info['reference'] = {}
        self.project_info['reference']['genome'] = None if self.proj.get('reference_genome') == 'other' else self.proj.get('reference_genome')
        self.project_info['reference']['organism'] = self.organism_names.get(self.project_info['reference']['genome'], '')
        self.project_info['user_ID'] = self.proj_details.get('customer_project_reference')
        self.project_info['num_lanes'] = self.proj_details.get('sequence_units_ordered_(lanes)')
        self.project_info['UPPMAX_id'] = kwargs.get('uppmax_id') if kwargs.get('uppmax_id') else self.proj.get('uppnex_id')
        self.project_info['UPPMAX_path'] = "/proj/{}/INBOX/{}".format(self.project_info['UPPMAX_id'], self.project_info['ngi_name'])
        self.project_info['ordered_reads'] = []
        self.project_info['best_practice'] = False if self.proj_details.get('best_practice_bioinformatics','No') == "No" else True
        self.project_info['status'] = "Sequencing done" if self.proj.get('project_summary', {}).get('all_samples_sequenced') else "Sequencing ongoing"
        self.project_info['library_construction'] = self.get_library_method()
        self.project_info['accredit'] = self.get_accredit_info(['library_preparation','sequencing','data_processing','data_analysis'])
        self.project_info['total_lanes'] = 0
        self.project_info['display_limit'] = kwargs.get('display_limit')
        self.project_info['missing_fc'] = False
        self.project_info['aborted_samples'] = {}
        
        ## Collect information about the sample preps and collect aborted samples
        for sample_id, sample in sorted(self.proj.get('samples', {}).iteritems()):
            self.LOG.info('Processing sample {}'.format(sample_id))
            ## Check if the sample is aborted before processing
            if sample.get('details',{}).get('status_(manual)') == "Aborted":
                self.LOG.info('Sample {} is aborted, so skipping it'.format(sample_id))
                self.project_info['aborted_samples'][sample_id] = {'user_id': sample.get('customer_name',''), 'status':'Aborted'}
                continue
            
            ## Basic fields from Project database
            self.samples_info[sample_id] = {'ngi_id': sample_id}
            ## special characters should be removed 
            self.samples_info[sample_id]['customer_name'] = sample.get('customer_name','').encode('ascii', 'ignore')
            self.samples_info[sample_id]['total_reads'] = sample.get('details',{}).get('total_reads_(m)')
            self.samples_info[sample_id]['reads_min'] = sample.get('details',{}).get('reads_min')
            
            ## Check if a non-aborted sample is sequenced
            if self.samples_info[sample_id]['total_reads'] == None:
                self.LOG.warn("Sample {} doesn't have total reads, so adding it to NOT sequenced samples list.".format(sample_id))
                self.project_info['aborted_samples'][sample_id] = {'user_id': sample.get('customer_name',''), 'status':'Not sequenced'}
                del self.samples_info[sample_id]
                continue
            
            ## Check if reads minimum set for sample and the status if it does
            if self.samples_info[sample_id]['reads_min']:
                self.project_info['ordered_reads'].append("{}M".format(self.samples_info[sample_id]['reads_min']))
                if float(self.samples_info[sample_id]['total_reads']) > float(self.samples_info[sample_id]['reads_min']):
                    self.samples_info[sample_id]['seq_status'] = 'PASSED'
                else:
                    self.samples_info[sample_id]['seq_status'] = 'FAILED'
            
            self.samples_info[sample_id]['preps'] = {}
            self.samples_info[sample_id]['flowcell'] = []
            ## Get sample objects from statusdb
            for sample_run_doc in scon.get_project_sample(sample_id, sample_prj=self.project_name):
                fc_name = sample_run_doc.get('flowcell')
                fc_run_name = "{}_{}".format(sample_run_doc.get('date'), fc_name)
                if fc_name not in self.flowcell_info.keys():
                    self.flowcell_info[fc_name] = {'name':fc_name,'run_name':fc_run_name, 'date': sample_run_doc.get('date')}
                if fc_run_name not in self.samples_info[sample_id]['flowcell']:
                    self.samples_info[sample_id]['flowcell'].append(fc_run_name)

            ## Go through each prep for each sample in the Projects database
            for prep_id, prep in sample.get('library_prep', {}).iteritems():
                self.samples_info[sample_id]['preps'][prep_id] = {'label': prep_id }
                self.samples_info[sample_id]['preps'][prep_id]['barcode'] = prep.get('reagent_label','')
                self.samples_info[sample_id]['preps'][prep_id]['qc_status'] = prep.get('prep_status','')
                
                #get average fragment size from lastest validation step if exists not for PCR-free libs
                if not 'pcr-free' in self.project_info['library_construction'].lower():
                    try:
                        lib_valids = prep['library_validation']
                        keys = sorted(lib_valids.keys(), key=lambda k: datetime.strptime(lib_valids[k]['start_date'], "%Y-%m-%d"), reverse=True)
                        self.samples_info[sample_id]['preps'][prep_id]['avg_size'] = re.sub(r'(\.[0-9]{,2}).*$', r'\1', str(lib_valids[keys[0]]['average_size_bp']))
                    except KeyError:
                        self.LOG.warn("No library validation step found or no sufficient info for sample {}".format(sample_id))
                else:
                    self.samples_info[sample_id]['preps'][prep_id]['avg_size'] = "N/A"
        
            if not self.samples_info[sample_id]['preps']:
                self.LOG.warn('No library prep information was available for sample {}'.format(sample_id))
        
        if not self.flowcell_info:
            self.LOG.warn('There is no flowcell to process for project {}'.format(self.project_name))
            self.project_info['missing_fc'] = True
            
        ## Collect reuired information for all flowcell run for the project
        for fc in self.flowcell_info.values():
            fc_name = fc['name']
            fc_obj = fcon.get_entry(fc['run_name'])
            fc_runp = fc_obj.get('RunParameters',{})
            fc_illumina = fc_obj.get('illumina',{})
            fc_run_summary = fc_illumina.get('run_summary',{})
            self.flowcell_info[fc_name]['lanes'] = {}
            
            ## Get sequecing method for the flowcell
            seq_template = "{}) Clustering was done by '{}' and samples were sequenced on {} ({}) with a {} setup using '{}' "\
                           "chemistry. The Bcl to FastQ conversion was performed using {} from the CASAVA software suite. The "\
                           "quality scale used is Sanger / phred33 / Illumina 1.8+."
            run_setup = fc_obj.get("run_setup")
            fc_chem = fc_runp.get('ReagentKitVersion', fc_runp.get('Sbs'))
            seq_plat = ["HiSeq2500","MiSeq"]["MCSVersion" in fc_runp.keys()]
            clus_meth = ["cBot","onboard clustering"][seq_plat == "MiSeq" or fc_runp.get("ClusteringChoice","") == "OnBoardClustering"]
            casava = fc_obj.get('DemultiplexConfig',{}).values()[0].get('Software',{}).get('Version')
            if seq_plat == "MiSeq":
                seq_software = "MSC {}/RTA {}".format(fc_runp.get("MCSVersion"),fc_runp.get("RTAVersion"))
            else:
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName"),fc_runp.get("ApplicationVersion"),fc_runp.get("RTAVersion"))
            tmp_method = seq_template.format("SECTION", clus_meth, seq_plat, seq_software, run_setup, fc_chem, casava)
            
            ## to make sure the sequencing methods are unique
            if tmp_method not in seq_methods.keys():
                seq_methods[tmp_method] = alphabets[len(seq_methods.keys())]
            self.flowcell_info[fc_name]['seq_meth'] = seq_methods[tmp_method]
            
            ## Collect quality info for samples and collect lanes of interest
            for stat in fc_illumina.get('Demultiplex_Stats',{}).get('Barcode_lane_statistics',[]):
                try:
                    sample, lane = (stat['Sample ID'], stat['Lane'])
                    if stat['Project'].replace('__','.') != self.project_name:
                        continue
                    ## to put in a empty dict for the first time
                    sample_qval[sample] = sample_qval.get(sample,{})
                    try:
                        sample_qval[sample]['{}_{}'.format(lane, fc_name)] = {'qval': float(stat.get('% of >= Q30 Bases (PF)')),
                                                                        'bases': int(stat.get('# Reads').replace(',',''))*int(run_setup.split('x')[-1])}
                    except (TypeError, ValueError) as e:
                        pass
                    ## collect lanes to proceed later
                    if lane not in self.flowcell_info[fc_name]['lanes']:
                        lane_sum = fc_run_summary.get(lane, fc_run_summary.get('A',{}))
                        self.flowcell_info[fc_name]['lanes'][lane] = {'id': lane,
                                                                      'cluster': self.get_lane_info('Clusters PF',lane_sum,run_setup[0],True),
                                                                      'phix': self.get_lane_info('% Error Rate',lane_sum,run_setup[0]),
                                                                      'avg_qval': self.get_lane_info('% Bases >=Q30',lane_sum,run_setup[0])}
                except KeyError:
                    continue
        
        ## give proper section name for the methods
        self.project_info['sequencing_methods'] = "\n\n".join([m.replace("SECTION",seq_methods[m]) for m in seq_methods])
        ## convert readsminimum list to a string
        self.project_info['ordered_reads'] = ", ".join(set(self.project_info['ordered_reads']))
        
        ## calculate average Q30 over all lanes and flowcell
        for sample in sample_qval:
            try:
                qinfo = sample_qval[sample]
                total_qvalsbp, total_bases = (0, 0)
                for k in qinfo:
                    total_qvalsbp += qinfo[k]['qval'] * qinfo[k]['bases']
                    total_bases += qinfo[k]['bases']
                avg_qval = float(total_qvalsbp)/total_bases if total_bases else float(total_qvalsbp) 
                self.samples_info[sample]['qscore'] = round(avg_qval, 2)
                ## Samples with avyg Q30 less than 80 should be failed according to our routines
                if int(self.samples_info[sample]['qscore']) < 80:
                    self.samples_info[sample]['seq_status'] = 'FAILED'
            except (TypeError, KeyError):
                self.LOG.error("Could not calcluate average Q30 for sample {}".format(sample))
        

    ###############################################################################
    ##### Create table text and header explanation from collected information #####
    ###############################################################################

        ## sample_info table
        sample_header = ['NGI ID', 'User ID', 'Mreads', '>=Q30']
        sample_filter = ['ngi_id', 'customer_name', 'total_reads', 'qscore']
        if self.proj.get('application') != "Finished library":
            sample_header.append('Status')
            sample_filter.append('seq_status')
        self.tables_info['tables']['sample_info'] = self.create_table_text(self.samples_info, filter_keys=sample_filter, header=sample_header)
        self.tables_info['header_explanation']['sample_info'] = "* _NGI ID:_ Internal NGI sample indentifier\n"\
                                                                "* _User ID:_ User submitted name for a sample\n"\
                                                                "* _Mreads:_ Total million reads (or pairs) for a sample\n"\
                                                                "* _>=Q30:_ Aggregated percentage of bases that have quality score more the Q30\n"\
                                                                "* _Status:_ Sequencing status of sample based on the total reads"
        if not self.project_info['ordered_reads']:
            self.tables_info['header_explanation']['sample_info'] = re.sub(r'\n\* _Status\:_ .*$','',self.tables_info['header_explanation']['sample_info'])
        
        ## library_info table
        library_header = ['NGI ID', 'Index', 'Lib Prep', 'Avg. FS', 'Lib QC']
        library_filter = ['ngi_id', 'barcode', 'label', 'avg_size', 'qc_status']
        library_list = []
        for s, v in self.samples_info.items():
            for p in v.get('preps',{}).values():
                p['ngi_id'] = s
                library_list.append(p)
        self.tables_info['tables']['library_info'] = self.create_table_text(library_list, filter_keys=library_filter, header=library_header)
        self.tables_info['header_explanation']['library_info'] = "* _NGI ID:_ Internal NGI sample indentifier\n"\
                                                                 "* _Index:_ Barcode sequence used for the sample\n"\
                                                                 "* _Lib Prep:_ NGI library indentifier\n"\
                                                                 "* _Avg. FS:_ Average fragment size of the library\n"\
                                                                 "* _Lib QC:_ Reception control library quality control step status\n"
        
        ## lanes_info table
        lanes_header = ['Date', 'FC id', 'Lane', 'Cluster(M)', 'Phix', '>=Q30(%)', 'Method']
        lanes_filter = ['date', 'name', 'id', 'cluster', 'phix', 'avg_qval', 'seq_meth']
        lanes_list = []
        for f, v in self.flowcell_info.items():
            for l in v.get('lanes',{}).values():
                l['date'] = v.get('date')
                l['name'] = v.get('name')
                l['seq_meth'] = v.get('seq_meth')
                lanes_list.append(l)
                self.project_info['total_lanes'] += 1
        self.tables_info['tables']['lanes_info'] = self.create_table_text(lanes_list, filter_keys=lanes_filter, header=lanes_header)
        self.tables_info['header_explanation']['lanes_info'] = "* _Date:_ Date of sequencing\n"\
                                                               "* _Flowcell:_ Flowcell identifier\n"\
                                                               "* _Lane:_ Flowcell lane number\n"\
                                                               "* _Clusters:_ Number of clusters that passed the read filters (millions)\n"\
                                                               "* _>=Q30:_ Aggregated percentage of bases that have a quality score of more than Q30\n"\
                                                               "* _PhiX:_ Average PhiX error rate for the lane\n"\
                                                               "* _Method:_ Sequencing method used. See above for description\n"
        
    #####################################################
    ##### Helper methods to get certain information #####
    #####################################################

    def create_table_text(self, ip, filter_keys=None, header=None, sep='\t'):
        """ Create a single text string that will be saved in a file in TABLE format
            from given dict and filtered based upon mentioned header.
            
            :param dict/list ip: Input dictionary/list to be convertead as table string
            :param list filter: A list of keys that will be used to filter the ip_dict
            :param list header: A list that will be used as header
            :param str sep: A string that will be used as separator
        """
        op_string = []
        if isinstance(ip, dict):
            ip = ip.values()
        if header:
            op_string.append(sep.join(header))
        if not filter_keys:
            filter_keys = []
            for i in ip:
                filter_keys.extend(i.keys())
            filter_keys = sorted(list(set(filter_keys)))
        for i in ip:
            row = []
            for k in filter_keys:
                row.append(i.get(k,'NA'))
            row = map(str, row)
            op_string.append(sep.join(row))
        return "\n".join(op_string)


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


    def get_library_method(self):
        """Get the library construction method and return as formatted string
        """
        if self.proj.get('application') == "Finished library":
            return "Library was prepared by user."
        try:
            lib_head = ['Input', 'Type', 'Option', 'Category']
            lib_meth = [i.strip() for i in re.sub("\[\d+\]$", '', self.proj_details['library_construction_method']).split(',')]
            if len(lib_meth) == 4:
                lib_list = []
                for category,method in zip(lib_head,lib_meth):
                    if method != '-':
                        lib_list.append("* {}: {}".format(category, method))
                return ("\n".join(lib_list))
            else:
                self.LOG.error("Library method is not mentioned in expected format for project {}".format(self.project_name))
        except KeyError:
            self.LOG.error("Could not find library construction method for project {} in statusDB".format(self.project_name))


    def get_accredit_info(self,keys):
        """Get swedac accreditation info for given step 'k'
        
        :param list keys: step names which are keys in project database
        """
        accredit_info = {}
        for k in keys:
            try:
                accredit = self.proj_details['accredited_({})'.format(k)]
                if accredit in ['Yes','No']:
                    accredit_info[k] = "{} under ISO accreditation 17025:2005".format(["[cross] Not validated","[tick] Validated"][accredit == "Yes"])
                elif accredit == 'N/A':
                    accredit_info[k] = "Not Applicable"
                else:
                    self.LOG.error("Accreditation step {} for project {} is found, but any value is not set".format(k,self.project_name))
            except KeyError:
                ## For "finished library" projects, set certain accredation steps as "NA" even if not set by default
                if k in ['library_preparation','data_analysis'] and self.proj.get('application') == "Finished library":
                    accredit_info[k] = "Not Applicable"
                else:
                    self.LOG.error("Could not find accreditation info for step {} for project {}".format(k,self.project_name))
        return accredit_info


    def get_lane_info(self, key, lane_info, reads, as_million=False):
        """Get the average value of gives key from given lane info
        
        :param str key: key to be fetched
        :param dict lane_info: a dictionary with required lane info
        :param str reads: number of reads for keys to be fetched
        """
        try:
            v = np.mean([float(lane_info.get('{} R{}'.format(key, str(r)))) for r in range(1,int(reads)+1)])
            return str(int(v/1000000)) if as_million else str(round(v,2))
        except TypeError:
            return
