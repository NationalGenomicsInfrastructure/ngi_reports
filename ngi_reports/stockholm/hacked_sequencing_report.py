"""

  :sequencing_report.py
  
  Module for creating reports based on data, extracted from StatusDB, and render them in rst format based on mako templates.
  The module contains ReportObject classes that act as connectors on top of StatusDB documents and are used for retrieving 
  field values as well as performing aggregating operations and gathering statistics. 
  
  The general idea is that the objects are instantiated and then passed as parameters to the method that renders the reports. 
  The mako templates contain the layout and content of the reports and receive the connector objects when rendering. The retrieval 
  of fields and statistics are done from the mako templates, although these should contain a minimum of logic. The logic is in
  the connector objects.
  
"""

import numpy as np
from collections import OrderedDict
from string import ascii_uppercase as alphabets

from scilifelab.db.statusdb import ProjectSummaryConnection, SampleRunMetricsConnection, FlowcellRunMetricsConnection, ProjectSummaryDocument

def report(ctrl, project_name, **kw):
    """Main method for generating a report summarizing the progress of a project. Renders rst reports, concatenates them
    and write them to a file.
    
    :param ctrl: a Controller object 
    :param project_name: name of the project to generate report for (e.g. J.Doe_11_01)
    :param **kw: additional arguments
    
    """
    
    notes = project_summary_report(ctrl,project_name,**kw)
    write_rest_note("report_test.rst","/Users/senthilkumarpanneerselvam/Desktop/task/delReports/trail_report/",contents=notes)

def project_summary_report(ctrl, project_name, sample_name=None, flowcell_id=None, **kw):
    """Generate and render a summary report for a project, consisting of a general summary, a
    flowcell-centric summary and one sample-centric summary for each sample.
    
    Instantiates a ProjectReportObject and passes them to the rendering methods.
    
    :param ctrl: the DeliveryReportController that invoked the method
    :param project_name: the project name (e.g. J.Doe_11_01)
    
    :returns: a list of rendered summary reports in rst format 
    """
    
    # Get connections to the databases in StatusDB
    pcon = ProjectSummaryConnection(**kw)
    assert pcon, "Could not connect to {} database in StatusDB".format("project")
    fcon = FlowcellRunMetricsConnection(**kw)
    assert fcon, "Could not connect to {} database in StatusDB".format("flowcell")
    scon = SampleRunMetricsConnection(**kw)
    assert scon, "Could not connect to {} database in StatusDB".format("samples")
    
    # Fetch the database document for the project 
    project = pcon.get_entry(project_name)
    if not project:
        ctrl.log.warn("No such project '{}'".format(project_name))
        return None
    # If the data source is not lims, we cannot generate a report using this method
    if project.get('source') != 'lims':
        ctrl.log.warn("The source for data for project {} is not LIMS. This type of report can only be generated for data from LIMS. Please refer to older versions of pm".format(project_name))
        return None
    
    # Instantiate a ProjectReportObject. This will be passed to the mako render method and used within the template
    psr = ProjectReportObject(ctrl, project, fcon, scon)
    
    # Render the project overview
    project_report = render_rest_note(tables={}, 
                                      report="project_report", 
                                      **{"project": psr,
                                         "skip_samples": sample_name,
                                         "skip_flowcells": flowcell_id,
                                         "issuer": kw.get("issuer",None)})

    return [project_report]
   
class ReportObject():
    """The base class for ReportObjects. Specialized ReportObjects inherit this.
    """

    def __init__(self, ctrl, dbobj, dbcon=None):
        self.ctrl = ctrl
        self.log = self.ctrl.log
        self.dbobj = dbobj
        self.dbcon = dbcon
        self.date_format = "%Y-%m-%d"
        
    def __getattr__(self, name):
        return self.dbobj.get(name)
        
    def __repr__(self):
        return "<ReportObject>"
    
    def _parse_date(self, val, fmt=None):
        if fmt is None:
            fmt = self.date_format
        org = val
        try:
            val = datetime.datetime.strptime(val,fmt)
        except TypeError, ValueError:
            val = org
        return val

    def _date_field(self, field, fmt=None):
        if fmt is None:
            fmt = self.date_format
        try:
            return self._parse_date(getattr(self,field)).strftime(fmt)
        except AttributeError:
            return "N/A"

