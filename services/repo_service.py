import requests
import re


class RepoService:

    def __init__(self, token, username):
        self.token = token
        self.username = username
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def list_all_repos(self):
        url = f'https://api.github.com/users/{self.username}/repos'
        return requests.get(url)

    def filter_repos(self, pattern):
        p = re.compile(pattern)
        all_repos = self.list_all_repos().json()
        filtered_repos = [repo for repo in all_repos if p.match(repo['name'])]
        return filtered_repos
