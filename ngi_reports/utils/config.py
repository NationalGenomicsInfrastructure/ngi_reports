""" Load and parse configuration file
"""
import ConfigParser
import os
from string import Template

def load_config(config_file=None):
    """Loads a configuration file.

    By default it assumes ~/.ngi_config/ngi_reports.conf
    """
    try:
        if not config_file:
            config_file = os.path.join(os.environ.get('HOME'), '.ngi_config', 'ngi_reports.conf')
            if not os.path.exists(config_file):
                config_file = os.path.join(os.environ.get("NGI_REPORTS_CONFIG"))
        config = ConfigParser.SafeConfigParser({'ngi_node': 'unknown'})
        with open(config_file) as f:
            config.readfp(f)
        return config
    except IOError:
        raise IOError(("There was a problem loading the configuration file. "
                "Please make sure that ~/.ngi_config/ngi_reports.conf exists "
                "or env vairable 'NGI_REPORTS_CONFIG' is set with path to conf "
                "file and set with read permissions"))

def expand_path(input_path, substitutions):
    """Use python's string templates to replace substitution patterns in
        the input path for those available in the substitution dict
    """
    return Template(input_path).substitute(substitutions)