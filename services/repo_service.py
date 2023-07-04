import base64
import json

import requests
import re
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()  # take environment variables from .env.
branch_name = os.getenv('BRANCH')


class RepoService:

    def __init__(self, token, username):
        """
        Initialize the RepoService instance.
        Args:
            token (str): GitHub authentication token.
            username (str): GitHub username/owner of the repositories.
        """
        self.token = token
        self.owner = username
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def list_all_repos(self):
        """
        Get a list of all repositories.
        Returns: list: List of repositories.
        """
        org_name = os.getenv('ORG')
        repositories = []
        page = 1
        per_page = 100
        timeout_seconds = 15  # Set your desired timeout value here
        if org_name != "":
            url = f"https://api.github.com/orgs/{org_name}/repos"
            while True:
                params = {
                    "page": page,
                    "per_page": per_page
                }
                try:
                    response = requests.get(url, headers=self.headers, params=params, timeout=timeout_seconds)
                    response.raise_for_status()  # Raise an exception for non-2xx status codes

                    data = response.json()
                    repositories.extend(data)

                    if len(data) < per_page:
                        break  # Reached the last page

                    page += 1

                except requests.exceptions.RequestException as e:
                    print("Failed to retrieve repositories:", str(e))
                    break


        else:
            url = f'https://api.github.com/users/{self.owner}/repos'
            res = requests.get(url, headers=self.headers)
            repositories.extend(res.json())
        return repositories

    def filter_repos(self, pattern):
        """
        Filter repositories based on a given pattern.
        Args: pattern (str): Regular expression pattern to filter repositories.
        Returns: List of filtered repositories.
        """
        p = re.compile(pattern)
        all_repos = self.list_all_repos()
        logger.info(f"Repo qty: {len(all_repos)}")
        filtered_repos = [repo for repo in all_repos if p.match(repo['name'])]
        return filtered_repos


    def get_commit_sha(self, repo_name, branch="master"):
        """
        Get the commit SHA of a branch in a repository.
        Args:
            repo_name (str): Repository name.
            branch (str, optional): Branch name. Defaults to "master".
        Returns: (str) Commit SHA of the branch.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo_name}/branches/{branch}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            commit_sha = response.json().get("commit", {}).get("sha")
            return commit_sha
        return None


    def create_branch(self, repo_name, branch):
        """
        Create a branch in a repository.
        Args:
            repo_name (str): Repository name.
            branch (str): Branch name.
        Returns: (dict) Response from the GitHub API.
        """
        commit_sha = self.get_commit_sha(repo_name)
        if commit_sha:
            url = f'https://api.github.com/repos/{self.owner}/{repo_name}/git/refs'
            data = {
                'ref': f'refs/heads/{branch}',
                'sha': commit_sha
            }
            response = requests.post(url, json=data, headers=self.headers)
            return response.json()
        else:
            return None

    def update_workflow(self, repo, branch, path, path_to_local_workflow):
        """
        Update a workflow file in a repository.
        Args:
            repo (str): Repository name.
            branch (str): Branch name.
            path (str): Path to the workflow file.
            path_to_local_workflow (str): Path to the local workflow file..
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/contents/{path}'
        # commit_sha = self.get_commit_sha(repo, branch)
        try:
            with open(path_to_local_workflow, 'r') as file:
                content = file.read()
                # Retrieve the existing workflow file details
                response = requests.get(url, headers=self.headers)
                workflow_data = response.json()
                sha = workflow_data['sha']
                data = {
                    'message': 'Updated workflow',
                    'content': base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                    'branch': branch,
                    'sha': sha
                }
                print(branch)
                response = requests.put(url, headers=self.headers, json=data)
                print(response)
                if response.status_code == 200:
                    logger.info(f"File updated successfully at {branch} in {repo}.")
                else:
                    print("Error updating file.")
        except ValueError:
            logger.error(f"Couldn't update workflow at {branch} in {repo} error: {ValueError}")
            raise

    def upload_workflow(self, repo_name, branch, path_to_workflow, workflow_name):
        """
        Upload a workflow file to a repository.
        Args:
            repo_name (str): Repository name.
            branch (str): Branch name.
            path_to_workflow (str): Path to the workflow file.
            workflow_name (str): Name of the workflow.
        """
        # self.create_branch(repo_name)
        commit_sha = self.get_commit_sha(repo_name, branch)
        url = f'https://api.github.com/repos/{self.owner}/{repo_name}/contents/.github/workflows/{workflow_name}?ref={branch}'
        try:
            with open(path_to_workflow, 'r') as file:
                content = file.read()

            data = {
                'message': 'Subir archivo de workflow',
                'content': base64.b64encode(content.encode()).decode(),
                'branch': branch,
                'sha': commit_sha
            }
            response = requests.put(url, json=data, headers=self.headers)
            if response.status_code == 201:
                print(f'Archivo de flujo de trabajo cargado en {repo_name} en la rama {branch}')
        except:
            print(f'Error al cargar el archivo de flujo de trabajo a {repo_name}. Status code: {response.status_code}')

        # if commit_sha:
        #
        #
        #
        #     else:
        # else:
        #     print(f'No se pudo crear o recuperar la confirmación SHA para la rama {branch} en el repositorio {repo_name}')


    def delete_branch(self, repo_name, branch):
        """
        Delete a branch from a repository.
        Args:
            repo_name (str): Repository name.
            branch (str): Branch name.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo_name}/git/refs/heads/{branch}'
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            logger.info(f"La rama '{branch}' ha sido eliminada del repositorio '{repo_name}'.")
        else:
            logger.error(f"Error al eliminar la rama '{branch}' del repositorio '{repo_name}'.")

    def create_deployment_branch_policy(self, repo, environment_name):
        """
        Create a deployment branch policy for an environment.
        Args:
            repo (str): Repository name.
            environment_name (str): Name of the environment.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/environments/{environment_name}/deployment-branch-policies'
        data = {
            "name": f"*{branch_name}*"
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            logger.info("Deployment branch policy created.")
        else:
            logger.error("Failed to create deployment branch policy. Status code:", response.status_code)

    def update_environment(self, repo, environment_name, is_protected_branches=False):
        """
        Update an environment in a repository.
        Args:
            repo (str): Repository name.
            environment_name (str): Name of the environment.
            is_protected_branches (bool, optional): Flag indicating if the environment has protected branches.
            Defaults to False.
        """
        url = f'https://api.github.com/repos/{self.owner}/{repo}/environments/{environment_name}'
        data = {
            "wait_timer": 0,
            # "reviewers": [],
            "deployment_branch_policy": {
                "protected_branches": is_protected_branches,
                "custom_branch_policies": not is_protected_branches
            }
        }
        response = requests.put(url, headers=self.headers, json=data)
        if response.status_code == 200 and not is_protected_branches:
            self.create_deployment_branch_policy(repo, environment_name)
            logger.info(f"{environment_name} environment updated successfully.")
        elif response.status_code == 200:
            logger.info(f"{environment_name} environment updated successfully.")
        else:
            logger.error("Failed to update environment. Status code:", response.status_code)
            raise

