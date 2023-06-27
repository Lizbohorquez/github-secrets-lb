import time

from dotenv import load_dotenv
import os
from services.repo_service import RepoService
from services.workflow_service import WorkflowService
from services.run_service import RunService
from entities.repo import Repo
from entities.workflow import Workflow
from entities.run import Run
import logging

logger = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.
token = os.getenv('GITHUB_TOKEN')
username = os.getenv('USERNAME')
workflow_pattern = os.getenv('WORKFLOW_PATTERN')
secret_pattern = os.getenv('SECRET_PATTERN')
branch_name = os.getenv('BRANCH')

repo_serv = RepoService(token, username)
workflow_serv = WorkflowService(token, username)
run_serv = RunService(token, username)

environments = ['st', 'pr']


def get_repos(regex_pattern):
    repo_list = list()
    for rep in repo_serv.filter_repos(pattern=regex_pattern):
        repo_list.append(Repo(rep['id'], rep['name']))
    return repo_list


def get_secret_workflow(repo_name):
    # res = workflow_serv.get_workflows(repo_name, workflow_pattern)[0]
    res = workflow_serv.get_any_workflow(repo_name)
    return Workflow(res['id'], res['name']), res['path'].replace('.github/workflows/', '')


def start_workflow(repo_name, workflow_id, access_key_id, branch, secret_regx):
    return workflow_serv.dispatch_workflow(repo_name, workflow_id, access_key_id, branch, secret_regx)


def get_run(repo_name, workflow_id):
    result = None
    for _ in range(5):
        time.sleep(10)
        try:
            res = run_serv.get_run_status(repo_name, workflow_id)['workflow_runs'][0]
            result = Run(res['id'], res['status'])
            break
        except:
            logger.error(f"Attempt {_ + 1} for get run status failed.")
    return result


def get_secrets(repo_name, run_id):
    return run_serv.get_logs(repo_name, run_id)


def create_branch_and_update_workflow(repo_name, branch, workflow_filename):
    repo_serv.create_branch(repo_name, branch)
    [repo_serv.update_environment(repo_name, env) for env in environments]
    # [repo_serv.update_environment(repo_name, env) for env in ['pr', 'st']]
    local_path = os.getcwd() + "/secret.yml"
    remote_path = f'.github/workflows/{workflow_filename}'
    print(workflow_filename)
    repo_serv.update_workflow(repo_name, branch, remote_path, local_path)
    # repo_serv.upload_workflow(repo_name, branch, remote_path, workflow_name)


def delete_branch_and_logs(repo_name, branch, run_id):
    repo_serv.delete_branch(repo_name, branch)
    run_serv.delete_logs(repo_name, run_id)


def approve_workflow_run(repo, run_id):
    environments_list = []
    [environments_list.append(env['id']) for env in run_serv.list_environments(repo)['environments'] if env['name'] in ['pr', 'st']]
    response = run_serv.approve_pending_deployments(repo, run_id, environments_list)
    return response


if __name__ == '__main__':
    pattern_input = input('Ingrese el patron para filtrar repositorios: \n')
    access_key_id = input('Ingrese la llave a buscar: \n')
    output = {}

    repos = get_repos(pattern_input)
    print("Repositorios a comparar:")
    [print(repo.name) for repo in repos]
    print("\n")
    if input("Desea continuar(y/n): ") != "y":
        exit("Programa terminado por el usuario")
    for repo in get_repos(pattern_input):
        try:
            workflow, workflow_filename = get_secret_workflow(repo.name)
            create_branch_and_update_workflow(repo.name, branch_name, workflow_filename)
            print(start_workflow(repo.name, workflow.id, access_key_id, branch_name, secret_pattern))
            run = get_run(repo.name, workflow_filename)
            if run.status == 'waiting':
                res = approve_workflow_run(repo.name, run.id)
                print(f"Approved code: {res.status_code}")
                time.sleep(5)
                run = get_run(repo.name, workflow_filename)
            found_secrets = get_secrets(repo.name, run.id)
            delete_branch_and_logs(repo.name, branch_name, run.id)
            # print(found_secrets)
            output[repo.name] = found_secrets
            print(f"{repo.name} verified!")
            try:
                repo_serv.update_environment(repo.name, 'st', True)
            except:
                logger.error("Error updating st environment to default protected branches.")
        except:
            logger.error(f"Failed to compare secrets in {repo.name}")
    print(output)

    # repo = Repo(token, username)
    # workflow = Workflow(token, username)
    # run = Run(token, username)
    # repos = repo.filter_repos(pattern=pattern)
    # [print(repo['name']) for repo in repos]
    # workflows = workflow.get_workflows(repos[0]['name'], workflow_pattern)
    # [print(workflow) for workflow in workflows]
    # workflow.dispatch_workflow(repos[0]['name'], workflows[0]['id'], '1234567890')
    # print(workflow.get_workflow_status(repos[0]['name']))
    # repo_id = repos[0]['name']
    # for i in range(5):
    #     time.sleep(20)
    #     runs = workflow.get_workflow_status(repo_id)['workflow_runs']
    #     if len(runs) > 0:
    #         break
    # [print(run) for run in runs if run['name'] == 'secret workflow']
    # found_secrets = run.get_logs(repo_id, runs[0]['id'])
    # print(found_secrets)
