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
        
        ## log file for testing purpose to be removed in the end
        missing_log = open('missing_stat/{}_project_summary.log'.format(self.project_name),'w')
        missing_log.write("project\t{}\n".format(self.project_name))
        
        ## Get information for the reports from statusdb
        self.project_info['ngi_id'] = self.proj.get('project_id')
        self.project_info['ngi_facility'] = self.proj_details.get('type')
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
        self.project_info['ordered_reads'] = [] #self.get_ordered_reads()
        self.project_info['best_practice'] = False if self.proj_details.get('best_practice_bioinformatics','No') == "No" else True
        self.project_info['status'] = "Sequencing done" if self.proj.get('project_summary', {}).get('all_samples_sequenced') else "Sequencing ongoing"
        self.project_info['library_construction'] = self.get_library_method()
        self.project_info['accredit'] = self.get_accredit_info(['library_preparation','sequencing','data_processing','data_analysis'])
        self.project_info['missing_prep'] = 0
        self.project_info['missing_fc'] = False
        self.project_info['aborted_samples'] = {}

        ## test purpose for missing keys, to be removed at last
        missing_log.write("application\t{}\n".format(self.project_info['application']))
        missing_log.write("open_date\t{}\n".format(self.proj.get('open_date')))
        missing_log.write("close_date\t{}\n".format(self.proj.get('close_date')))
        missing_log.write("keys_project\n")
        missing_log.write("uppmax_id\t{}\n".format("yes" if self.project_info['UPPMAX_id'] else "no"))
        missing_log.write("library_meth\t{}\n".format("yes" if self.project_info['library_construction'] else "no"))
        missing_log.write("accredit_lib\t{}\n".format("yes" if self.project_info['accredit'].get('library_preparation') else "no"))
        missing_log.write("accredit_seq\t{}\n".format("yes" if self.project_info['accredit'].get('sequencing') else "no"))
        missing_log.write("accredit_data\t{}\n".format("yes" if self.project_info['accredit'].get('data_processing') else "no"))
        missing_log.write("accredit_analysis\t{}\n".format("yes" if self.project_info['accredit'].get('data_analysis') else "no"))
        missing_log.write("keys_sample\n")
        ck_cn, ck_in, ck_fs, ck_st = (0, 0, 0, 0)
        
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
            self.samples_info[sample_id]['customer_name'] = sample.get('customer_name','')
            self.samples_info[sample_id]['total_reads'] = sample.get('details',{}).get('total_reads_(m)')
            self.samples_info[sample_id]['reads_min'] = sample.get('details',{}).get('reads_min')
            if self.samples_info[sample_id]['total_reads'] == None:
                self.LOG.warn("Sample {} dont have total reads, so adding it to NOT sequenced samples list.".format(sample_id))
                self.project_info['aborted_samples'][sample_id] = {'user_id': sample.get('customer_name',''), 'status':'Not sequenced'}
                del self.samples_info[sample_id]
                continue
            if self.samples_info[sample_id]['reads_min']:
                self.project_info['ordered_reads'].append("{}M".format(self.samples_info[sample_id]['reads_min']))
                self.samples_info[sample_id]['seq_status'] = ['FAIL','PASS'][float(self.samples_info[sample_id]['total_reads']) > \
                                                                         float(self.samples_info[sample_id]['reads_min'])]
            
            self.samples_info[sample_id]['preps'] = {}
            self.samples_info[sample_id]['flowcell'] = []

            ## Get sample objects from statusdb
            s_ids = []
            for sample_run_doc in scon.get_project_sample(sample_id, sample_prj=self.project_name):
                fc_name = sample_run_doc.get('flowcell')
                fc_run_name = "{}_{}".format(sample_run_doc.get('date'), fc_name)
                if fc_name not in self.flowcell_info.keys():
                    self.flowcell_info[fc_name] = {'name':fc_name,'run_name':fc_run_name, 'date': sample_run_doc.get('date')}
                if fc_run_name not in self.samples_info[sample_id]['flowcell']:
                    self.samples_info[sample_id]['flowcell'].append(fc_run_name)
                s_ids.append(sample_run_doc.get("_id"))

            ## Go through each prep in the Projects database
            for prep_id, prep in sample.get('library_prep', {}).iteritems():
                # If we have sample_run_metrics then it should have been sequenced
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
                ## test purpose for missing keys, to be removed at last
                if not ck_in and not prep.get('reagent_label',''):
                    ck_in = 1
                if not ck_st and not prep.get('prep_status',''):
                    ck_st = 1
                if not ck_fs and not self.samples_info[sample_id]['preps'][prep_id].get('avg_size',''):
                    ck_fs = 1
            ## test purpose for missing keys, to be removed at last
            if not ck_cn and not sample.get('customer_name',''):
                ck_cn = 1
        
            if not self.samples_info[sample_id]['preps']:
                self.LOG.warn('No library prep information was available for sample {}'.format(sample_id))
                self.project_info['missing_prep'] += 1
                ck_in, ck_fs, ck_st = (1, 1, 1)
        
        if not self.flowcell_info:
            self.LOG.warn('There is no flowcell to preocess for project {}'.format(self.project_name))
            self.project_info['missing_fc'] = True
            
