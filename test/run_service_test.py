import pytest

from services.run_service import RunService
from services.workflow_service import WorkflowService
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()  # take environment variables from .env.
token = os.getenv('GITHUB_TOKEN')
username = os.getenv('USERNAME')
branch_name = os.getenv('BRANCH')

# Replace with repo name to test
REPO = "DevNet-Associate"


@pytest.fixture
def run_service():
    run_service = RunService(token, username)
    yield run_service


@pytest.fixture
def workflow_service():
    workflow_service = WorkflowService(token, username)
    yield workflow_service


# def test_get_pending_deployments(run_service):
#     deployments = run_service.list_all_deployments(REPO, branch_name)
#     for deploy in deployments:
#         logger.info(f"Number of deployments: {len(deployments)} \n"
#                     f" id: {deploy['id']} \n"
#                     f"environment: {deploy['environment']}")


def test_approve_deployment(run_service, workflow_service):
    res = workflow_service.get_any_workflow(REPO)
    workflow_id = res['id']
    run = run_service.get_run_status(REPO, workflow_id)['workflow_runs'][0]
    environments = []
    [environments.append(env['id']) for env in run_service.list_environments(REPO)['environments'] if env['name'] in ['pr', 'st']]
    response = run_service.approve_pending_deployments(REPO, run['id'], environments)
    logger.info(response)


def test_list_environments(run_service):
    response = run_service.list_environments(REPO)
    logger.info(response)
