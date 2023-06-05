import base64
import requests
import re
import logging

logger = logging.getLogger(__name__)


class RepoService:

    def __init__(self, token, username):
        self.token = token
        self.owner = username
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def list_all_repos(self):
        url = f'https://api.github.com/users/{self.owner}/repos'
        return requests.get(url)

    def filter_repos(self, pattern):
        p = re.compile(pattern)
        all_repos = self.list_all_repos().json()
        filtered_repos = [repo for repo in all_repos if p.match(repo['name'])]
        return filtered_repos

    # Obtener el Sha de la rama "master"
    def get_commit_sha(self, repo_name, branch="master"):
        url = f'https://api.github.com/repos/{self.owner}/{repo_name}/branches/{branch}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            commit_sha = response.json().get("commit", {}).get("sha")
            return commit_sha
        return None

    # Crear la rama
    def create_branch(self, repo_name, branch):
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
        except:
            logger.error(f"Couldn't update workflow in at {branch} in {repo}")
            raise

    def upload_workflow(self, repo_name, branch, path_to_workflow, workflow_name):
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

    # Elimina la rama "test" del repo filtrado
    def delete_branch(self, repo_name, branch):
        url = f'https://api.github.com/repos/{self.owner}/{repo_name}/git/refs/heads/{branch}'
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print(f"La rama '{branch}' ha sido eliminada del repositorio '{repo_name}'.")
        else:
            print(f"Error al eliminar la rama '{branch}' del repositorio '{repo_name}'.")
