""" Common reports module.
Place for code common to all reports.
eg. Information retrieval from the filesystem or Charon
"""

import collections
import os
import re
import xmltodict
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
        self.date_format = "%Y-%m-%d"
        self.creation_date = datetime.now().strftime(self.date_format)


    def parse_piper_xml(self):
        """ Parses the XML setup files that Piper uses
        """

        def _nextitem(xml):
            # One sample
            if isinstance(xml, dict):
                yield xml
            # Many samples
            elif isinstance(xml, list):
                for i in xml:
                    yield i
            else:
                # This is passed below so doesn't halt execution
                raise KeyError("Could not parse run['inputs']['sample']")

        def _getfcid(str):
            pat = r'^[AB]?([a-zA-Z0-9\-]{8,20})'
            m = re.match(pat,str)
            if m is not None:
                return m.group(1)
            return str

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
                    for sample in _nextitem(run['inputs']['sample']):
                        try:
                            fcid = [_getfcid(pfu['unitinfo']) \
                                for library in _nextitem(sample['library']) \
                                for pfu in _nextitem(library['platformunit'])]
                        except (IndexError, KeyError) as e:
                            self.LOG.warning('Could not parse platform unit info in sample XML file: {}'.format(e.message))
                            fcid = ['N/A']
                        sid = sample['samplename']
                        samples[sid] = {'id': sid, 'run_id': ';'.join(set(fcid))}
                except KeyError as e:
                    self.LOG.warning('Could not find essential key in sample XML file: '+e.message)
                    pass

                # Non-Essential fields
                try:
                    project['sequencing_platform'] = run['metadata']['platform']
                    project['ref_genome'] = os.path.basename(run['metadata']['reference'])
                except KeyError as e:
                    self.LOG.warning('Could not find optional key in sample XML file: '+e.message)
                    pass

        return {'project': project, 'samples': samples}


    def flatten_dict(self, d, parent_key="", sep="."):
        """
        Flattens a dict by concatenating the keys
        separated by the specified separator (sep) until it finds a value.
        Optionally it adds parent_key as a prefix.
        E.g. {my : {nested: {key: value}}} -> "my.nested.key: value"
        """
        items = []
        for k, v in d.items():
            new_key = "{}{}{}".format(parent_key, sep, k) if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(list(self.flatten_dict(v, new_key, sep=sep).items()))
            else:
                items.append((new_key, v))
        return dict(items)
