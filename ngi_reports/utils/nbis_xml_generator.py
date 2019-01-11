#!/usr/bin/env python

import argparse
import couchdb
import os
import re

from collections import defaultdict
from ngi_reports.log import loggers
from ngi_reports.utils import statusdb


class xml_generator(object):
    """
        A class with class methods to generate run/experiment XML files
        which user can submit to reads archive with the help of NBIS
    """
    def __init__(self, project, outdir=os.getcwd(), ignore_lib_prep=False, flowcells=None, LOG=None, pcon=None, fcon=None, xcon=None):
        """ Instantiate required objtects"""
        self.LOG = LOG or loggers.minimal_logger('nbis_xml_generator')
        try:
            self.pcon = pcon or statusdb.ProjectSummaryConnection()
            assert self.pcon, "Could not connect to {} database in StatusDB".format("project")
            self.fcon = fcon or statusdb.FlowcellRunMetricsConnection()
            assert self.fcon, "Could not connect to {} database in StatusDB".format("flowcell")
            self.xcon = xcon or statusdb.X_FlowcellRunMetricsConnection()
            assert self.xcon, "Could not connect to {} database in StatusDB".format("x_flowcells")
            self._check_and_load_project(project)
            assert isinstance(self.project, couchdb.client.Document), "Could not get proper project document for {} from StatusDB".format(project)
            self.samples_delivered = self.project.get('staged_files', {})
            assert self.samples_delivered, "No delivered samples for project {}, cannot generate XML files".format(project)
            self._check_and_load_flowcells(flowcells)
            assert isinstance(self.flowcells, dict), "Could not get the flowcell for project {} from StatusDB".format(project)
        except AssertionError as e:
            self.LOG.error(e)
            raise e
        self.outdir = self._check_and_load_outdir(outdir)
        self._set_project_design()
        self._check_and_load_lib_preps()
        self._stats_from_flowcells()


    def generate_xml(self, return_string_dict=False):
        """ Generate experiment/run xml file from the string template """
        experiment_xml_string, run_xml_string = ("", "")
        for sample_stat in self._collect_sample_stats():
            # fill in to experiment values from collected stat
            experiment_xml_string += ('\t<EXPERIMENT alias="{alias}" center_name="">\n'
                                      '\t\t<TITLE>{title}</TITLE>\n'
                                      '\t\t<STUDY_REF refname="{study}"/>\n'
                                      '\t\t<DESIGN>\n'
                                      '\t\t\t<DESIGN_DESCRIPTION> {design} </DESIGN_DESCRIPTION>\n'
                                      '\t\t\t<SAMPLE_DESCRIPTOR refname="{discriptor}"/>\n'
                                      '\t\t\t<LIBRARY_DESCRIPTOR>\n'
                                      '\t\t\t\t<LIBRARY_NAME>{library}_lib</LIBRARY_NAME>\n'
                                      '\t\t\t\t<LIBRARY_STRATEGY>{strategy}</LIBRARY_STRATEGY>\n'
                                      '\t\t\t\t<LIBRARY_SOURCE>{source}</LIBRARY_SOURCE>\n'
                                      '\t\t\t\t<LIBRARY_SELECTION>{selection}</LIBRARY_SELECTION>\n'
                                      '\t\t\t\t<LIBRARY_LAYOUT>{layout}</LIBRARY_LAYOUT>\n'
                                      '\t\t\t\t<LIBRARY_CONSTRUCTION_PROTOCOL>{protocol}</LIBRARY_CONSTRUCTION_PROTOCOL>\n'
                                      '\t\t\t</LIBRARY_DESCRIPTOR>\n'
                                      '\t\t</DESIGN>\n'
                                      '\t\t<PLATFORM>\n'
                                      '\t\t\t<ILLUMINA>\n'
                                      '\t\t\t\t<INSTRUMENT_MODEL>{instrument}</INSTRUMENT_MODEL>\n'
                                      '\t\t\t</ILLUMINA>\n'
                                      '\t\t</PLATFORM>\n'
                                      '\t\t<PROCESSING/>\n'
                                      '\t</EXPERIMENT>\n').format(**sample_stat['experiment'])
            # fill in to run values from collected stat
            run_xml_string += ('\t<RUN alias="{alias}" run_center="National Genomics Infrastructure, Stockholm" center_name="">\n'
                               '\t\t<EXPERIMENT_REF refname="{exp_ref}"/>\n'
                               '\t\t<DATA_BLOCK>\n'
                               '\t\t\t<FILES>\n'
                               '{files}'
                               '\t\t\t</FILES>\n'
                               '\t\t</DATA_BLOCK>\n'
                               '\t</RUN>\n').format(**sample_stat['run'])
        # wrap in final xml string tags
        experiment_set = ('<EXPERIMENT_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                          'xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.experiment.xsd">'
                          '\n{}\n</EXPERIMENT_SET>\n').format(experiment_xml_string)
        run_set = ('<RUN_SET  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.run.xsd">'
                   '\n{}\n</RUN_SET>\n').format(run_xml_string)
        # dont save in file if asked to return as string
        if return_string_dict:
            return {'experiments': experiment_set, 'runs': run_set}
        # save in files in given outdir
        with open(os.path.join(self.outdir, "{}_experiments.xml".format(self.project['project_id'])), 'w') as exml, \
             open(os.path.join(self.outdir, "{}_runs.xml".format(self.project['project_id'])), 'w') as rxml:
            exml.write(experiment_set)
            rxml.write(run_set)


    def _collect_sample_stats(self):
        """ Collect stats that will be used to generate the xml files """
        for sample in sorted(self.samples_delivered.keys()):
            # all the samples should exist, if not fail right away
            sample_seq_instrument = self.sample_aggregated_stat[sample]
            for inst in sorted(sample_seq_instrument.keys()):
                inst_stat = sample_seq_instrument[inst]
                experiment = { 'alias' : "{}_{}_experiment".format(sample, inst),
                               'title' : "Prep for {} sequenced in {}".format(sample, inst_stat['xml_text']),
                               'study' : self.project["project_id"],
                               'design' : self.project_design["design"].format(instrument=inst_stat['xml_text']),
                               'discriptor' : sample,
                               'library' : "{}_prep".format(sample),
                               'strategy' : self.project_design["strategy"],
                               'source' : self.project_design["source"],
                               'selection' : self.project_design["selection"],
                               'layout' : self.project_design["layout"],
                               'protocol' : self.project_design["protocol"],
                               'instrument' : inst_stat['xml_text'] }
                run  = { 'alias' : "{}_{}_runs".format(sample, inst),
                         'exp_ref' : experiment['alias'],
                         'data_name' : sample,
                         'files' : self._generate_files_block(self.samples_delivered[sample], flowcells=inst_stat['runs']) }
                yield { 'experiment': experiment, 'run': run }


    def _stats_from_flowcells(self):
        """ Go through the flowcells and collect needed informations """
        self.sample_aggregated_stat = defaultdict(dict)
        # try to get instrument type and samples sequenced
        for fc, fc_info in self.flowcells.iteritems():
            fc_obj = self.xcon.get_entry(fc_info['run_name']) if fc_info['db'] == 'x_flowcells' else self.fcon.get_entry(fc_info['run_name'])
            if not fc_obj:
                self.LOG.warn("Could not fetch flowcell {} from {} db, will remove it from list".format(fc_info['run_name'], fc_info['db']))
                continue
            # get instrument type from runid, it should fail if 'Id' not exist in document
            full_run_id = fc_obj.get('RunInfo', {})['Id']
            if "_ST-" in full_run_id:
                fc_info["instrument"] = "HiSeq X Ten"
            elif "_M0" in full_run_id:
                fc_info["instrument"] = "Illumina MiSeq"
            elif "_A0" in full_run_id:
                fc_info["instrument"] = "Illumina NovaSeq"
            elif "_D0" in full_run_id:
                fc_info["instrument"] = "Illumina HiSeq 2500"
            instrument_key = fc_info["instrument"].lower().replace(' ', '_')
            # get samples sequenced from demux stat
            fc_info["samples"] = []
            for lane_stat in fc_obj.get("illumina", {}).get('Demultiplex_Stats', {}).get('Barcode_lane_statistics', []):
                lane_sample = lane_stat.get("Sample", "")
                if lane_sample.startswith(self.project['project_id']) and lane_sample in self.samples_delivered and lane_sample not in fc_info["samples"]:
                    prep_id = "A"
                    #try and get the prep id for given sample and FC combo
                    if not self.ignore_lib_prep:
                        try:
                            sample_preps_fcs = self.sample_prep_fc_map.get(lane_sample)
                            prep_id_list = [pid for pid, seqruns in sample_preps_fcs.iteritems() if full_run_id in seqruns]
                            assert len(prep_id_list) == 1
                            prep_id = prep_id_list[0]
                        except AssertionError:
                            self.LOG.warning("Not able to find prep id for sample '{}' - FC '{}'. Found prep seq map is '{}'".format(lane_sample, full_run_id, sample_preps_fcs))
                            self.LOG.warning("Generated XML file may not be reliable, double check the file manually and run with '--ignore-lib-prep' option if neccesary")
                    prep_inst_key = "{}_{}".format(prep_id, instrument_key)
                    if prep_inst_key not in self.sample_aggregated_stat[lane_sample]:
                        self.sample_aggregated_stat[lane_sample][prep_inst_key] = {'xml_text': fc_info["instrument"], 'runs': []}
                    self.sample_aggregated_stat[lane_sample][prep_inst_key]['runs'].append(full_run_id)
                    fc_info["samples"].append(lane_sample)
            # this should never happen but good to catch
            if len(fc_info["samples"]) == 0:
                self.LOG.warn("No sample were found for project {} in fc {}, this is so weird".format(self.project['project_id'], fc_info['run_name']))


    def _set_project_design(self):
        """ Get project library design and protocol details """
        # This function is not particularly clever, but this is the best
        # I was able to do with avilable stuff at the time of writing
        self.project_design = {}
        # get application type of project
        proj_app = self.project.get("details", {}).get("application")
        # get library construction method and parse neccesary information
        p_input, p_type, p_option, p_category = [''] * 4
        lib_meth_match = re.search(r'^(.*?),(.*?),(.*?),(.*?)[\[,](.*)$', self.project.get("details", {}).get("library_construction_method", ""))
        if lib_meth_match:
            p_input, p_type, p_option, p_category = lib_meth_match.groups()[:4]
        # if no library kit found use application type or default string
        if not p_type or "user" in p_type or "house" in p_type:
            dp_design = proj_app or p_input if p_input.lower() != "library" else "Sample"
            dp_protocol = "NA"
        else:
            dp_design = p_type
            dp_protocol = "{}{}".format(p_type, ", {}".format(p_option) if p_option else "")
        design_template = "{} library for sequencing on ".format(dp_design)
        self.project_design['design'] = design_template + "{instrument}"
        self.project_design['protocol'] = dp_protocol
        # try setting strategy based on application type
        if not proj_app or proj_app.lower() == "metagenomics":
            dp_strategy = "OTHER"
        elif proj_app.lower() == "rna-seq":
            dp_strategy = "miRNA-Seq" if self.project.get("details", {}).get("bioinformatic_qc", "").lower() == "mirna-seq" else "RNA-Seq"
        elif proj_app.lower() in ["rna-seq", "chip-seq", "rad-seq"]:
            dp_strategy = proj_app.replace("-s", "-S")
        elif proj_app == "WG re-seq":
            dp_strategy = "WGS"
        self.project_design['strategy'] = dp_strategy
        # try getting source from input type
        if proj_app.lower() == "metagenomics":
            dp_source = "METAGENOMIC"
        elif "rna" in proj_app.lower():
            dp_source = "TRANSCRIPTOMIC"
        elif p_input =="DNA":
            dp_source = "GENOMIC"
        else:
            dp_source = "OTHER"
        self.project_design['source'] = dp_source
        # get layout from setup
        seq_setup = self.project.get("details",{}).get("sequencing_setup", "")
        if seq_setup.startswith("1x"):
            dp_layout = "<SINGLE/>"
        elif seq_setup.startswith("2x"):
            dp_layout = "<PAIRED></PAIRED>"
        else:
            self.LOG.warn("Was not able to fetch sequencing setup from couchdb for project {}, so choosing PAIRED".format())
            dp_layout = "<PAIRED></PAIRED>"
        self.project_design['layout'] = dp_layout
        # set library selection depending upon setup
        if dp_protocol == "NA":
            dp_selection = "unspecified"
        elif dp_strategy.lower() == "chip-seq":
            dp_selection = "ChIP"
        elif dp_strategy.lower() == "rad-seq":
            dp_selection = "Restriction Digest"
        elif dp_strategy.lower() == "rna-seq":
            if p_option and "poly-a" in p_option.lower():
                dp_selection = "cDNA"
            elif p_option and "ribozero" in p_option.lower():
                dp_selection = "Inverse rRNA selection"
            else:
                dp_selection = "unspecified"
        else:
            dp_selection = "RANDOM"
        self.project_design["selection"] = dp_selection

    def _generate_files_block(self, files, flowcells=None):
        """ Take a 'files' dict and give xml block string to include in final xml """
        file_block = ""
        for fl, fl_stat in files.iteritems():
            # collect only fastq files
            if not fl.endswith('fastq.gz'):
                continue
            # if flowcells given filter files only from that flowcell
            if flowcells and fl.split("/")[2] not in flowcells:
                continue
            file_block += ('\t\t\t\t<FILE filename="{}" filetype="fastq" checksum_method="MD5" checksum="{}" />\n'.format(fl, fl_stat.get('md5_sum','')))
        return file_block


    def _check_and_load_project(self, project):
        """ Get the project document from couchDB if it is not """
        if isinstance(project, str):
            self.LOG.info("Fetching project '{}' from statusDB".format(project))
            project = self.pcon.get_entry(project, use_id_view=True)
        self.project = project


    def _check_and_load_flowcells(self, flowcells):
        """ Get the project's flowcells if not already given """
        if not flowcells or not isinstance(flowcells, dict):
            self.LOG.info("Fetching flowcells sequenced for project '{}' from StatusDB".format(self.project['project_id']))
            flowcells = {}
            flowcells.update(self.fcon.get_project_flowcell(self.project['project_id'], self.project.get('open_date','2015-01-01')))
            flowcells.update(self.xcon.get_project_flowcell(self.project['project_id'], self.project.get('open_date','2015-01-01')))
        self.flowcells = flowcells


    def _check_and_load_lib_preps(self, ignore_lib_prep=False):
        """ If not asked to ignore create a dict with lib prep and sequenced FC for lookup downstream """
        self.ignore_lib_prep = ignore_lib_prep
        self.sample_prep_fc_map = defaultdict(dict)
        if not self.ignore_lib_prep:
            for sample in self.samples_delivered.keys():
                sample_preps = self.project.get("samples", {}).get(sample, {}).get("library_prep", {})
                for prep, prep_info in sample_preps.iteritems():
                    self.sample_prep_fc_map[sample][prep] = prep_info.get("sequenced_fc", [])


    def _check_and_load_outdir(self, outdir):
        """ Check the given outdir and see if its valid one """
        if not os.path.exists(outdir):
            self.LOG.info("Given outdir '{}' does not exist so will create it".format(outdir))
            os.makedirs(outdir)
        elif not os.path.isdir(outdir):
            self.LOG.warn("Given outdir '{}' is not valid so will use current directory".format(outdir))
            outdir = os.getcwd()
        return outdir


if __name__ == "__main__":
    parser = argparse.ArgumentParser("nbis_xml_generator.py")
    parser.add_argument("project", type=str, metavar='<project id>', help="NGI project id for which XML files are generated")
    parser.add_argument("--outdir", type=str, default=os.getcwd(), help="Output directory where the XML files will be saved")
    parser.add_argument("--ignore-lib-prep", default=False, action="store_true", help="Dont take in account the lib preps")
    kwargs = vars(parser.parse_args())
    LOG = loggers.minimal_logger('nbis_xml_generator')
    LOG.info("Generating xml files for project {}".format(kwargs['project']))
    xgen = xml_generator(kwargs['project'], LOG=LOG, outdir=kwargs['outdir'], ignore_lib_prep=kwargs['ignore_lib_prep'])
    xgen.generate_xml()
    LOG.info("Generated xml files for project {}".format(kwargs['project']))