#        import pdb; pdb.set_trace()
        ## test purpose for missing keys, to be removed at last
        if len(self.project_info['aborted_samples']) == len(self.proj.get('samples', {})):
            ck_in, ck_fs, ck_st = (1, 1, 1)
        missing_log.write("customer_name\t{}\n".format("no" if ck_cn else "yes"))
        missing_log.write("index_sequence\t{}\n".format("no" if ck_in else "yes"))
        missing_log.write("library_qc\t{}\n".format("no" if ck_st else "yes"))
        missing_log.write("fragment_size\t{}\n".format("no" if ck_fs else "yes"))
        missing_log.write("keys_flowcell\n")
        ck_qs, ck_bs, ck_cl, ck_ph, ck_aq = (0, 0, 0, 0, 0)
        
            
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
                           "chemistry. The Bcl to Fastq conversion was performed using {} from the CASAVA software suite. The "\
                           "quality scale used is Sanger / phred33 / Illumina 1.8+."
            run_setup = fc_obj.get("run_setup")
            fc_chem = fc_runp.get('ReagentKitVersion') if fc_runp.get('ReagentKitVersion') else fc_runp.get('Sbs')
            seq_plat = ["HiSeq2500","MiSeq"]["MCSVersion" in fc_runp.keys()]
            clus_meth = ["cBot","onboard clustering"][seq_plat == "MiSeq" or fc_runp.get("ClusteringChoice","") == "OnBoardClustering"]
            casava = fc_obj.get('DemultiplexConfig',{}).values()[0].get('Software',{}).get('Version')
            if seq_plat == "MiSeq":
                seq_software = "MSC {}/RTA {}".format(fc_runp.get("MCSVersion"),fc_runp.get("RTAVersion"))
            else:
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName"),fc_runp.get("ApplicationVersion"),fc_runp.get("RTAVersion"))
            tmp_method = seq_template.format("SECTION", clus_meth, seq_plat, seq_software, run_setup, fc_chem, casava)
            
            ## to make sure the sequencing methods are uniq
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
                        ## test purpose for missing keys, to be removed at last
                        if not ck_qs and not stat.get('% of >= Q30 Bases (PF)'):
                            ck_qs = 1
                        if not ck_bs and not stat.get('# Reads'):
                            ck_bs = 1
                        pass
                    # collect lanes to proceed later
                    if lane not in self.flowcell_info[fc_name]['lanes']:
                        self.flowcell_info[fc_name]['lanes'][lane] = {'id': lane}
                except KeyError:
                    continue
            
            ## proceed through the lane summary and get rquired info
            for lane in self.flowcell_info[fc_name]['lanes'].keys():
                # for a miseq run there will be only one lane named 'A'
                lane_sum = fc_run_summary.get(lane, fc_run_summary.get('A',{}))
                self.flowcell_info[fc_name]['lanes'][lane]['cluster'] = self.get_lane_info('Clusters PF',lane_sum,run_setup[0],True)
                self.flowcell_info[fc_name]['lanes'][lane]['phix'] = self.get_lane_info('% Error Rate',lane_sum,run_setup[0])
                self.flowcell_info[fc_name]['lanes'][lane]['avg_qval'] = self.get_lane_info('% Bases >=Q30',lane_sum,run_setup[0])
            
                ## test purpose for missing keys, to be removed at last
                if not ck_cl and not self.flowcell_info[fc_name]['lanes'][lane]['cluster']:
                    ck_cl = 1
                if not ck_ph and not self.flowcell_info[fc_name]['lanes'][lane]['phix']:
                    ck_ph = 1
                if not ck_aq and not self.flowcell_info[fc_name]['lanes'][lane]['avg_qval']:
                    ck_aq = 1
        
        ## test purpose for missing keys, to be removed at last
        if len(self.project_info['aborted_samples']) == len(self.proj.get('samples', {})):
            ck_qs, ck_bs, ck_cl, ck_ph, ck_aq = (1, 1, 1, 1, 1)
        missing_log.write("demulti_quality\t{}\n".format("no" if ck_qs else "yes"))
        missing_log.write("demulti_bases\t{}\n".format("no" if ck_bs else "yes"))
        missing_log.write("lane_cluster\t{}\n".format("no" if ck_cl else "yes"))
        missing_log.write("lane_phix\t{}\n".format("no" if ck_ph else "yes"))
        missing_log.write("lane_quality\t{}\n".format("no" if ck_aq else "yes"))
        missing_log.close()
        
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
            except (TypeError, KeyError):
                self.LOG.error("Could not calcluate average Q30 for sample {}".format(sample))


    #####################################################
    ##### Helper methods to get certain information #####
    #####################################################

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
                return ''
        except KeyError:
            self.LOG.error("Could not find library construction method for project {} in statusDB".format(self.project_name))
            return ''


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
                else:
                    accredit_info[k] = accredit.replace("N/A","Not Applicable")
            except KeyError:
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
            return ''
