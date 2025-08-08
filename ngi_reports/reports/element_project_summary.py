"""Module for producing the Element Project Summary Report"""

import os
import ngi_reports.reports.project_summary

from collections import OrderedDict
from string import ascii_uppercase as alphabets


class Report(ngi_reports.reports.project_summary.Report):
    def __init__(self, LOG, working_dir, **kwargs):
        super(Report, self).__init__(LOG, working_dir, **kwargs)

    def generate_report_template(self, proj, template, support_email):
        self.set_signature()

        # Helper vars
        seq_methods = OrderedDict()
        dem_methods = OrderedDict()

        # Get information for the report
        self.report_basename = proj.ngi_name
        self.report_info["support_email"] = support_email
        self.report_info["dates"] = self.get_order_dates(proj.dates)
        self.report_info["report_date"] = self.creation_date
        self.report_info["accredit"] = self.get_accredit_info(
            proj.accredited, proj.library_construction, proj.ngi_name
        )

        # Collect required information for all flowcell run for the project
        sorted_project_fcs = dict(
            sorted(proj.flowcells.items(), key=lambda item: item[1].date)
        )

        for fc in sorted_project_fcs.values():
            run_setup_text = f"{fc.run_setup['R1']}nt(Read1)-{fc.run_setup['I1']}nt(Index1)-{fc.run_setup['I2']}nt(Index2)-{fc.run_setup['R2']}nt(Read2)"
            throughput_versions = {
                "High": "High",
                "Med": "Medium",
                "Low": "Low",
            }
            throughput_text = f"{fc.fc_type['Type']} {throughput_versions[fc.fc_type['Throughput']]} Output"  # Cloudbreak FS Medium Output
            tmp_seq_method = f"SECTION) Samples were sequenced on {fc.type} with {throughput_text} throughput and a {run_setup_text} setup."
            tmp_dem_method = f"SECTION) The Bases to FastQ conversion was performed using bases2fastq version {fc.seq_software['bases2fastq_version']}."

            # Make sure the sequencing methods are unique
            if tmp_seq_method not in list(seq_methods.keys()):
                seq_methods[tmp_seq_method] = alphabets[len(list(seq_methods.keys()))]
            fc.seq_meth = seq_methods[tmp_seq_method]

            # Make sure the demux methods are unique
            if tmp_dem_method not in list(dem_methods.keys()):
                dem_methods[tmp_dem_method] = alphabets[len(list(dem_methods.keys()))]
            fc.dem_meth = dem_methods[tmp_dem_method]

        # Give proper section name for the methods
        self.report_info["sequencing_methods"] = "\n\n".join(
            [method.replace("SECTION", seq_methods[method]) for method in seq_methods]
        )
        self.report_info["demultiplexing_methods"] = "\n\n".join(
            [method.replace("SECTION", dem_methods[method]) for method in dem_methods]
        )
        # Check if sequencing and demultiplexing info is complete
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

        # sample_info table
        unit_magnitude = {"#reads": "", "Kreads": " Thousand", "Mreads": " Million"}
        sample_header = ["NGI ID", "User ID", "RC", proj.samples_unit, ">=Q30"]
        sample_filter = [
            "ngi_id",
            "customer_name",
            "initial_qc.initial_qc_status",
            "total_reads",
            "qscore",
        ]
        for sample_id, sample in list(proj.samples.items()):
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

        # library_info table
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

        # lanes_info table
        lanes_header = [
            "Date",
            "FC id",
            "Lane",
            "Polonies(M)",
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
        for flowcell_id, flowcell in list(proj.flowcells.items()):
            for lane in list(flowcell.lanes.values()):
                lane = vars(lane)
                lane["date"] = flowcell.date
                lane["name"] = flowcell.name
                lane["seq_meth"] = flowcell.seq_meth
                lanes_list.append(lane)

        self.tables_info["tables"]["lanes_info"] = self.create_table_text(
            sorted(lanes_list, key=lambda d: f"{d['date']}_{d['id']}"),
            filter_keys=lanes_filter,
            header=lanes_header,
        )
        self.tables_info["header_explanation"]["lanes_info"] = (
            "* _Date:_ Date of sequencing\n"
            "* _Flowcell:_ Flowcell identifier\n"
            "* _Lane:_ Flowcell lane number\n"
            "* _Polonies:_ Number of polonies that passed the read filters (millions)\n"
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
