"""Module for producing the Element Project Summary Report"""

import os
import ngi_reports.reports.project_summary

from collections import OrderedDict
from string import ascii_uppercase as alphabets


class Report(ngi_reports.reports.project_summary.Report):
    def __init__(self, LOG, working_dir, **kwargs):
        super(Report, self).__init__(LOG, working_dir, **kwargs)

    def generate_report_template(self, proj, template, support_email):
        ## Check and exit if signature not provided
        if not self.signature:
            self.LOG.error(
                "It is required to provide Signature/Name while generating 'project_summary' report, see -s opition in help"
            )
            raise SystemExit
        else:
            self.report_info["signature"] = self.signature

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
        seq_template = "{}) Samples were sequenced on {} ({}) with a {} setup using {}."  # TODO: Update
        ## Get demultiplexing method for the flowcell
        dem_template = "{}) The Bases to FastQ conversion was performed using {} version {}."  # TODO: update
        ## Collect required information for all flowcell run for the project
        sorted_project_fcs = dict(
            sorted(proj.flowcells.items(), key=lambda item: item[1].date)
        )

        for fc in sorted_project_fcs.values():
            ## Sort by the order of reads
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
                seq_software = "{} {}".format(
                    applicationName, fc.seq_software.get("ApplicationVersion")
                )
            else:
                seq_software = "{} {}/RTA {}".format(
                    applicationName,
                    fc.seq_software.get("ApplicationVersion"),
                    fc.seq_software.get("RTAVersion"),
                )
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
            [m.replace("SECTION", seq_methods[m]) for m in seq_methods]
        )
        self.report_info["demultiplexing_methods"] = "\n\n".join(
            [m.replace("SECTION", dem_methods[m]) for m in dem_methods]
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
        for s, v in list(proj.samples.items()):
            v = vars(v)
            if v["initial_qc"]["initial_qc_status"] == "PASSED":
                v["initial_qc"]["initial_qc_status"] = "[pass]"
            elif v["initial_qc"]["initial_qc_status"] == "FAILED":
                v["initial_qc"]["initial_qc_status"] = "[fail]"
            elif v["initial_qc"]["initial_qc_status"] == "NA":
                v["initial_qc"]["initial_qc_status"] = "[na]"
        self.tables_info["tables"]["sample_info"] = self.create_table_text(
            proj.samples.values(), filter_keys=sample_filter, header=sample_header
        )
        self.tables_info["header_explanation"]["sample_info"] = (
            "* _NGI ID:_ Internal NGI sample identifier\n"
            "* _User ID:_ Sample name submitted by user\n"
            '* _RC:_ Reception control status. Value "NA" means this is a finished library and results are presented in Lib. QC below.\n'
            "* _{}:_ Total{} reads (or pairs) for a sample\n"
            "* _>=Q30:_ Aggregated percentage of bases that have a quality score >= Q30".format(
                proj.samples_unit, unit_magnitude[proj.samples_unit]
            )
        )

        ## library_info table
        library_header = ["NGI ID", "Index", "Lib. Prep", "Avg. FS(bp)", "Lib. QC"]
        library_filter = ["ngi_id", "barcode", "label", "avg_size", "qc_status"]
        library_list = []
        for s, v in list(proj.samples.items()):
            for p in list(v.preps.values()):
                p = vars(p)
                p["ngi_id"] = s
                if p["qc_status"] == "PASSED":
                    p["qc_status"] = "[pass]"
                elif p["qc_status"] == "FAILED":
                    p["qc_status"] = "[fail]"
                elif p["qc_status"] == "NA":
                    p["qc_status"] = "[na]"
                library_list.append(p)
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
            sorted(lanes_list, key=lambda d: "{}_{}".format(d["date"], d["id"])),
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
                "{}_project_summary".format(self.report_basename),
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
