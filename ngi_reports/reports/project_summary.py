#!/usr/bin/env python

"""Module for producing the Project Summary Report
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
        self.report_dir = os.path.join(working_dir, "reports")
        self.report_basename = ""
        self.project = kwargs.get("project")

    def generate_report_template(self, proj, template, support_email):
        self.set_signature()

        ## Helper vars
        seq_methods = OrderedDict()
        dem_methods = OrderedDict()

        ## Get information for the report
        self.report_basename = proj.ngi_name
        self.report_info["support_email"] = support_email
        self.report_info["dates"] = self.get_order_dates(proj.dates)
        self.report_info["report_date"] = self.creation_date
        self.report_info["accredit"] = self.get_accredit_info(
            proj.accredited, proj.library_construction, proj.ngi_name
        )

        ## Get sequecing method for the flowcell
        seq_template = "{}) Samples were sequenced on {} ({}) with a {} setup using {}."
        ## Get demultiplexing method for the flowcell
        dem_template = (
            "{}) The Bcl to FastQ conversion was performed using {} from the CASAVA software "
            "suite. The quality scale used is Sanger / phred33 / Illumina 1.8+."
        )
        ## Collect required information for all flowcell run for the project

        sorted_project_fcs = dict(
            sorted(proj.flowcells.items(), key=lambda item: item[1].date)
        )

        for fc in sorted_project_fcs.values():
            ## Sort by the order of readss
            run_setup = sorted(fc.run_setup, key=lambda k: k["Number"])
            run_setup_text = ""
            read_count = 0
            index_count = 0
            for read in run_setup:
                run_setup_text += read["NumCycles"]
                run_setup_text += "nt"
                if read["IsIndexedRead"] == "N":
                    read_count += 1
                    run_setup_text += "(Read"
                    run_setup_text += str(read_count)
                elif read["IsIndexedRead"] == "Y":
                    index_count += 1
                    run_setup_text += "(Index"
                    run_setup_text += str(index_count)
                if run_setup.index(read) == len(run_setup) - 1:
                    run_setup_text += ")"
                else:
                    run_setup_text += ")-"

            if fc.type == "NovaSeq6000":
                fc_chem = "'{}' workflow in '{}' mode flowcell".format(
                    fc.chemistry.get("WorkflowType"), fc.chemistry.get("FlowCellMode")
                )
            elif fc.type == "NovaSeqXPlus":
                fc_chem = "'{}' mode flowcell".format(
                    fc.chemistry.get("RecipeName").replace(" Sequencing", "")
                )
            elif fc.type == "NextSeq500":
                fc_chem = "'{}-Output' chemistry".format(fc.chemistry.get("Chemistry"))
            elif fc.type == "NextSeq2000":
                fc_chem = "'{}' flowcell".format(fc.chemistry.get("Chemistry"))
            else:
                fc_chem = "'{}' chemistry".format(fc.chemistry.get("Chemistry"))

            applicationName = (
                "MSC" if fc.type == "MiSeq" else fc.seq_software.get("ApplicationName")
            )
            if fc.type == "NovaSeqXPlus":
                seq_software = (
                    f"{applicationName} {fc.seq_software.get('ApplicationVersion')}"
                )
            else:
                seq_software = f"{applicationName} {fc.seq_software.get('ApplicationVersion')}/RTA {fc.seq_software.get('RTAVersion')}"
            tmp_seq_method = seq_template.format(
                "SECTION", fc.type, seq_software, run_setup_text, fc_chem
            )
            tmp_dem_method = dem_template.format("SECTION", fc.casava)

            ## to make sure the sequencing methods are unique
            if tmp_seq_method not in list(seq_methods.keys()):
                seq_methods[tmp_seq_method] = alphabets[len(list(seq_methods.keys()))]
            fc.seq_meth = seq_methods[tmp_seq_method]

            ## to make sure the demux methods are unique
            if tmp_dem_method not in list(dem_methods.keys()):
                dem_methods[tmp_dem_method] = alphabets[len(list(dem_methods.keys()))]
            fc.dem_meth = dem_methods[tmp_dem_method]

        ## give proper section name for the methods
        self.report_info["sequencing_methods"] = "\n\n".join(
            [method.replace("SECTION", seq_methods[method]) for method in seq_methods]
        )
        self.report_info["demultiplexing_methods"] = "\n\n".join(
            [method.replace("SECTION", dem_methods[method]) for method in dem_methods]
        )
        ## Check if sequencing and demultiplexing info is complete
        if not self.report_info["sequencing_methods"]:
            self.LOG.warn(
                "Sequencing methods may have some missing information, kindly check your inputs."
            )
        if not self.report_info["demultiplexing_methods"]:
            self.LOG.warn(
                "Demultiplexing methods may have some missing information, kindly check your inputs."
            )

        ###############################################################################
        ##### Create table text and header explanation from collected information #####
        ###############################################################################

        ## sample_info table
        unit_magnitude = {"#reads": "", "Kreads": " Thousand", "Mreads": " Million"}
        sample_header = ["NGI ID", "User ID", "RC", proj.samples_unit, ">=Q30"]
        sample_filter = [
            "ngi_id",
            "customer_name",
            "initial_qc.initial_qc_status",
            "total_reads",
            "qscore",
        ]
        for s, sample in list(proj.samples.items()):
            sample = vars(sample)
            if sample["initial_qc"]["initial_qc_status"] == "PASSED":
                sample["initial_qc"]["initial_qc_status"] = "[pass]"
            elif sample["initial_qc"]["initial_qc_status"] == "FAILED":
                sample["initial_qc"]["initial_qc_status"] = "[fail]"
            elif sample["initial_qc"]["initial_qc_status"] == "NA":
                sample["initial_qc"]["initial_qc_status"] = "[na]"
        self.tables_info["tables"]["sample_info"] = self.create_table_text(
            proj.samples.values(), filter_keys=sample_filter, header=sample_header
        )
        self.tables_info["header_explanation"]["sample_info"] = (
            "* _NGI ID:_ Internal NGI sample identifier\n"
            "* _User ID:_ Sample name submitted by user\n"
            '* _RC:_ Reception control status. Value "NA" means this is a finished library and results are presented in Lib. QC below.\n'
            f"* _{proj.samples_unit}:_ Total{unit_magnitude[proj.samples_unit]} reads (or pairs) for a sample\n"
            "* _>=Q30:_ Aggregated percentage of bases that have a quality score >= Q30"
        )

        ## library_info table
        library_header = ["NGI ID", "Index", "Lib. Prep", "Avg. FS(bp)", "Lib. QC"]
        library_filter = ["ngi_id", "barcode", "label", "avg_size", "qc_status"]
        library_list = []
        for sample_id, sample in list(proj.samples.items()):
            for prep in list(sample.preps.values()):
                prep = vars(prep)
                prep["ngi_id"] = sample_id
                if prep["qc_status"] == "PASSED":
                    prep["qc_status"] = "[pass]"
                elif prep["qc_status"] == "FAILED":
                    prep["qc_status"] = "[fail]"
                elif prep["qc_status"] == "NA":
                    prep["qc_status"] = "[na]"
                library_list.append(prep)
        self.tables_info["tables"]["library_info"] = self.create_table_text(
            sorted(library_list, key=lambda d: d["ngi_id"]),
            filter_keys=library_filter,
            header=library_header,
        )
        self.tables_info["header_explanation"]["library_info"] = (
            "* _NGI ID:_ Internal NGI sample identifier\n"
            "* _Index:_ Barcode sequence used for the sample\n"
            '* _Lib. Prep:_ NGI library identifier. The first library prep will be marked "A", the second "B" and so on.\n'
            '* _Avg. FS:_ Average fragment size of the library. Value "NA" means this was not measured.\n'
            "* _Lib. QC:_ Library quality control status\n"
        )

        ## lanes_info table
        lanes_header = [
            "Date",
            "FC id",
            "Lane",
            "Cluster(M)",
            ">=Q30(%)",
            "Phix",
            "Method",
        ]
        lanes_filter = [
            "date",
            "name",
            "id",
            "total_reads_proj",
            "weighted_avg_qval_proj",
            "phix",
            "seq_meth",
        ]
        lanes_list = []
        for f, v in list(proj.flowcells.items()):
            for l in list(v.lanes.values()):
                l = vars(l)
                l["date"] = v.date
                l["name"] = v.name
                l["seq_meth"] = v.seq_meth
                lanes_list.append(l)

        self.tables_info["tables"]["lanes_info"] = self.create_table_text(
            sorted(lanes_list, key=lambda d: f"{d['date']}_{d['id']}"),
            filter_keys=lanes_filter,
            header=lanes_header,
        )
        self.tables_info["header_explanation"]["lanes_info"] = (
            "* _Date:_ Date of sequencing\n"
            "* _Flowcell:_ Flowcell identifier\n"
            "* _Lane:_ Flowcell lane number\n"
            "* _Clusters:_ Number of clusters that passed the read filters (millions)\n"
            "* _>=Q30:_ Aggregated percentage of bases that have a quality score ≥ Q30\n"
            "* _PhiX:_ Average PhiX error rate for the lane\n"
            "* _Method:_ Sequencing method used. See description under Sequencing heading above.\n"
        )

        # Make the file basename
        output_bn = os.path.realpath(
            os.path.join(
                self.working_dir,
                self.report_dir,
                f"{self.report_basename}_project_summary",
            )
        )

        # Parse the template
        try:
            md = template.render(
                project=proj,
                tables=self.tables_info["header_explanation"],
                report_info=self.report_info,
            )
            return {output_bn: md}
        except:
            self.LOG.error("Could not parse the project_summary template")
            raise

    #####################################################
    ##### Helper methods to get certain information #####
    #####################################################

    def create_table_text(self, ip, filter_keys=None, header=None, sep="\t"):
        """Create a single text string that will be saved in a file in TABLE format
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
                    row.append(i.get(k, "NA"))
                else:
                    if "." in k:
                        k_list = k.split(".")
                        row.append(getattr(i, k_list[0]).get(k_list[1], "NA"))
                    else:
                        row.append(getattr(i, k, "NA"))
            row = list(map(str, row))
            op_string.append(sep.join(row))
        return "\n".join(op_string)

    def get_order_dates(self, project_dates):
        """Get order dates as a markdown string. Ignore if unavailable"""
        dates = []
        for item in project_dates:
            if project_dates.get(item):
                dates.append(
                    f"_{item.replace('_', ' ').capitalize()}:_ {project_dates[item]}"
                )
        return ", ".join(dates)

    def get_accredit_info(self, accredit_dict, library_construction, proj_name):
        """Get swedac accreditation info for given step 'k'

        :param Project proj: Project object containing details of the relevant project
        """
        accredit_info = {}
        for key in accredit_dict:
            accredit = accredit_dict[key]
            ## For "finished library" projects, set certain accredation steps as "NA" even if not set by default
            if (
                key in ["library_preparation", "data_analysis"]
                and library_construction == "Library was prepared by user."
            ):
                accredit_info[key] = "Not Applicable"
            elif accredit in ["Yes", "No"]:
                accredit_info[key] = "{} under ISO/IEC 17025".format(
                    ["[cross] Not accredited", "[tick] Accredited"][accredit == "Yes"]
                )
            elif accredit == "N/A":
                accredit_info[key] = "Not Applicable"
            else:
                self.LOG.error(
                    f"Accreditation step {key} for project {proj_name} is found, but no value is set"
                )
        return accredit_info

    # Generate CSV files for the tables
    def create_txt_files(self, op_dir=None):
        """Generate the CSV files for mentioned tables i.e. a dictionary with table name as key,
        which will be used as file name and the content of file in single string as value to
        put in the TXT file

        :param str op_dir: Path where the TXT files should be created, current dir is default
        """
        for tb_nm, tb_cont in list(self.tables_info["tables"].items()):
            if "[pass]" or "[fail]" or "[na]" in tb_cont:
                tb_cont = tb_cont.replace("[pass]", "Pass")
                tb_cont = tb_cont.replace("[fail]", "Fail")
                tb_cont = tb_cont.replace("[na]", "NA")
            op_fl = f"{self.report_basename}_{tb_nm}.txt"
            if op_dir:
                op_fl = os.path.join(op_dir, op_fl)
            with open(op_fl, "w") as TXT:
                TXT.write(tb_cont)