class ProjectReportObject(ReportObject):
    """The ProjectReportObject mostly represents a project document in StatusDB. It contains access methods to fields and 
    convenience methods for e.g. creating rst tables. The object also serves as an entry point to ReportObjects 
    representing e.g. flowcells and samples belonging to the project.
    """
    
    def __init__(self, ctrl, dbobj, fcon=None, scon=None):
        """
        
        :param ctrl: reference to a Controller object that holds e.g. reference to log and config
        :param dbobj: the database document representing the project
        :param fcon: a database connection to the flowcell database, used to fetch objects for flowcells relevant to the project
        :param scon: a database connection to the samples database, used to fetch objects for sample runs performed in the project
        
        """ 
        ReportObject.__init__(self,ctrl,dbobj,fcon)
        self.details = self.dbobj.get("details",{})
        self.project_samples = sorted([ProjectSampleReportObject(ctrl,sample,self.project_name,scon) for sample in self.dbobj.get("samples",{}).values()], key=lambda name: name.scilife_name)
        self.project_flowcells()
        self.accredited_libMethods = {}
        self.accredited_seqMethods = {}
        self.accredit_info = OrderedDict()
        
    def __repr__(self):
        return "<ProjectReportObject {}>".format(self.project_name)

    def __getattr__(self, name):
        return self.dbobj.get(name,self.details.get(name))

    def order_received_date(self):
        return self._date_field("order_received")
    def contract_received_date(self):
        return self._date_field("contract_sent")
    def samples_received_date(self):
        return self._date_field("samples_received")
    def queued_date(self):
        return self._date_field("queued")
    def get_min_reads(self):
        try:
            return self.samples.values()[0]["details"]["reads_min"]
        except KeyError:
            return "No minimal ordered amount"
    def project_flowcells(self):
        """Fetch flowcell documents for project-related flowcells
        """
        # skip if we have already fetched the documents
        if self.flowcells and len(self.flowcells) > 0:
            return
        self.flowcells = []
        lane_fc = sorted(list(set([fc for sample in self.project_samples for fc in sample.sample_run_flowcells()])))
        self.flowcell_lanes = {}
        for lane, fc in [(lfc.split("_")[0],"_".join(lfc.split("_")[1:3])) for lfc in lane_fc]:
            if fc not in self.flowcell_lanes:
                self.flowcell_lanes[fc] = []
            self.flowcell_lanes[fc].append(lane)
             
        for fcid in self.flowcell_lanes.keys():
            fcdoc = self.dbcon.get_entry(fcid)
            if not fcdoc:
                self.log.warn("Could not find flowcell document for {}".format(fcid))
                continue
            self.flowcells.append(FlowcellReportObject(self.ctrl,fcdoc))
            
    def project_flowcell_summary_table_data(self):
        if not self.flowcells:
            self.project_flowcells()        
        return [[fc.Date,
                 fc.Barcode,
                 fc.ScannerID,
                 fc.run_setup,
                 fc.FCPosition,
                 lane,
                 fc.lane_clusters(lane)/1e6,
                 str(fc.q30(lane)),
                 str(fc.phix(lane))] for fc in self.flowcells for lane in self.flowcell_lanes[fc.name]]
    
    def project_flowcell_summary_table(self):
        return _make_rst_table([["Date","Flowcell","Instrument","Run setup","Position","Lane","Clusters (M)","Q30 (%)","PhiX (%)"]] + self.project_flowcell_summary_table_data())
    
    # to create the table with all meta info of the project    
    def get_order_info(self):
        order_info_fields = OrderedDict([("Project name", self.project_name),
                             ("Project id", self.project_id),
                             ("Application", self.application), 
                             ("Run setup", getattr(self,"sequencing_setup")),
                             ("Best practice analysis", self.best_practice_bioinformatics),
                             ("Lanes ordered", getattr(self,"sequence_units_ordered_(lanes)")),
                             ("Number of samples", self.no_of_samples),
                             ("Reference Genome", self.reference_genome), 
                             ("Minimum ordered reads(M)", self.get_min_reads()),
                             ("Order recieved", self.order_received_date()),
                             ("Contract recieved", self.contract_received_date()),
                             ("Samples recieved", self.samples_received_date()),
                             ("Queue data", self.queued_date()),
                             ("All data delivered", datetime.datetime.now().strftime("%Y-%m-%d")),
                             ("UPPNEX id", self.uppnex_id),
                             ("UPPNEX project path", "/proj/{}/INBOX/{}".format(self.uppnex_id,self.project_name))])
        return _make_rst_table([["**Fields**","**Info**"]] + [[k,v] for k,v in order_info_fields.items()])
    
    # to fetch and create a template text to be entered in report for library prep method(s)
    def get_libPrep_method(self):
        libPrep_template = '  + **{}:** Library was prepared using "{}" protocol.'
        prep_methods = [self.details.get("library_construction_method")]
        all_methods = []
        for cnt in range(len(prep_methods)):
            all_methods.append(libPrep_template.format(alphabets[cnt],prep_methods[cnt]))
            self.accredit_info["Library preparation"] = "|{}|".format("Yes" if prep_methods[cnt] in self.accredited_libMethods else "No")
        return "\n\n".join(all_methods)
    
    # to fetch and create a template text to be entered in report for sequencing method(s)
    def get_seq_method(self):
        seq_template = '  + **{}:** Clustered using {} and sequenced on {} ({}) with a {} setup in {} mode.'
        if not self.flowcells:
            self.project_flowcells()
        seq_method_info = []
        
        # see through all flowcells run for this project sequencing methonds
        for fc in self.flowcells:
            fc_runp = fc.RunParameters
            seq_plat = ["HiSeq2500","MiSeq"]["MCSVersion" in fc_runp.keys()] 
            clus_meth = ["cBot","onboard clustering"][seq_plat == "MiSeq" or fc_runp.get("ClusteringChoice","") == "OnBoardClustering"]
            run_setup = fc.run_setup
            run_mode = fc_runp.get("RunMode","High Output")
            if seq_plat == "MiSeq":
                seq_software = "MSC {}/RTA {}".format(fc_runp.get("MCSVersion"),fc_runp.get("RTAVersion"))
            else:
                seq_software = "{} {}/RTA {}".format(fc_runp.get("ApplicationName"),fc_runp.get("ApplicationVersion"),fc_runp.get("RTAVersion"))
            tmp_method = seq_template.format("SECTION", clus_meth, seq_plat, seq_software, run_setup, run_mode)
            ## to make sure the sequencing methods are uniq
            if tmp_method not in seq_method_info:
                seq_method_info.append(tmp_method)
                
        ## give proper section name for the methods
        seq_method_info = [seq_method_info[c].replace("SECTION",alphabets[c]) for c in range(len(seq_method_info))]
        self.accredit_info["Sequencing data"] = "|Yes|"
        return "\n\n".join(seq_method_info)

    def accredition_table(self):
        self.accredit_info["Demultiplexing"] = "|Yes|"
        self.accredit_info["Data flow"] = "|Yes|"
        self.accredit_info["Data processing"] = "|Yes|"
        return _make_rst_table([["**Methods used**","**Swedac accredited**"]] + [[k,v] for k,v in self.accredit_info.items()])

