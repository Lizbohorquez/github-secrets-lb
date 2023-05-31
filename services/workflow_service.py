import requests
import re
from datetime import datetime, timedelta


class WorkflowService:

    def __init__(self, token, owner):
        self.token = token
        self.owner = owner
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def get_workflows(self, repo, pattern):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows'
        p = re.compile(pattern)
        response = requests.get(url, headers=self.headers)
        workflows = response.json()['workflows']
        [print(workflow['name']) for workflow in workflows]
        return [workflow for workflow in workflows if p.match(workflow['name'])]

    def get_workflow(self, repo, workflow_id):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_any_workflow(self, repo):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows'
        response = requests.get(url, headers=self.headers)
        workflows = response.json()['workflows']
        return workflows[0]

    def dispatch_workflow(self, repo, workflow_id, access_key_id, branch, secret_pattern):
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}/dispatches'
        data = {
            'ref': branch,
            'inputs': {
                'access_key_id': access_key_id,
                'filter_secret_pattern': secret_pattern
            }
        }
        return requests.post(url, json=data, headers=self.headers)

    def get_workflow_status(self, repo):
        current_date = datetime.now().strftime("%Y-%m-%d")
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs?status=completed&created={current_date}&per_page=1'
        # add_headers = {
        #     'status': 'cancelled',
        #     'per_page': 1
        # }
        # headers = self.headers.update(add_headers)
        # print(headers)
        response = requests.get(url, headers=self.headers)
        return response.json()
