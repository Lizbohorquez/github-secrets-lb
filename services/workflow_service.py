import requests
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WorkflowService:
    """
    A class that provides methods to interact with GitHub workflows.
    """

    def __init__(self, token, owner):
        """
        Initializes the WorkflowService.
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

    def get_workflows(self, repo, pattern):
        """
        Retrieves all workflows in a repository that match a specified pattern.
        Args:
            repo (str): Repository name.
            pattern (str): Regular expression pattern to match workflow names.
        Returns: List of matching workflows.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows'
        p = re.compile(pattern)
        response = requests.get(url, headers=self.headers)
        workflows = response.json()['workflows']
        [print(workflow['name']) for workflow in workflows]
        return [workflow for workflow in workflows if p.match(workflow['name'])]

    def get_workflow(self, repo, workflow_id):
        """
        Retrieves details of a specific workflow in a repository.
        Args:
            repo (str): Repository name.
            workflow_id (str): Workflow ID.
        Returns: (dict) Workflow details.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_any_workflow(self, repo):
        """
        Retrieves details of any workflow in a repository.
        Args: repo (str): Repository name.
        Returns: (dict) Workflow details.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows'
        response = requests.get(url, headers=self.headers)
        workflows = response.json()['workflows']
        try:
            return workflows[0]
        except:
            logger.error(
                "Couldn't find any workflow in ", repo
            )
            raise

    def dispatch_workflow(self, repo, workflow_id, access_key_id, branch, secret_pattern):
        """
        Dispatches a workflow in a repository with specified inputs.
        Args:
            repo (str): Repository name.
            workflow_id (str): Workflow ID.
            access_key_id (str): Access key ID.
            branch (str): Branch name.
            secret_pattern (str): Secret pattern.
        Returns: Response from the GitHub API.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/workflows/{workflow_id}/dispatches'
        data = {
            'ref': branch,
            'inputs': {
                'access_key_id': access_key_id,
                'filter_secret_pattern': secret_pattern
            }
        }
        return requests.post(url, json=data, headers=self.headers)

    # def get_workflow_status(self, repo):
    #     current_date = datetime.now().strftime("%Y-%m-%d")
    #     url = f'https://api.github.com/repos/{self.owner}/{repo}/actions/runs?status=completed&created={current_date}&per_page=1'
    #     # add_headers = {
    #     #     'status': 'cancelled',
    #     #     'per_page': 1
    #     # }
    #     # headers = self.headers.update(add_headers)
    #     # print(headers)
    #     response = requests.get(url, headers=self.headers)
    #     return response.json()
