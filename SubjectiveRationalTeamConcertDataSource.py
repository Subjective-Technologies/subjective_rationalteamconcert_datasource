import os
import subprocess
import requests
from urllib.parse import urljoin

from subjective_abstract_data_source_package import SubjectiveDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class SubjectiveRationalTeamConcertDataSource(SubjectiveDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        server_url = self.params['server_url']
        project_area = self.params['project_area']
        repository_workspace = self.params['repository_workspace']
        target_directory = self.params['target_directory']
        username = self.params['username']
        password = self.params['password']

        BBLogger.log(f"Starting fetch process for RTC workspace '{repository_workspace}' from server '{server_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log("Authenticating with RTC server.")
            auth_command = [
                'lscm', 'login', '-r', server_url, '-u', username, '-P', password
            ]
            subprocess.run(auth_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Loading workspace '{repository_workspace}' into '{target_directory}'.")
            load_command = [
                'lscm', 'load', repository_workspace, '-d', target_directory
            ]
            subprocess.run(load_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Successfully loaded workspace '{repository_workspace}' into '{target_directory}'.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error during RTC operations: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error during RTC operations: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return SVG icon content, preferring a local icon.svg in the plugin folder."""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        try:
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#16335B"/><text x="12" y="13" font-size="6" fill="#fff" text-anchor="middle">RTC</text></svg>'

    def get_connection_data(self):
        """
        Return the connection type and required fields for Rational Team Concert.
        """
        return {
            "connection_type": "RationalTeamConcert",
            "fields": ["server_url", "project_area", "repository_workspace", "username", "password", "target_directory"]
        }

