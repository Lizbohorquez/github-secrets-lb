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

    def get_run_status(self, repo):
        current_date = datetime.now().strftime("%Y-%m-%d")
        status = ""
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs?status=completed&created={current_date}&per_page=1'
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
                print(f'{env}: {p.findall(out)}')
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

    def get_check_runs(self, repo, run_id):
        url = f"https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}"
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if response.status_code == 200:
            run_data = response.json()
            check_suite_id = run_data['check_suite_id']
            print("check suite id:", check_suite_id)
            try:
                check_runs = self.get_check_runs_by_suite_id(repo, check_suite_id)
            except:
                logger.error("Couldn't get check runs for run id:", run_id)
                raise
            return check_runs
        else:
            logger.error(f"Failed to retrieve check run ID. Status code: {response.status_code}")
            raise

    def get_check_runs_by_suite_id(self, repo, check_suite_id):
        url = f"https://api.github.com/repos/{self.owner}/{repo}/check-suites/{check_suite_id}/check-runs"
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if response.status_code == 200:
            check_runs_data = response.json()["check_runs"]
            check_runs = [run["id"] for run in check_runs_data]
            return check_runs
        else:
            print(f"Failed to retrieve check runs. Status code: {response.status_code}")
            return None
