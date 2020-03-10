#!/usr/bin/env python

""" Class for generating project reports
Note: Much of this code was written by Pontus and lifted from
the SciLifeLab repo - see
https://github.com/senthil10/scilifelab/blob/edit_report/scilifelab/report/sequencing_report.py
"""

import os
import re
import numpy as np
import unicodedata

from datetime import datetime
from collections import OrderedDict, defaultdict
from string import ascii_uppercase as alphabets
from ngi_reports.common import project_summary
from ngi_reports.utils import statusdb, nbis_xml_generator
from ConfigParser import NoSectionError, NoOptionError

class Report(project_summary.CommonReport):

    ## initialize class and assign basic variables
    def __init__(self, config, LOG, working_dir, **kwargs):
        # Initialise the parent class
        # This will grab info from the Piper XML files if found
        super(Report, self).__init__(config, LOG, working_dir, **kwargs)

        ## Project name - collect from the command line if we have it
        self.project_name = kwargs.get('project', self.project_info.get('ngi_name'))
        if not self.project_name:
            self.LOG.error("No project name/id provided - please specify using '--project'")
            raise SystemExit

        ## Check and exit if signature not provided
        if not kwargs.get('signature'):
            self.LOG.error("It is required to provide Signature/Name while generating 'project_summary' report, see -s opition in help")
            raise SystemExit
        else:
            self.project_info['signature'] = kwargs.get('signature')

        ## Get connections to the databases in StatusDB
        self.LOG.info("Connecting to statusDB...")
        pcon = statusdb.ProjectSummaryConnection()
        assert pcon, "Could not connect to {} database in StatusDB".format("project")
        fcon = statusdb.FlowcellRunMetricsConnection()
        assert fcon, "Could not connect to {} database in StatusDB".format("flowcell")
        xcon = statusdb.X_FlowcellRunMetricsConnection()
        assert xcon, "Could not connect to {} database in StatusDB".format("x_flowcells")
        self.LOG.info("...connected")

        ## Get the project from statusdb, make call according to id or name
        id_view, pid_as_uppmax_dest = (True, True) if re.match('^P\d+$', self.project_name) else (False, False)
        self.proj = pcon.get_entry(self.project_name, use_id_view=id_view)
        if not self.proj:
            self.LOG.error("No such project name/id '{}', check if provided information is right".format(self.project_name))
            raise KeyError
        self.project_name = self.proj.get('project_name')

        ## Report filename
        self.report_fn = "{}_project_summary".format(self.project_name)
        ## Bail If the data source is not lims (old projects)
        if self.proj.get('source') != 'lims':
            self.LOG.error("The source for data for project {} is not LIMS.".format(self.project_name))
            raise BaseException

        ## Helper vars
        self.seq_methods, self.sample_qval = (OrderedDict(), defaultdict(dict))
        self.proj_details = self.proj.get('details',{})
        self.project_info['skip_fastq'] = kwargs.get('skip_fastq')
        self.project_info['cluster'] = kwargs.get('cluster')
        self.project_info['not_as_million'] = kwargs.get('not_as_million')

        ## Check if it is an aborted project before proceding
        if "aborted" in self.proj_details:
            self.LOG.warn("Project {} was aborted, so not proceeding.".format(self.project_name))
            raise SystemExit

        ## Get information for the reports from statusdb
        self.project_info['ngi_name'] = self.project_name
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
        self.project_info['reference']['organism'] = self.organism_names.get(self.project_info['reference']['genome'], None)
        self.project_info['user_ID'] = self.to_ascii(self.proj_details.get('customer_project_reference',''))
        self.project_info['num_lanes'] = self.proj_details.get('sequence_units_ordered_(lanes)')
        if 'hdd' in self.proj.get('uppnex_id','').lower():
            self.project_info['cluster'] = 'hdd'
        else:
            self.project_info['cluster'] = 'grus'
        self.project_info['best_practice'] = False if self.proj_details.get('best_practice_bioinformatics','No') == "No" else True
        self.project_info['library_construction'] = self.get_library_method()
        self.project_info['is_finished_lib'] = True if "by user" in self.project_info['library_construction'].lower() else False
        self.project_info['accredit'] = self.get_accredit_info(['library_preparation','sequencing','data_processing','data_analysis'])
        self.project_info['total_lanes'] = 0
        self.project_info['missing_fc'] = False
        self.project_info['is_hiseqx'] = False
        self.project_info['aborted_samples'] = OrderedDict()
        self.project_info['seq_setup'] = self.proj_details.get('sequencing_setup')

        self.samples_to_include = kwargs.get('samples', [])
        if self.samples_to_include:
            self.LOG.info('"--samples" option is passed, will only include samples {}'.format(", ".join(self.samples_to_include)))

        ## Collect information about the sample preps and collect aborted samples
        for sample_id, sample in sorted(self.proj.get('samples', {}).iteritems()):
            if self.samples_to_include and sample_id not in self.samples_to_include:
                continue
            self.LOG.info('Processing sample {}'.format(sample_id))
            ## Check if the sample is aborted before processing
            if sample.get('details',{}).get('status_(manual)') == "Aborted":
                self.LOG.info('Sample {} is aborted, so skipping it'.format(sample_id))
                self.project_info['aborted_samples'][sample_id] = {'user_id': sample.get('customer_name','NA'), 'status':'Aborted'}
                continue

            ## Basic fields from Project database
            self.samples_info[sample_id] = {'ngi_id': sample_id}

            ## get total reads if avialable or mark sample as not sequenced
            try:
                self.samples_info[sample_id]['total_reads'] = "{:.2f}".format(float(sample['details']['total_reads_(m)']))
            except KeyError:
                self.LOG.warn("Sample {} doesn't have total reads, so adding it to NOT sequenced samples list.".format(sample_id))
                self.project_info['aborted_samples'][sample_id] = {'user_id': sample.get('customer_name','NA'), 'status':'Not sequenced'}
                ## dont gather unnecessary information if not going to be looked up
                if not kwargs.get('yield_from_fc'):
                    del self.samples_info[sample_id]
                    continue

            ## special characters should be removed
            self.samples_info[sample_id]['customer_name'] = self.to_ascii(sample.get('customer_name','NA'))
            self.samples_info[sample_id]['preps'] = {}

            ## Go through each prep for each sample in the Projects database
            for prep_id, prep in sample.get('library_prep', {}).iteritems():
                self.samples_info[sample_id]['preps'][prep_id] = {'label': prep_id }
                if not prep.get('reagent_label'):
                    self.LOG.warn("Could not fetch barcode for sample {} in prep {}".format(sample_id, prep_id))
                    self.samples_info[sample_id]['preps'][prep_id]['barcode'] = "NA"
                    self.samples_info[sample_id]['preps'][prep_id]['qc_status'] = "NA"
                else:
                    self.samples_info[sample_id]['preps'][prep_id]['barcode'] = prep.get('reagent_label', 'NA')
                if not prep.get('prep_status'):
                    self.LOG.warn("Could not fetch prep-status for sample {} in prep {}".format(sample_id, prep_id))
                else:
                    self.samples_info[sample_id]['preps'][prep_id]['qc_status'] = prep.get('prep_status', 'NA')

                #get average fragment size from lastest validation step if exists not for PCR-free libs
                if 'pcr-free' in self.project_info['library_construction'].lower():
                    self.LOG.info("PCR-free library was used, so setting fragment size as NA")
                    self.samples_info[sample_id]['preps'][prep_id]['avg_size'] = "NA"
                else:
                    try:
                        lib_valids = prep['library_validation']
                        keys = sorted([k for k in lib_valids.keys() if re.match('^[\d\-]*$',k)], key=lambda k: datetime.strptime(lib_valids[k]['start_date'], "%Y-%m-%d"), reverse=True)
                        self.samples_info[sample_id]['preps'][prep_id]['avg_size'] = re.sub(r'(\.[0-9]{,2}).*$', r'\1', str(lib_valids[keys[0]]['average_size_bp']))
                    except:
                        self.LOG.warn("No library validation step found or no sufficient info for sample {}".format(sample_id))
                        self.samples_info[sample_id]['preps'][prep_id]['avg_size'] = "NA"

            if not self.samples_info[sample_id]['preps']:
                self.LOG.warn('No library prep information was available for sample {}'.format(sample_id))

        ## collect all the flowcell this project was run
        self.flowcell_info.update(fcon.get_project_flowcell(self.project_info['ngi_id'], self.proj.get('open_date','2015-01-01')))
        self.flowcell_info.update(xcon.get_project_flowcell(self.project_info['ngi_id'], self.proj.get('open_date','2015-01-01')))

        ## Collect required information for all flowcell run for the project
        for fc in self.flowcell_info.values():
            fc_name = fc['name']
            if fc_name in kwargs.get('exclude_fc'):
                del self.flowcell_info[fc_name]
                continue

            # get database document from appropriate database
            if fc['db'] == 'x_flowcells':
                fc_obj = xcon.get_entry(fc['run_name'])
            else:
                fc_obj = fcon.get_entry(fc['run_name'])

            # set the fc type
            fc_inst = fc_obj.get('RunInfo', {}).get('Instrument','')
            if fc_inst.startswith('ST-'):
                fc['type'] = 'HiSeqX'
                self.project_info['is_hiseqx'] = True
                fc_runp = fc_obj.get('RunParameters',{}).get('Setup',{})
            elif '-' in fc_name:
                fc['type'] = 'MiSeq'
                fc_runp = fc_obj.get('RunParameters',{})
            elif fc_inst.startswith('A'):
                fc['type'] = 'NovaSeq6000'
                fc_runp = fc_obj.get('RunParameters',{})
            elif fc_inst.startswith('NS'):
                fc['type'] = 'NextSeq500'
                fc_runp = fc_obj.get('RunParameters',{})
            else:
                fc['type'] = 'HiSeq2500'
                fc_runp = fc_obj.get('RunParameters',{}).get('Setup',{})
            fc_illumina = fc_obj.get('illumina',{})
            fc_lane_summary = fc_obj.get('lims_data', {}).get('run_summary', {})
            self.flowcell_info[fc_name]['lanes'] = OrderedDict()

            ## Get sequecing method for the flowcell
            seq_template = "{}) Samples were sequenced on {} ({}) with a {} setup "\
                           "using {}. The Bcl to FastQ conversion was performed using {} from the CASAVA software "\
                           "suite. The quality scale used is Sanger / phred33 / Illumina 1.8+."
            run_setup = fc_obj.get("run_setup")
            if fc['type'] == 'NovaSeq6000':
                fc_chem = "'{}' workflow in '{}' mode flowcell".format(fc_runp.get('WorkflowType'), fc_runp.get('RfidsInfo', {}).get('FlowCellMode'))
            elif fc['type'] == 'NextSeq500':
                fc_chem = "'{}-Output' chemistry".format(fc_runp.get('Chemistry').replace("NextSeq ", ""))
            else:
                fc_chem = "'{}' chemistry".format(fc_runp.get('ReagentKitVersion', fc_runp.get('Sbs')))
            seq_plat = fc['type']
            try:
                casava = fc_obj['DemultiplexConfig'].values()[0]['Software']['Version']
            except KeyError, IndexError:
                casava = None
            if seq_plat == "MiSeq":
                seq_software = "MSC {}/RTA {}".format(fc_runp.get("MCSVersion"),fc_runp.get("RTAVersion"))
            elif seq_plat == "NextSeq500":
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName", fc_runp.get("Application", fc_runp.get("Setup").get("ApplicationName"))),
                                                     fc_runp.get("ApplicationVersion", fc_runp.get("Setup").get("ApplicationVersion")),fc_runp.get("RTAVersion", fc_runp.get("RtaVersion")))
            else:
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName", fc_runp.get("Application")),
                                                     fc_runp.get("ApplicationVersion"), fc_runp.get("RTAVersion", fc_runp.get("RtaVersion")))                
            tmp_method = seq_template.format("SECTION", seq_plat, seq_software, run_setup, fc_chem, casava)

            ## to make sure the sequencing methods are unique
            if tmp_method not in self.seq_methods.keys():
                self.seq_methods[tmp_method] = alphabets[len(self.seq_methods.keys())]
            self.flowcell_info[fc_name]['seq_meth'] = self.seq_methods[tmp_method]

            ## Collect quality info for samples and collect lanes of interest
            for stat in fc_illumina.get('Demultiplex_Stats',{}).get('Barcode_lane_statistics',[]):
                try:
                    if re.sub('_+','.',stat['Project'],1) != self.project_name and stat['Project'] != self.project_name:
                        continue
                    sample, lane, barcode = (stat['Sample'] if fc['db'] == "x_flowcells" else stat['Sample ID'], stat['Lane'], stat['Barcode sequence'] if fc['db'] == "x_flowcells" else stat['Index'])
                    if self.samples_to_include and sample not in self.samples_to_include:
                        continue
                    try:
                        if fc['db'] == "flowcell":
                            qval_key, base_key = ('% of >= Q30 Bases (PF)', '# Reads')
                        elif fc['db'] == "x_flowcells":
                            qval_key, base_key = ('% >= Q30bases', 'PF Clusters')
                        r_idx = '{}_{}_{}'.format(lane, fc_name, barcode)
                        r_num, r_len = map(int, run_setup.split('x'))
                        qval = float(stat.get(qval_key))
                        pfrd = int(stat.get(base_key).replace(',',''))
                        pfrd = pfrd/2 if fc['db'] == "flowcell" else pfrd
                        base = pfrd * r_num * r_len
                        self.sample_qval[sample][r_idx] = {'qval': qval, 'reads': pfrd, 'bases': base}
                    except (TypeError, ValueError, AttributeError) as e:
                        self.LOG.warn("Something went wrong while fetching Q30 for sample {} with barcode {} in FC {} at lane {}".format(sample, barcode, fc_name, lane))
                        pass
                    ## collect lanes of interest to proceed later
                    if lane not in self.flowcell_info[fc_name]['lanes']:
                        lane_sum = fc_lane_summary.get(lane, fc_lane_summary.get('A',{}))
                        self.flowcell_info[fc_name]['lanes'][lane] = {'id': lane,
                                                                      'cluster': self.get_lane_info('Reads PF (M)' if 'NovaSeq' in fc['type'] else 'Clusters PF',lane_sum,
                                                                                                     run_setup[0], False if 'NovaSeq' in fc['type'] else True),
                                                                      'avg_qval': self.get_lane_info('% Bases >=Q30',lane_sum,run_setup[0]),
                                                                      'phix': kwargs.get('fc_phix',{}).get(fc_name, {}).get(lane, self.get_lane_info('% Error Rate',lane_sum,run_setup[0]))}

                        ## Check if the above created dictionay have all info needed
                        for k,v in self.flowcell_info[fc_name]['lanes'][lane].iteritems():
                            if not v:
                                self.LOG.warn("Could not fetch {} for FC {} at lane {}".format(k, fc_name, lane))
                except KeyError:
                    continue

        ## Check if there are FCs processed
        if not self.flowcell_info:
            self.LOG.warn('There is no flowcell to process for project {}'.format(self.project_name))
            self.project_info['missing_fc'] = True

        ## give proper section name for the methods
        self.project_info['sequencing_methods'] = "\n\n".join([m.replace("SECTION",self.seq_methods[m]) for m in self.seq_methods])
        ## Check if sequencing info is complete
        if "None" in self.project_info['sequencing_methods']:
            self.LOG.warn("Sequencing methods have some missing information, kindly check.")

        if self.sample_qval and kwargs.get('yield_from_fc'):
            self.LOG.info("'yield_from_fc' option was given so will compute the yield from collected flowcells")
            for sample in self.samples_info.keys():
                if sample not in self.sample_qval.keys():
                    del self.samples_info[sample]

        ## calculate average Q30 over all lanes and flowcell
        for sample in sorted(self.sample_qval.keys()):
            try:
                qinfo = self.sample_qval[sample]
                total_qvalsbp, total_bases, total_reads = (0, 0, 0)
                for k in qinfo:
                    total_qvalsbp += qinfo[k]['qval'] * qinfo[k]['bases']
                    total_bases += qinfo[k]['bases']
                    total_reads += qinfo[k]['reads']
                avg_qval = float(total_qvalsbp)/total_bases if total_bases else float(total_qvalsbp)
                self.samples_info[sample]['qscore'] = round(avg_qval, 2)
                ## Get/overwrite yield from the FCs computed instead of statusDB value
                if kwargs.get('yield_from_fc') and total_reads:
                    self.samples_info[sample]['total_reads'] = total_reads if self.project_info.get('not_as_million') else "{:.2f}".format(total_reads/float(1000000))
                    if sample in self.project_info['aborted_samples']:
                        self.LOG.info("Sample {} was sequenced, so removing it from NOT sequenced samples list".format(sample))
                        del self.project_info['aborted_samples'][sample]
            except (TypeError, KeyError):
                self.LOG.error("Could not calcluate average Q30 for sample {}".format(sample))


    ###############################################################################
    ##### Create table text and header explanation from collected information #####
    ###############################################################################

        ## sample_info table
        sample_header = ['NGI ID', 'User ID', '#reads' if self.project_info.get('not_as_million') else 'Mreads', '>=Q30']
        sample_filter = ['ngi_id', 'customer_name', 'total_reads', 'qscore']

        self.tables_info['tables']['sample_info'] = self.create_table_text(sorted(self.samples_info.values(), key=lambda d: d['ngi_id']), filter_keys=sample_filter, header=sample_header)
        self.tables_info['header_explanation']['sample_info'] = "* _NGI ID:_ Internal NGI sample indentifier\n"\
                                                                "* _User ID:_ User submitted name for a sample\n"\
                                                                "* _Mreads:_ Total million reads (or pairs) for a sample\n"\
                                                                "* _>=Q30:_ Aggregated percentage of bases that have quality score more the Q30"
        if self.project_info.get('not_as_million'):
            self.tables_info['header_explanation']['sample_info'] = self.tables_info['header_explanation']['sample_info'].replace("_Mreads:_ Total million reads (or pairs) for a sample",
                                                                                                                                  "_#reads:_ Total number of reads (or pairs) for a sample")
        ## library_info table
        library_header = ['NGI ID', 'Index', 'Lib Prep', 'Avg. FS', 'Lib QC']
        library_filter = ['ngi_id', 'barcode', 'label', 'avg_size', 'qc_status']
        library_list = []
        for s, v in self.samples_info.items():
            for p in v.get('preps',{}).values():
                p['ngi_id'] = s
                library_list.append(p)
        self.tables_info['tables']['library_info'] = self.create_table_text(sorted(library_list, key=lambda d: d['ngi_id']), filter_keys=library_filter, header=library_header)
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
        self.tables_info['tables']['lanes_info'] = self.create_table_text(sorted(lanes_list, key=lambda d: "{}_{}".format(d['date'],d['id'])), filter_keys=lanes_filter, header=lanes_header)
        self.tables_info['header_explanation']['lanes_info'] = "* _Date:_ Date of sequencing\n"\
                                                               "* _Flowcell:_ Flowcell identifier\n"\
                                                               "* _Lane:_ Flowcell lane number\n"\
                                                               "* _Clusters:_ Number of clusters that passed the read filters (millions)\n"\
                                                               "* _>=Q30:_ Aggregated percentage of bases that have a quality score of more than Q30\n"\
                                                               "* _PhiX:_ Average PhiX error rate for the lane\n"\
                                                               "* _Method:_ Sequencing method used. See above for description\n"


    ######################################################
    ##### Create XML text from collected information #####
    ######################################################

        self.xml_info = {}
        if kwargs.get('xml', False):
            self.LOG.info("Fetching information for xml generation")
            try:
                xgen = nbis_xml_generator.xml_generator(self.proj, # statusdb project object
                                                        ignore_lib_prep=kwargs.get("ignore_lib_prep"), # boolean to ignore prep
                                                        flowcells=self.flowcell_info, # sequenced FC for the project
                                                        LOG=self.LOG, # log object for logging
                                                        pcon=pcon, # StatusDB project connection
                                                        fcon=fcon, # StatusDB flowcells connection
                                                        xcon=xcon) # StatusDB xflowcells connection
                self.xml_info.update(xgen.generate_xml(return_string_dict=True))
            except Exception as e:
                self.LOG.warning("Fetching XML information failed due to '{}'".format(e))


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
            dates.append("_All samples sequenced:_ {}".format(self.proj.get('project_summary',{}).get('all_samples_sequenced')))
        if self.creation_date:
            dates.append("_Report date:_ {}".format(self.creation_date))
        return ", ".join(dates)


    def get_library_method(self):
        """Get the library construction method and return as formatted string
        """
        if self.proj.get('application') == "Finished library":
            return "Library was prepared by user."
        try:
            lib_meth_pat = r'^(.*?),(.*?),(.*?),(.*?)[\[,](.*)$' #Input, Type, Option, Category -/, doucment number
            lib_head = ['Input', 'Type', 'Option', 'Category']
            lib_meth = re.search(lib_meth_pat, self.proj_details['library_construction_method'])
            if lib_meth:
                lib_meth_list = lib_meth.groups()[:4] #not interested in the document number
                lib_list = []
                for name,value in zip(lib_head, lib_meth_list):
                    value = value.strip() #remove empty space(s) at the ends
                    if value == 'By user':
                        return "Library was prepared by user."
                    if value and value != "-":
                        lib_list.append("* {}: {}".format(name, value))
                return ("\n".join(lib_list))
            else:
                self.LOG.error("Library method is not mentioned in expected format for project {}".format(self.project_name))
                return None
        except KeyError:
            self.LOG.error("Could not find library construction method for project {} in statusDB".format(self.project_name))
            return None


    def get_accredit_info(self,keys):
        """Get swedac accreditation info for given step 'k'

        :param list keys: step names which are keys in project database
        """
        accredit_info = {}
        for k in keys:
            try:
                accredit = self.proj_details['accredited_({})'.format(k)]
                if accredit in ['Yes','No']:
                    accredit_info[k] = "{} under ISO accreditation 17025".format(["[cross] Not validated","[tick] Validated"][accredit == "Yes"])
                elif accredit == 'N/A':
                    accredit_info[k] = "Not Applicable"
                else:
                    self.LOG.error("Accreditation step {} for project {} is found, but any value is not set".format(k,self.project_name))
            except KeyError:
                ## For "finished library" projects, set certain accredation steps as "NA" even if not set by default
                if k in ['library_preparation','data_analysis'] and self.project_info['library_construction'] == "Library was prepared by user.":
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
            return None

    def to_ascii(self,value):
        """Convert any non-ASCII character to its closest ASCII equivalent

        :param string value: a 'str' or 'unicode' string
        """
        if not isinstance(value, unicode):
            value = unicode(value, 'utf-8')
        return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
