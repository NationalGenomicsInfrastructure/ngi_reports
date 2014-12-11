""" Common reports module.
Place for code common to both Stockholm and Uppsala NGI Nodes.
eg. Information retrieval from the filesystem or Charon
"""

import os
import xmltodict
from datetime import datetime


class BaseReport(object):
    """ Base report object class. Provides some common fields and helper
    methods to be used by all report types.
    """
    
    def __init__(self, config, LOG, working_dir, **kwargs):
        # Incoming handles
        self.config = config
        self.LOG = LOG
        self.working_dir = working_dir
    
        # Setup
        ngi_node = config.get('ngi_reports', 'ngi_node')
    
        # Standalone fields
        self.date_format = "%Y-%m-%d"
        self.creation_date = datetime.now().strftime(self.date_format)
    
    
    def parse_piper_xml(self):
        """ Parses the XML setup files that Piper uses
        """
        project = {}
        samples = {}
        xml_files = []
        # Find XML files in working directory
        for file in os.listdir(self.working_dir):
            if file.endswith(".xml"):
                xml_files.append(os.path.join(self.working_dir, file))
        # Find XML files in setup_xml_files/
        setup_dir = os.path.join(self.working_dir, 'setup_xml_files')
        if os.path.isdir(setup_dir):
            for file in os.listdir(setup_dir):
                if file.endswith(".xml"):
                    xml_files.append(os.path.join(setup_dir, file))
        
        
        self.LOG.info('Found {} Piper setup XML file{}..'.format(len(xml_files), '' if len(xml_files) == 1 else 's'))
        for xml_fn in xml_files:
            try:
                with open(os.path.realpath(xml_fn)) as fh:
                    raw_xml = xmltodict.parse(fh)
            except IOError as e:
                self.LOG.warning("Could not open configuration file \"{}\".".format(xml_fn))
                pass
            else:
                run = raw_xml['project']
                # Essential fields   
                try:
                    project['id'] = run['metadata']['name']
                    project['ngi_name'] = run['metadata']['name']
                    # One sample
                    if isinstance(run['inputs']['sample'], dict):
                        sid = run['inputs']['sample']['samplename']
                        samples[sid] = {'id': sid}
                    # Many samples
                    elif isinstance(run['inputs']['sample'], list):
                        for sample in run['inputs']['sample']:
                            sid = sample['samplename']
                            samples[sid] = {'id': sid}
                    else:
                        # This is passed below so doesn't halt execution
                        raise KeyError("Could not parse run['inputs']['sample']")
                except KeyError as e:
                    self.LOG.warning('Could not find essential key in sample XML file: '+e.message)
                    pass
        
                # Non-Essential fields   
                try:
                    project['UPPMAXid'] = run['metadata']['uppmaxprojectid']
                    project['sequencing_platform'] = run['metadata']['platform']
                    project['ref_genome'] = os.path.basename(run['metadata']['reference'])
                except KeyError as e:
                    self.LOG.warning('Could not find optional key in sample XML file: '+e.message)
                    pass
        
        return {'project': project, 'samples': samples}