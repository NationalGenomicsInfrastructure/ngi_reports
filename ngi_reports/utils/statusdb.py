#!/usr/bin/env python

import os
import yaml
from datetime import datetime
from ibmcloudant import CouchDbSessionAuthenticator, cloudant_v1


class statusdb_connection(object):
    """Main class to make connection to the statusdb, by default looks for config
    file in home, if not try with provided config

    :param dict config: a dictionary with essential info to make a connection
    :param logger log: a logger instance to log information when necessary
    """

    def __init__(self, config=None, log=None):
        self.log = log
        default_config = os.path.join(
            os.environ.get("HOME"), ".ngi_config", "statusdb.yaml"
        )
        # if there is no first default config, try to get it from environ
        if not os.path.exists(default_config):
            default_config = os.path.join(os.environ.get("STATUS_DB_CONFIG"))
        try:
            with open(default_config) as f:
                conf = yaml.safe_load(f)
                config = conf["statusdb"]
        except IOError:
            if not config:
                raise SystemExit(
                    "Could not find any config info in '~/.ngi_config/statusdb.yaml' or ENV variable 'STATUS_DB_CONFIG'"
                )

        self.user = config.get("username")
        self.pwrd = config.get("password")
        self.url = config.get("url")
        self.display_url_string = f"https://{self.user}:********@{self.url}"

        # Initialize IBM Cloudant client
        authenticator = CouchDbSessionAuthenticator(self.user, self.pwrd)
        self.connection = cloudant_v1.CloudantV1(authenticator=authenticator)
        self.connection.set_service_url(f"https://{self.url}")

        # Test connection
        try:
            self.connection.get_server_information().get_result()
        except Exception as e:
            raise SystemExit(
                f"Connection failed for URL {self.display_url_string}. Error: {e}"
            )

    def get_project_flowcell(
        self, project_id, open_date="2015-01-01", date_format="%Y-%m-%d"
    ):
        """From information available in flowcell db connection collect the flowcell this project was sequenced

        :param project_id: NGI project ID to get the flowcells
        :param open_date: Open date of project to skip the check for all flowcells
        :param date_format: The format of specified open_date
        """
        try:
            open_date = datetime.strptime(open_date, date_format)
        except TypeError:
            open_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        project_flowcells = {}
        time_format = (
            "%Y%m%d"
            if type(self) is (NanoporeRunConnection or ElementRunConnection)
            else "%y%m%d"
        )
        date_sorted_fcs = sorted(
            list(self.proj_list.keys()),
            key=lambda k: datetime.strptime(k.split("_")[0], time_format),
            reverse=True,
        )
        for fc in date_sorted_fcs:
            if type(self) is NanoporeRunConnection:
                # 20220721_1216_1G_PAM62368_3ae8de85
                fc_date, fc_time, position, fc_name, fc_hash = fc.split("_")
            elif type(self) is ElementRunConnection:
                # 20250417_AV242106_A2440533805
                fc_date, sequencer_id, fc_name = fc.split("_")
            else:
                # 220404_000000000-K797K
                fc_date, fc_name = fc.split("_")
            if datetime.strptime(fc_date, time_format) < open_date:
                break
            if (
                project_id in self.proj_list[fc]
                and fc_name not in project_flowcells.keys()
            ):
                project_flowcells[fc_name] = {
                    "name": fc_name,
                    "run_name": fc,
                    "date": fc_date,
                    "db": self.dbname,
                }
        return project_flowcells


class ProjectSummaryConnection(statusdb_connection):
    def __init__(self, dbname="projects"):
        super(ProjectSummaryConnection, self).__init__()
        self.dbname = dbname

    def get_entry(self, name, use_id_view=False):
        """Retrieve entry from given db for a given name.

        :param name: unique name identifier (primary key, not the uuid)
        """
        try:
            doc = self.connection.post_view(
                db=self.dbname,
                ddoc="project",
                view="project_name" if not use_id_view else "project_id",
                key=name,
                reduce=False,
                include_docs=True,
            ).get_result()["rows"][0]["doc"]
            if not doc:
                if self.log:
                    self.log.warn(f"No entry '{name}' in {self.dbname}")
                return None
            return doc
        except Exception as e:
            if self.log:
                self.log.error(f"Error retrieving document '{name}': {e}")
            return None


class GenericRunConnection(statusdb_connection):
    def __init__(self, dbname=None):
        super(GenericRunConnection, self).__init__()

    def get_entry(self, name):
        try:
            doc = self.connection.post_view(
                db=self.dbname,
                ddoc="names",
                view="project_ids_list",
                key=name,
                reduce=False,
                include_docs=True,
            ).get_result()["rows"][0]["doc"]
            if not doc:
                if self.log:
                    self.log.warn(f"No entry '{name}' in {self.dbname}")
                return None
            return doc
        except Exception as e:
            if self.log:
                self.log.error(f"Error retrieving document '{name}': {e}")
            return None


class X_FlowcellRunMetricsConnection(GenericRunConnection):
    def __init__(self, dbname="x_flowcells"):
        super(X_FlowcellRunMetricsConnection, self).__init__()
        self.dbname = dbname
        self.proj_list = {
            row["key"]: row["value"]
            for row in self.connection.post_view(
                db=self.dbname, ddoc="names", view="project_ids_list", reduce=False
            ).get_result()["rows"]
            if row["key"]
        }


class ElementRunConnection(GenericRunConnection):
    def __init__(self, dbname="element_runs"):
        super(ElementRunConnection, self).__init__()
        self.dbname = dbname
        self.proj_list = {
            k["key"]: k["value"]
            for k in self.connection.post_view(
                db=self.dbname, ddoc="names", view="project_ids_list", reduce=False
            ).get_result()["rows"]
            if k["key"]
        }


class NanoporeRunConnection(GenericRunConnection):
    def __init__(self, dbname="nanopore_runs"):
        super(NanoporeRunConnection, self).__init__()
        self.dbname = dbname
        self.name_view = {
            row["key"]: row["id"]
            for row in self.connection.post_view(
                db=self.dbname, ddoc="names", view="name", reduce=False
            ).get_result()["rows"]
        }
        self.proj_list = {
            row["key"]: row["value"]
            for row in self.connection.post_view(
                db=self.dbname, ddoc="names", view="project_ids_list", reduce=False
            ).get_result()["rows"]
            if row["key"]
        }
