#!/usr/bin/env python

""" Module for producing the Project Summary Report
Note: Much of this code was written by Pontus and lifted from
the SciLifeLab repo
"""

from collections import defaultdict, OrderedDict
import os
from string import ascii_uppercase as alphabets

import ngi_reports.reports


class Report(ngi_reports.reports.BaseReport):

    ## initialize class and assign basic variables
    def __init__(self, LOG, working_dir, **kwargs):
        # Initialise the parent class
        super(Report, self).__init__(LOG, working_dir, **kwargs)
        # general initialization
        self.tables_info = defaultdict(dict)
        self.report_info = {}
        # report name and directory to be created
        self.report_dir = os.path.join(working_dir, 'reports')
        self.report_basename = ''
        self.signature = kwargs.get('signature')


    def generate_report_template(self, proj, template, support_email):

        ## Check and exit if signature not provided
        if not self.signature:
            self.LOG.error('It is required to provide Signature/Name while generating \'project_summary\' report, see -s opition in help')
            raise SystemExit
        else:
            self.report_info['signature'] = self.signature

        ## Helper vars
        seq_methods = OrderedDict()

        ## Get information for the report
        self.report_basename              = '{}_project_summary'.format(proj.ngi_name)
        self.report_info['support_email'] = support_email
        self.report_info['dates']         = self.get_order_dates(proj)
        self.report_info['report_date']   = self.creation_date
        self.report_info['accredit']      = self.get_accredit_info(proj)

        ## Get sequecing method for the flowcell
        seq_template = '{}) Samples were sequenced on {} ({}) with a {} setup '\
                       'using {}. The Bcl to FastQ conversion was performed using {} from the CASAVA software '\
                       'suite. The quality scale used is Sanger / phred33 / Illumina 1.8+.'
        ## Collect required information for all flowcell run for the project
        for fc in proj.flowcells.values():
            ## Sort by the order of readss
            run_setup = sorted(fc.run_setup, key=lambda k: k['Number'])
            run_setup_text = ''
            read_count = 0
            index_count = 0
            for read in run_setup:
                run_setup_text += read['NumCycles']
                run_setup_text += 'nt'
                if read['IsIndexedRead'] == 'N':
                    read_count += 1
                    run_setup_text += '(Read'
                    run_setup_text += str(read_count)
                elif read['IsIndexedRead'] == 'Y':
                    index_count += 1
                    run_setup_text += '(Index'
                    run_setup_text += str(index_count)
                if run_setup.index(read) == len(run_setup)-1:
                    run_setup_text += ')'
                else:
                    run_setup_text += ')-'

            if fc.type == 'NovaSeq6000':
                fc_chem = '\'{}\' workflow in \'{}\' mode flowcell'.format(fc.chemistry.get('WorkflowType'), fc.chemistry.get('FlowCellMode'))
            elif fc.type == 'NextSeq500':
                fc_chem = '\'{}-Output\' chemistry'.format(fc.chemistry.get('Chemistry'))
            else:
                fc_chem = '\'{}\' chemistry'.format(fc.chemistry.get('Chemistry'))

            applicationName = 'MSC' if fc.type == "MiSeq" else fc.seq_software.get('ApplicationName')
            seq_software = "{} {}/RTA {}".format(applicationName, fc.seq_software.get('ApplicationVersion'), fc.seq_software.get('RTAVersion'))
            tmp_method = seq_template.format('SECTION', fc.type, seq_software, run_setup_text, fc_chem, fc.casava)

            ## to make sure the sequencing methods are unique
            if tmp_method not in list(seq_methods.keys()):
                seq_methods[tmp_method] = alphabets[len(list(seq_methods.keys()))]
            fc.seq_meth = seq_methods[tmp_method]


        ## give proper section name for the methods
        self.report_info['sequencing_methods'] = "\n\n".join([m.replace('SECTION',seq_methods[m]) for m in seq_methods])
        ## Check if sequencing info is complete
        if not self.report_info['sequencing_methods']:
            self.LOG.warn('Sequencing methods may have some missing information, kindly check your inputs.')


        ###############################################################################
        ##### Create table text and header explanation from collected information #####
        ###############################################################################

        ## sample_info table
        sample_header = ['NGI ID', 'User ID', '#reads' if proj.not_as_million else 'Mreads', '>=Q30']
        sample_filter = ['ngi_id', 'customer_name', 'total_reads', 'qscore']

        self.tables_info['tables']['sample_info'] = self.create_table_text(proj.samples.values(), filter_keys=sample_filter, header=sample_header)
        self.tables_info['header_explanation']['sample_info'] = '* _NGI ID:_ Internal NGI sample indentifier\n'\
                                                                '* _User ID:_ User submitted name for a sample\n'\
                                                                '* _Mreads:_ Total million reads (or pairs) for a sample\n'\
                                                                '* _>=Q30:_ Aggregated percentage of bases that have quality score more the Q30'
        if proj.not_as_million:
            self.tables_info['header_explanation']['sample_info'] = self.tables_info['header_explanation']['sample_info'].replace('_Mreads:_ Total million reads (or pairs) for a sample',
                                                                                                                                  '_#reads:_ Total number of reads (or pairs) for a sample')
        ## library_info table
        library_header = ['NGI ID', 'Index', 'Lib Prep', 'Avg. FS', 'Lib QC']
        library_filter = ['ngi_id', 'barcode', 'label', 'avg_size', 'qc_status']
        library_list = []
        for s, v in list(proj.samples.items()):
            for p in list(v.preps.values()):
                p = vars(p)
                p['ngi_id'] = s
                library_list.append(p)
        self.tables_info['tables']['library_info'] = self.create_table_text(sorted(library_list, key=lambda d: d['ngi_id']), filter_keys=library_filter, header=library_header)
        self.tables_info['header_explanation']['library_info'] = '* _NGI ID:_ Internal NGI sample indentifier\n'\
                                                                 '* _Index:_ Barcode sequence used for the sample\n'\
                                                                 '* _Lib Prep:_ NGI library indentifier\n'\
                                                                 '* _Avg. FS:_ Average fragment size of the library\n'\
                                                                 '* _Lib QC:_ Reception control library quality control step status\n'

        ## lanes_info table
        lanes_header = ['Date', 'FC id', 'Lane', 'Cluster(M)', 'Phix', '>=Q30(%)', 'Method']
        lanes_filter = ['date', 'name', 'id', 'cluster', 'phix', 'avg_qval', 'seq_meth']
        lanes_list = []
        for f, v in list(proj.flowcells.items()):
            for l in list(v.lanes.values()):
                l = vars(l)
                l['date'] = v.date
                l['name'] = v.name
                l['seq_meth'] = v.seq_meth
                lanes_list.append(l)

        self.tables_info['tables']['lanes_info'] = self.create_table_text(sorted(lanes_list, key=lambda d: '{}_{}'.format(d['date'],d['id'])), filter_keys=lanes_filter, header=lanes_header)
        self.tables_info['header_explanation']['lanes_info'] = '* _Date:_ Date of sequencing\n'\
                                                               '* _Flowcell:_ Flowcell identifier\n'\
                                                               '* _Lane:_ Flowcell lane number\n'\
                                                               '* _Clusters:_ Number of clusters that passed the read filters (millions)\n'\
                                                               '* _>=Q30:_ Aggregated percentage of bases that have a quality score of more than Q30\n'\
                                                               '* _PhiX:_ Average PhiX error rate for the lane\n'\
                                                               '* _Method:_ Sequencing method used. See above for description\n'

        # Make the file basename
        output_bn = os.path.realpath(os.path.join(self.working_dir, self.report_dir, '{}_project_summary'.format(self.report_basename)))

        # Parse the template
        try:
            md = template.render(project=proj, tables=self.tables_info['header_explanation'], report_info=self.report_info)
            return {output_bn: md}
        except:
            self.LOG.error('Could not parse the project_summary template')
            raise


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
            ip = list(ip.values())
        if header:
            op_string.append(sep.join(header))
        if not filter_keys:
            filter_keys = []
            for i in ip:
                filter_keys.extend(list(i.keys()))
            filter_keys = sorted(list(set(filter_keys)))
        for i in ip:
            row = []
            for k in filter_keys:
                if type(i) is dict:
                    row.append(i.get(k,'NA'))
                else:
                    row.append(getattr(i, k, 'NA'))
            row = list(map(str, row))
            op_string.append(sep.join(row))
        return '\n'.join(op_string)


    def get_order_dates(self, project):
        """ Get order dates as a markdown string. Ignore if unavailable
        """
        dates = []
        for item in project.dates:
            if project.dates.get(item):
                dates.append('_{}:_ {}'.format(item.replace('_', ' ').capitalize(), project.dates[item]))
        return ', '.join(dates)

    def get_accredit_info(self, proj):
        """Get swedac accreditation info for given step 'k'

        :param Project proj: Project object containing details of the relevant project
        """
        accredit_info = {}
        for key in proj.accredited:
            try:
                accredit = proj.accredited[key]
                if accredit in ['Yes','No']:
                    accredit_info[key] = '{} under ISO accreditation 17025'.format(['[cross] Not validated','[tick] Validated'][accredit == 'Yes'])
                elif accredit == 'N/A':
                    accredit_info[key] = 'Not Applicable'
                else:
                    self.LOG.error('Accreditation step {} for project {} is found, but any value is not set'.format(key, proj.ngi_name))
            except KeyError:
                ## For "finished library" projects, set certain accredation steps as "NA" even if not set by default
                if key in ['library_preparation','data_analysis'] and project.library_construction == 'Library was prepared by user.':
                    accredit_info[key] = 'Not Applicable'
                else:
                    self.LOG.error('Could not find accreditation info for step {} for project {}'.format(key, proj.ngi_name))
        return accredit_info

    # Generate CSV files for the tables
    def create_txt_files(self, op_dir=None):
        """ Generate the CSV files for mentioned tables i.e. a dictionary with table name as key,
            which will be used as file name and the content of file in single string as value to
            put in the TXT file

            :param str op_dir: Path where the TXT files should be created, current dir is default
        """
        for tb_nm, tb_cont in list(self.tables_info['tables'].items()):
            op_fl = '{}_{}.txt'.format(self.report_basename, tb_nm)
            if op_dir:
                op_fl = os.path.join(op_dir, op_fl)
            with open(op_fl, 'w') as TXT:
                TXT.write(tb_cont)
