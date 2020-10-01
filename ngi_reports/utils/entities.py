""" Define various entities and populate them
"""

class Sample:
    """Sample class
    """
    def __init__(self):
        self.customer_name = ''
        self.ngi_id        = ''
        self.preps         = {}
        self.qscore        = ''
        self.total_reads   = ''

    class Prep:
        """Prep class
        """
        def __init__(self):
            self.avg_size    = ''
            self.barcode     = ''
            self.label       = ''
            self.qc_status   = ''

class Flowcell:
    """Flowcell class
    """
    def __init__(self):
        self.date     = ''
        self.db       = ''
        self.lanes    = OrderedDict()
        self.name     = ''
        self.run_name = ''
        self.seq_meth = ''
        self.type     = ''

    class Lane:
        def __init__(self):
            self.avg_qval = ''
            self.cluster  = ''
            self.dates    = ''
            self.id       = ''
            self.name     = ''
            self.phix     = ''
            self.seq_meth = ''

class Project:
    """Project class
    """
    def __init__(self):
        self.aborted_samples = OrderedDict()
        self.accredit = {}
        self.application = ''
        self.best_practice = False
        self.cluster = ''
        self.contact = ''
        self.dates = ''#do something
        self.is_finished_lib = False
        self.is_hiseqx = False
        self.library_construction  = ''
        self.missing_fc  = False
        self.ngi_facility = ''
        self.ngi_id = ''
        self.ngi_name = ''
        self.not_as_million  = False
        self.num_samples = 0
        self.num_lanes = 0
        self.reference = { 'genome': None,
                            'organism': None }
        self.report_date = ''
        self.seq_setup = ''
        self.sequencing_methods  = ''
        self.signature  = ''
        self.skip_fastq = False
        self.support_email = ''
        self.total_lanes = 0
        self.user_ID = ''

    class AbortedSampleInfo:
        """Aborted Sample info class
        """
        def __init__(self):
            self.status = ''
            self.user_id = ''
