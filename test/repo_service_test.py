import pytest
from services.repo_service import RepoService
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
token = os.getenv('GITHUB_TOKEN')
username = os.getenv('USERNAME')

# Replace with repo name to test
REPO = ""


@pytest.fixture
def repo_service():
    repo_service = RepoService(token, username)
    yield repo_service


def test_list_all_repos(repo_service):
    assert isinstance(repo_service.list_all_repos(), list)


def test_filter_repos(repo_service):
    repo_list = list()
    pattern = "^Dev.*"
    expected_repo = "DevNet-Associate"
    for rep in repo_service.filter_repos(pattern=pattern):
        repo_list.append(rep['name'])
    assert expected_repo in repo_list


def test_update_environment(repo_service):
    repo_service.update_environment(REPO, 'st')