class ProjectSampleReportObject(ReportObject):
    
    def __init__(self, ctrl, dbobj, project_name, scon=None):
        ReportObject.__init__(self,ctrl,dbobj,scon)
        self.details = self.dbobj.get("details",{})
        self.library_prep = self.dbobj.get("library_prep",{})
        self.project_name = project_name
        self._sample_run_objs()
    
    def __repr__(self):
        return "<ProjectSampleReportObject {}>".format(self.scilife_name)

    def __getattr__(self, name):
        return self.dbobj.get(name,self.details.get(name))
    
    def _sample_run_objs(self):
        """Connect to the samples database and fetch sample_run_metrics documents for sequencing runs belonging to this sample
        """
        # Get all sample runs for the project and create objects 
        self.sample_run_objs = {sample_run_doc.get("_id"):SampleRunReportObject(self.ctrl,sample_run_doc) for sample_run_doc in self.dbcon.get_project_sample(self.scilife_name, sample_prj=self.project_name)}
        ids = self.sample_run_objs.keys()
        
        # Match the document ids to the sample_run_metrics entries under the corresponding prep
        for prep in self.library_prep.keys():
            for lane_run_data in self.library_prep[prep].get("sample_run_metrics",{}).values():
                doc_id = lane_run_data.get("sample_run_metrics_id")
                try:
                    ids.remove(doc_id)
                    self.sample_run_objs[doc_id].library_prep = prep
                except ValueError:
                    self.log.warn("No sample_run_metrics document for run {} with id {} found in samples database!".format(lane_run,doc_id))
        for id in ids:
            self.log.warn("sample_run_metrics document found for run {} but no corresponding entry in projects database. Please check for inconsistencies!".format(self.sample_run_objs[id].get("name","N/A")))
            self.sample_run_objs[id].library_prep = "N/A"
        self.sample_run_objs = self.sample_run_objs.values() 
            
    def library_prep_status(self):
        """Go through all preps and check if any of them have passed"""
        return "PASS" if any([prep.get("prep_status","").lower() == "passed" for prep in self.library_prep.values()]) else "FAIL"
    def library_prep_table_data(self):
        return [[k,
                 self.library_prep_fragment_size(k),
                 ", ".join(self.library_prep[k].get("reagent_labels",[])),
                 self.library_prep[k].get("prep_status")] for k in sorted(self.library_prep.keys())]
    def library_prep_table(self):
        return _make_rst_table([["Library prep", "Average fragment size (bp)", "Index", "Library validation"]] + self.library_prep_table_data())
    def library_prep_fragment_size(self, prep):
        validation = self._latest_library_validation(prep)
        if not validation:
            return None
        return validation.get("average_size_bp")
    def sample_run_flowcells(self, prep=None):
        return list(set(["_".join(k.split("_")[0:3]) for lbl, data in self.library_prep.items() for k in data.get("sample_run_metrics",{}).keys() if not prep or prep == lbl]))
    def project_sample_name_table_data(self):
        return [self.scilife_name, self.customer_name]
    def sample_status_table_data(self):
        return [self.scilife_name, 
                self.initial_QC_status or "N/A", 
                self.library_prep_status(), 
                self.status or "N/A", 
                self.m_reads_sequenced]

    def _latest_library_validation(self, prep):
        """Determines the latest library validation based on 1) date, 2) lims id
        """
        if prep not in self.library_prep:
            self.log.warn("Library prep {} is not in the list of library preps for sample {}".format(prep,self.scilife_name))
            return None
        
        validations = self.library_prep[prep].get("library_validation")
        if not validations:
            self.log.warn("Library prep {} for sample {} does not have any library validation".format(prep,self.scilife_name))
            return None
            
        # Sort first by the lims id which will break ties when sorting on date
        keys = sorted(validations.keys(), reverse=True)
        # Then  sort by starting date
        keys = sorted(keys, key=lambda k: self._parse_date(validations[k].get("start_date")), reverse=True)
        # Return the most recent validation
        return validations[keys[0]]

    def sample_run_table(self, project, flowcell=None):
        return _make_rst_table([["Library prep", "Sequencing started", "Flowcell ID", "Flowcell position", "Lane", "Reads (M)", "Yield (Mbases)", "Average Q", "Q30 (%)", "Perfect index read (%)"]] + [summary for prep in sorted(self.library_prep.keys()) for summary in self.sample_run_table_data(project, prep, flowcell)])
        
    def sample_run_table_data(self, project, prep=None, flowcell=None):
        """Compile the results related to a sample run by combining information from the sample object and the flowcell object
        """
        sample_run_data = []
        # Loop over the preps and compile data for each of the sample runs
        for sprep in self.library_prep.keys():
            if prep and prep != sprep:
                continue
            # Get the list of flowcells for which there exists sample_run_metrics sections in the project database entry
            sample_runs = [[sr.split("_")[0],"_".join(sr.split("_")[1:3])] for sr in self.sample_run_flowcells(sprep)]
            # If we are restricting to a particular flowcell, prune the sample_runs list
            if flowcell:
                sample_runs = [sr for sr in sample_runs if sr[1] == flowcell]
            # Compile information for each flowcell in the project
            for lane, run in sorted(sample_runs, key=lambda s: (s[1],s[0])):
                [fcobj] = [fc for fc in project.flowcells if fc.name == run]
                if fcobj is None:
                    self.log.warn("Could not find flowcell object corresponding to sample run {} for sample {}, please check database/python code!".format(run,self.scilife_name))
                    continue
                splobj = fcobj.flowcell_samples.get(self.scilife_name,{}).get(lane)
                if splobj is None:
                    self.log.warn("Could not find sample flowcell object corresponding to sample run {} for sample {}, please check database/python code!".format(run,self.scilife_name))
                    continue
                for spl in splobj.values():
                    sample_run_data.append([sprep,
                                            fcobj.Date,
                                            fcobj.Flowcell,
                                            fcobj.FCPosition,
                                            spl.lane,
                                            int(spl.reads)/1e6,
                                            spl.yield_bases,
                                            spl.avgQ,
                                            spl.q30,
                                            spl.mm0])
        return sample_run_data

    def sample_delivery_table(self):
        return _make_rst_table([["Library prep", "Flowcell ID", "Lane", "Read", "File size (bytes)", "Checksum", "Path"]] + [f for obj in sorted(self.sample_run_objs, key=lambda o: "_".join([o.library_prep,o.flowcell,o.lane])) for f in obj.sample_delivery_table_data()])
        
