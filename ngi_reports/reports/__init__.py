""" Common reports module.
Place for code common to all reports.
eg. Information retrieval from the filesystem or Charon
"""

from datetime import datetime


class BaseReport(object):
    """ Base report object class. Provides some common fields and helper
    methods to be used by all report types.
    """

    def __init__(self, LOG, working_dir, **kwargs):
        # Incoming handles
        self.LOG = LOG
        self.working_dir = working_dir

        # Standalone fields
        self.creation_date = datetime.now().strftime('%Y-%m-%d')
