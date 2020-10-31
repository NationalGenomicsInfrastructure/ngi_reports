""" Define various entities and populate them
"""
import re
import numpy as np
from collections import defaultdict, OrderedDict
from datetime import datetime

from ngi_reports.utils import statusdb


class Sample:
    """Sample class
    """
    def __init__(self):
        self.customer_name = ''
        self.ngi_id        = ''
        self.preps         = {}
        self.qscore        = ''
        self.total_reads   = ''
        self.initial_qc    = { 'initial_qc_status' : '',
                                'concentration': '',
                                'conc_units':'',
                                'volume_(ul)': '',
                                'amount_(ng)': '',
                                'rin': ''
                                }
        self.well_location = ''

class Prep:
    """Prep class
    """
    def __init__(self):
        self.avg_size    = 'NA'
        self.barcode     = 'NA'
        self.label       = ''
        self.qc_status   = 'NA'

class Flowcell:
    """Flowcell class
    """
    def __init__(self):
        self.date      = ''
        self.lanes     = OrderedDict()
        self.name      = ''
        self.run_name  = ''
        self.run_setup = []
        self.seq_meth  = ''
        self.type      = ''
        self.run_params = {}
        self.chemistry = {}
        self.casava = None
        self.seq_software = {}

class Lane:
    """Lane class
    """
    def __init__(self):
        self.avg_qval = ''
        self.cluster  = ''
        self.id       = ''
        self.phix     = ''

    def set_lane_info(self, to_set, key, lane_info, reads, as_million=False):
        """Set the average value of gives key from given lane info
        :param str to_set: class parameter to be set
        :param str key: key to be fetched
        :param dict lane_info: a dictionary with required lane info
        :param str reads: number of reads for keys to be fetched
        """
        try:
            v = np.mean([float(lane_info.get('{} R{}'.format(key, str(r)))) for r in range(1,int(reads)+1)])
            val = '{:.2f}'.format(round(v/1000000, 2)) if as_million else '{:.2f}'.format(round(v, 2))
        except TypeError:
            val = None

        if to_set == 'cluster':
            self.cluster = val
        elif to_set == 'avg_qval':
            self.avg_qval = val
        elif to_set == 'fc_phix':
            self.phix = val


