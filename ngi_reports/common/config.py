""" Load and parse configuration file
"""
import ConfigParser
import os

def load_config(config_file=None):
    """Loads a configuration file.

    By default it assumes ~/.ngi_reports/ngi_reports.conf
    """
    try:
        if not config_file:
            config_file = os.path.join(os.environ.get('HOME'), '.ngi_reports', 'ngi_reports.conf')
        config = ConfigParser.SafeConfigParser()
        with open(config_file) as f:
            config.readfp(f)
        return config
    except IOError:
        raise IOError(("There was a problem loading the configuration file. "
                "Please make sure that ~/.ngi_reports/ngi_reports.conf exists "
                "and that you have read permissions"))