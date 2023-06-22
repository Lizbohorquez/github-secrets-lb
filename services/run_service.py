import re

import requests
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RunService:

    def __init__(self, token, owner):
        self.token = token
        self.owner = owner
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def get_run_status(self, repo, workflow_id):
        current_date = datetime.now().strftime("%Y-%m-%d")
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}/runs?status=waiting&created={current_date}&per_page=1'
        response = requests.get(url, headers=self.headers)
        print(response.json())
        res = response.json()['workflow_runs']
        if len(res) == 0:
            url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}/runs?status=completed&created={current_date}&per_page=1'
            response = requests.get(url, headers=self.headers)
        return response.json()

    def get_logs(self, repo, run_id):
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

    # Elimina el run del workflow ejecutado
    def delete_logs(self, repo, run_id):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}'
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 204:
            print(f'Logs eliminados para el run {run_id}')
        else:
            print(f'fallo eliminacion de logs para el run {run_id}. Status code: {response.status_code}')

    def approve_pending_deployments(self, repo, run_id, environments):
        url = f"https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}/pending_deployments"
        data = {
            "environment_ids": environments,
            "state": "approved",
            "comment": "Deployments approved..."
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def list_environments(self, repo):
        url = f"https://api.github.com/repos/{self.owner}/{repo}/environments"
        response = requests.get(url, headers=self.headers)
        return response.json()