class Project:
    """Project class
    """
    def __init__(self):
        self.aborted_samples = OrderedDict()
        self.samples = OrderedDict()
        self.flowcells = {}
        self.accredited = { 'library_preparation': 'N/A',
                            'data_processing': 'N/A',
                            'sequencing': 'N/A',
                            'data_analysis':'N/A'
                            }
        self.application = ''
        self.best_practice = False
        self.cluster = ''
        self.contact = ''
        self.dates = { 'order_received': None,
                        'open_date':  None,
                        'first_initial_qc_start_date': None,
                        'contract_received': None,
                        'samples_received': None,
                        'queue_date': None,
                        'all_samples_sequenced': None
                    }
        self.is_finished_lib = False
        self.is_hiseqx = False
        self.library_construction  = ''
        self.missing_fc  = False
        self.ngi_facility = ''
        self.ngi_name = ''
        self.not_as_million  = False
        self.num_samples = 0
        self.num_lanes = 0
        self.ngi_id = ''
        self.reference = { 'genome': None,
                            'organism': None }
        self.report_date = ''
        self.sequencing_setup = ''
        self.skip_fastq = False
        self.user_ID = ''


    class AbortedSampleInfo:
        """Aborted Sample info class
        """
        def __init__(self, user_id, status):
            self.status = status
            self.user_id = user_id


    def populate(self, log, organism_names, **kwargs):

        project = kwargs.get('project', '')
        if not project:
            raise SystemExit()
        self.skip_fastq = kwargs.get('skip_fastq')
        self.cluster = kwargs.get('cluster')
        self.not_as_million = kwargs.get('not_as_million')

        pcon = statusdb.ProjectSummaryConnection()
        assert pcon, 'Could not connect to {} database in StatusDB'.format('project')

        if re.match('^P\d+$', project):
            self.ngi_id = project
            id_view, pid_as_uppmax_dest = (True, True)
        else:
            self.ngi_name = project
            id_view, pid_as_uppmax_dest = (False, False)

        proj = pcon.get_entry(project, use_id_view=id_view)
        if not proj:
            log.error('No such project name/id "{}", check if provided information is right'.format(project))
            raise KeyError
        self.ngi_name = proj.get('project_name')

        if proj.get('source') != 'lims':
            log.error('The source for data for project {} is not LIMS.'.format(project))
            raise BaseException

        proj_details = proj.get('details',{})

        if 'aborted' in proj_details:
            log.warn('Project {} was aborted, so not proceeding.'.format(project))
            raise SystemExit

        if not id_view:
            self.ngi_id = proj.get('project_id')

        for date in self.dates:
            self.dates[date] = proj_details.get(date, None)

        if proj.get('project_summary',{}).get('all_samples_sequenced'):
            self.dates['all_samples_sequenced'] = proj.get('project_summary',{}).get('all_samples_sequenced')


        self.contact               = proj.get('contact')
        self.application           = proj.get('application')
        self.num_samples           = proj.get('no_of_samples')
        self.ngi_facility          = 'Genomics {} Stockholm'.format(proj_details.get('type')) if proj_details.get('type') else None
        self.reference['genome']   = None if proj.get('reference_genome') == 'other' else proj.get('reference_genome')
        self.reference['organism'] = organism_names.get(self.reference['genome'], None)
        self.user_ID               = proj_details.get('customer_project_reference','')
        self.num_lanes             = proj_details.get('sequence_units_ordered_(lanes)')

        if 'hdd' in proj.get('uppnex_id','').lower():
            self.cluster = 'hdd'
        else:
            self.cluster = 'grus'

        self.best_practice          = False if proj_details.get('best_practice_bioinformatics','No') == 'No' else True
        self.library_construction   = self.get_library_method(self.ngi_name, self.application, proj_details['library_construction_method'])
        self.is_finished_lib        = True if 'by user' in self.library_construction.lower() else False

        for key in self.accredited:
            self.accredited[key] = proj_details.get('accredited_({})'.format(key))

        if 'hiseqx' in proj_details.get('sequencing_platform', ''):
            self.is_hiseqx = True

        self.sequencing_setup = proj_details.get('sequencing_setup')

        for sample_id, sample in sorted(proj.get('samples', {}).items()):
            if kwargs.get('samples', []) and sample_id not in kwargs.get('samples', []):
                log.info('Will not include sample {} as it is not in given list'.format(sample_id))
                continue

            customer_name = sample.get('customer_name','NA')
            #Get once for a project
            if self.dates['first_initial_qc_start_date'] is not None:
                self.dates['first_initial_qc_start_date'] = sample.get('first_initial_qc_start_date')

            log.info('Processing sample {}'.format(sample_id))
            ## Check if the sample is aborted before processing
            if sample.get('details',{}).get('status_(manual)') == 'Aborted':
                log.info('Sample {} is aborted, so skipping it'.format(sample_id))
                self.aborted_samples[sample_id] = AbortedSampleInfo(customer_name, 'Aborted')
                continue

            samObj               = Sample()
            samObj.ngi_id        = sample_id
            samObj.customer_name = customer_name
            samObj.well_location = sample.get('well_location')
            ## Basic fields from Project database
            # Initial qc
            if sample.get('initial_qc'):
                for item in samObj.initial_qc:
                    samObj.initial_qc[item] = sample['initial_qc'].get(item)

            #Library prep
            ## get total reads if available or mark sample as not sequenced
            try:
                samObj.total_reads = '{:.2f}'.format(float(sample['details']['total_reads_(m)']))
            except KeyError:
                log.warn('Sample {} doesnt have total reads, so adding it to NOT sequenced samples list.'.format(sample_id))
                self.aborted_samples[sample_id] = AbortedSampleInfo(customer_name, 'Not sequenced')
                ## dont gather unnecessary information if not going to be looked up
                if not kwargs.get('yield_from_fc'):
                    del self.samples[sample_id]
                    continue

            ## Go through each prep for each sample in the Projects database
            for prep_id, prep in list(sample.get('library_prep', {}).items()):
                prepObj = Prep()
                prepObj.label = prep_id
                if prep.get('reagent_label') and prep.get('prep_status'):
                    prepObj.barcode = prep.get('reagent_label', 'NA')
                    prepObj.qc_status = prep.get('prep_status', 'NA')
                else:
                    log.warn('Could not fetch barcode/prep status for sample {} in prep {}'.format(sample_id, prep_id))

                if 'pcr-free' not in self.library_construction:
                    if prep.get('library_validation'):
                        lib_valids = prep['library_validation']
                        keys = sorted([k for k in list(lib_valids.keys()) if re.match('^[\d\-]*$',k)], key=lambda k: datetime.strptime(lib_valids[k]['start_date'], '%Y-%m-%d'), reverse=True)
                        prepObj.avg_size = re.sub(r'(\.[0-9]{,2}).*$', r'\1', str(lib_valids[keys[0]]['average_size_bp']))
                    else:
                        log.warn('No library validation step found or no sufficient info for sample {}'.format(sample_id))

                samObj.preps[prep_id] = prepObj

            if not samObj.preps:
                log.warn('No library prep information was available for sample {}'.format(sample_id))
            self.samples[sample_id] = samObj

        #Get Flowcell data
        fcon = statusdb.FlowcellRunMetricsConnection()
        assert fcon, 'Could not connect to {} database in StatusDB'.format('flowcell')
        xcon = statusdb.X_FlowcellRunMetricsConnection()
        assert xcon, 'Could not connect to {} database in StatusDB'.format('x_flowcells')
        flowcell_info = fcon.get_project_flowcell(self.ngi_id, self.dates['open_date'])
        flowcell_info.update(xcon.get_project_flowcell(self.ngi_id, self.dates['open_date']))

        sample_qval = defaultdict(dict)

        for fc in list(flowcell_info.values()):
            if fc['name'] in kwargs.get('exclude_fc'):
                continue
            fcObj           = Flowcell()
            fcObj.name      = fc['name']
            fcObj.run_name  = fc['run_name']
            fcObj.date      = fc['date']

            # get database document from appropriate database
            if fc['db'] == 'x_flowcells':
                fc_details = xcon.get_entry(fc['run_name'])
            else:
                fc_details = fcon.get_entry(fc['run_name'])

            # set the fc type
            fc_inst = fc_details.get('RunInfo', {}).get('Instrument','')
            if fc_inst.startswith('ST-'):
                fcObj.type = 'HiSeqX'
                self.is_hiseqx = True
                fc_runp = fc_details.get('RunParameters',{}).get('Setup',{})
            elif '-' in fcObj.name :
                fcObj.type = 'MiSeq'
                fc_runp = fc_details.get('RunParameters',{})
            elif fc_inst.startswith('A'):
                fcObj.type = 'NovaSeq6000'
                fc_runp = fc_details.get('RunParameters',{})
            elif fc_inst.startswith('NS'):
                fcObj.type = 'NextSeq500'
                fc_runp = fc_details.get('RunParameters',{})
            else:
                fcObj.type = 'HiSeq2500'
                fc_runp = fc_details.get('RunParameters',{}).get('Setup',{})

            ## Fetch run setup for the flowcell
            fcObj.run_setup = fc_details.get('RunInfo').get('Reads')

            if fcObj.type == 'NovaSeq6000':
                fcObj.chemistry = {'WorkflowType' : fc_runp.get('WorkflowType'), 'FlowCellMode' : fc_runp.get('RfidsInfo', {}).get('FlowCellMode')}
            elif fcObj.type == 'NextSeq500':
                fcObj.chemistry = {'Chemistry':  fc_runp.get('Chemistry').replace('NextSeq ', '')}
            else:
                fcObj.chemistry = {'Chemistry' : fc_runp.get('ReagentKitVersion', fc_runp.get('Sbs'))}

            try:
                fcObj.casava = list(fc_details['DemultiplexConfig'].values())[0]['Software']['Version']
            except (KeyError, IndexError):
                continue

            if fcObj.type == 'MiSeq':
                fcObj.seq_software = {'RTAVersion': fc_runp.get('RTAVersion'),
                                        'ApplicationVersion': fc_runp.get('MCSVersion')
                                        }
            elif fcObj.type == 'NextSeq500':
                fcObj.seq_software = {'RTAVersion': fc_runp.get('RTAVersion', fc_runp.get('RtaVersion')),
                                        'ApplicationName': fc_runp.get('ApplicationName', fc_runp.get('Application', fc_runp.get('Setup').get('ApplicationName'))),
                                        'ApplicationVersion': fc_runp.get('ApplicationVersion', fc_runp.get('Setup').get('ApplicationVersion'))
                                        }
            else:
                fcObj.seq_software = {'RTAVersion': fc_runp.get('RTAVersion', fc_runp.get('RtaVersion')),
                                        'ApplicationName': fc_runp.get('ApplicationName', fc_runp.get('Application')),
                                        'ApplicationVersion': fc_runp.get('ApplicationVersion')
                                        }

            ## Collect quality info for samples and collect lanes of interest
            for stat in fc_details.get('illumina',{}).get('Demultiplex_Stats',{}).get('Barcode_lane_statistics',[]):
                try:
                    if re.sub('_+','.',stat['Project'],1) != self.ngi_name and stat['Project'] != self.ngi_name:
                        continue

                    lane = stat['Lane']
                    if fc['db'] == 'x_flowcells':
                        sample = stat['Sample']
                        barcode = stat['Barcode sequence']
                        qval_key, base_key = ('% >= Q30bases', 'PF Clusters')

                    else:
                        sample = stat['Sample ID']
                        barcode = stat['Index']
                        qval_key, base_key = ('% of >= Q30 Bases (PF)', '# Reads')

                    if kwargs.get('samples', []) and sample not in kwargs.get('samples', []):
                        continue

                    try:
                        r_idx = '{}_{}_{}'.format(lane, fcObj.name, barcode)
                        r_len_list = [x['NumCycles'] for x in fcObj.run_setup if x['IsIndexedRead'] == 'N']
                        r_len_list = [int(x) for x in r_len_list]
                        r_num = len(r_len_list)
                        qval = float(stat.get(qval_key))
                        pfrd = int(stat.get(base_key).replace(',',''))
                        pfrd = pfrd/2 if fc['db'] == 'flowcell' else pfrd
                        base = pfrd * sum(r_len_list)
                        sample_qval[sample][r_idx] = {'qval': qval, 'reads': pfrd, 'bases': base}

                    except (TypeError, ValueError, AttributeError) as e:
                        log.warn('Something went wrong while fetching Q30 for sample {} with barcode {} in FC {} at lane {}'.format(sample, barcode, fcObj.name, lane))
                        pass
                    ## collect lanes of interest to proceed later
                    fc_lane_summary = fc_details.get('lims_data', {}).get('run_summary', {})
                    if lane not in fcObj.lanes:
                        laneObj = Lane()
                        lane_sum = fc_lane_summary.get(lane, fc_lane_summary.get('A',{}))
                        laneObj.id = lane
                        laneObj.set_lane_info('cluster', 'Reads PF (M)' if 'NovaSeq' in fcObj.type or 'NextSeq' in fcObj.type else 'Clusters PF', lane_sum,
                                                    str(r_num), False if 'NovaSeq' in fcObj.type else True)
                        laneObj.set_lane_info('avg_qval', '% Bases >=Q30', lane_sum, str(r_num))
                        laneObj.set_lane_info('fc_phix', '% Error Rate', lane_sum, str(r_num))
                        if kwargs.get('fc_phix',{}).get(fcObj.name, {}):
                            laneObj.phix = kwargs.get('fc_phix').get(fcObj.name).get(lane)

                        fcObj.lanes[lane] = laneObj

                        ## Check if the above created lane object has all needed info
                        for k,v in vars(laneObj).items():
                            if not v:
                                log.warn('Could not fetch {} for FC {} at lane {}'.format(k, fcObj.name, lane))
                except KeyError:
                    continue
            self.flowcells[fcObj.name] = fcObj

        if not self.flowcells:
            log.warn('There is no flowcell to process for project {}'.format(self.ngi_name))
            self.missing_fc = True


        if sample_qval and kwargs.get('yield_from_fc'):
            log.info('\'yield_from_fc\' option was given so will compute the yield from collected flowcells')
            for sample in list(self.samples.keys()):
                if sample not in list(sample_qval.keys()):
                    del self.samples[sample]

        ## calculate average Q30 over all lanes and flowcell
        for sample in sorted(sample_qval.keys()):
            try:
                qinfo = sample_qval[sample]
                total_qvalsbp, total_bases, total_reads = (0, 0, 0)
                for k in qinfo:
                    total_qvalsbp += qinfo[k]['qval'] * qinfo[k]['bases']
                    total_bases += qinfo[k]['bases']
                    total_reads += qinfo[k]['reads']
                avg_qval = float(total_qvalsbp)/total_bases if total_bases else float(total_qvalsbp)
                self.samples[sample].qscore = '{:.2f}'.format(round(avg_qval, 2))
                ## Get/overwrite yield from the FCs computed instead of statusDB value
                if kwargs.get('yield_from_fc') and total_reads:
                    self.samples[sample].total_reads = total_reads if self.not_as_million else '{:.2f}'.format(total_reads/float(1000000))
                    if sample in self.aborted_samples:
                        log.info('Sample {} was sequenced, so removing it from NOT sequenced samples list'.format(sample))
                        del self.aborted_samples[sample]
            except (TypeError, KeyError):
                log.error('Could not calcluate average Q30 for sample {}'.format(sample))


    def get_library_method(self, project_name, application, library_construction_method):
        """Get the library construction method and return as formatted string
        """
        if application == 'Finished library':
            return 'Library was prepared by user.'
        try:
            lib_meth_pat = r'^(.*?),(.*?),(.*?),(.*?)[\[,](.*)$' #Input, Type, Option, Category -/, doucment number
            lib_head = ['Input', 'Type', 'Option', 'Category']
            lib_meth = re.search(lib_meth_pat, library_construction_method)
            if lib_meth:
                lib_meth_list = lib_meth.groups()[:4] #not interested in the document number
                lib_list = []
                for name,value in zip(lib_head, lib_meth_list):
                    value = value.strip() #remove empty space(s) at the ends
                    if value == 'By user':
                        return 'Library was prepared by user.'
                    if value and value != '-':
                        lib_list.append('* {}: {}'.format(name, value))
                return ('\n'.join(lib_list))
            else:
                log.error('Library method is not mentioned in expected format for project {}'.format(project_name))
                return None
        except KeyError:
            log.error('Could not find library construction method for project {} in statusDB'.format(project_name))
            return None
