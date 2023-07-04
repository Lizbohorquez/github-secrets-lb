import re

import requests
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RunService:
    """
    A class that provides methods to interact with GitHub workflow runs.
    """

    def __init__(self, token, owner):
        """
        Initializes the RunService.
        Args:
            token (str): GitHub authentication token.
            owner (str): Repository owner username.
        """
        self.token = token
        self.owner = owner
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def get_run_status(self, repo, workflow_id):
        """
         Retrieves the status of the latest run for a specific workflow in a repository.
         Args:
            repo (str): Repository name.
            workflow_id (str): Workflow ID.
        Returns:
            dict: Run status details.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}/runs?created={current_date}&per_page=1'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_logs(self, repo, run_id):
        """
        Retrieves the logs of a specific workflow run in a repository.
        Args:
            repo (str): Repository name.
            run_id (str): Run ID.
        Returns: dict Logs details.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}/attempts/1/logs'
        response = requests.get(url, headers=self.headers, stream=True)
        file_name = '../logs.zip'
        chunk_size = 128
        p = re.compile('Is present in AWS.*')
        result = {}
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
        # files_to_extract = ['1_get-qa-secrets.txt', '1_get-st-secrets.txt', '1_get-pr-secrets.txt']
        files_to_extract = {
            'qa': '1_get-qa-secrets.txt',
            'st': '1_get-st-secrets.txt',
            'pr': '1_get-pr-secrets.txt'
        }
        with zipfile.ZipFile(file_name, 'r') as zip:
            zip.extract('1_get-qa-secrets.txt', '')
            zip.extract('1_get-st-secrets.txt', '')
            zip.extract('1_get-pr-secrets.txt', '')
        for env in list(dict.fromkeys(files_to_extract)):
            with open(files_to_extract[env], 'r') as file:
                out = file.read()
                result[env] = p.findall(out)
        return result


    def delete_logs(self, repo, run_id):
        """
        Deletes the logs of a specific workflow run in a repository.
        Args:
            repo (str): Repository name.
            run_id (str): Run ID.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}'
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 204:
            print(f'Logs eliminados para el run {run_id}')
        else:
            print(f'fallo eliminacion de logs para el run {run_id}. Status code: {response.status_code}')

    def approve_pending_deployments(self, repo, run_id, environments):
        """
        Approves pending deployments for specific environments in a workflow run.
        Args:
            repo (str): Repository name.
            run_id (str): Run ID.
            environments (list): List of environment IDs.
        Returns: (dict) Response from the GitHub API.
        """
        url = f"https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}/pending_deployments"
        data = {
            "environment_ids": environments,
            "state": "approved",
            "comment": "Deployments approved..."
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def list_environments(self, repo):
        """
        Lists all environments in a repository.
        Args: repo (str): Repository name.
        Returns: (dict) Environment details.
        """
        url = f"https://api.github.com/repos/{self.owner}/{repo}/environments"
        response = requests.get(url, headers=self.headers)
        return response.json()
