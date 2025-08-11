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
        self.signature = kwargs.get("signature")

    def set_signature(self):
        """Set the signature for the report.
        Exit if not provided."""
        if not self.signature:
            self.LOG.error(
                "It is required to provide Signature/Name while generating 'project_summary' report, see -s opition in help"
            )
            raise SystemExit
        else:
            self.report_info["signature"] = self.signature