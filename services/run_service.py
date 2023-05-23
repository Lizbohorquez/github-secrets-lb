import re

import requests
import zipfile


class RunService:

    def __init__(self, token, owner):
        self.token = token
        self.owner = owner
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def get_logs(self, repo, run_id):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs/{run_id}/attempts/1/logs'
        response = requests.get(url, headers=self.headers, stream=True)
        file_name = '../logs.zip'
        chunk_size = 128
        p = re.compile('Is present in.*')
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
