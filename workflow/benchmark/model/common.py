import os
import subprocess
from pathlib import Path
from shlex import split
from logging import getLogger
from benchmark.model.workspace import Workspace
from benchmark.model.error import WorkflowError

class Common:

    BENCHMARKER_NETWORK_NAME = 'benchmarker'
    FAILED_TO_START_PROVIDER_SERVICES = 1090
    DOCKERFILE_PREFIX_PATH = 'debian-jdk8-'

    LOGS_FILE_NAME = 'logs.tar.gz'

    BENCHMARKER_NETWORK_SUBNET = '10.10.10.0/24'
    BENCHMARKER_NETWORK_GATEWAY = '10.10.10.1'
    NCAT_IMAGE_PATH = 'registry.cn-shanghai.aliyuncs.com/aliware2019/aliware:alpine-nmap-ncat'  # noqa: E501

    FAILED_TO_LOCK_LOCAL_WORKSPACE = 1010
    FAILED_TO_GENERATE_DOCKER_PASSWORD_FILE = 1020
    FAILED_TO_CREATE_REMOTE_TASK_HOME = 1030
    FAILED_TO_LOCK_REMOTE_TASK_HOME = 1040
    FAILED_TO_UPLOAD_DOCKER_PASSWORD_FILE = 1050
    FAILED_TO_LOGIN_TO_DOCKER_REPOSITORY = 1060
    FAILED_TO_PULL_DOCKER_IMAGES = 1070
    FAILED_TO_CHECK_IMAGE_APP_SIGNATURE = 1071
    FAILED_TO_CHECK_SCRIPT_SIGNATURE = 1073
    FAILED_TO_CREATE_DOCKER_NETWORK = 1074
    FAILED_TO_START_PROVIDER_SERVICES = 1090
    FAILED_TO_START_CONSUMER_SERVICE = 1100
    FAILED_TO_WARMUP_APPLICATIONS = 1110
    FAILED_TO_PRESSURE_APPLICATIONS = 1120
    FAILED_TO_UPLOAD_DOCKER_FILE = 1130
    FAILED_TO_BUILD_DOCKER_IMAGES = 1140

    VALID_ERRORS = [
        FAILED_TO_LOGIN_TO_DOCKER_REPOSITORY,
        FAILED_TO_PULL_DOCKER_IMAGES,
        FAILED_TO_CHECK_IMAGE_APP_SIGNATURE,
        FAILED_TO_CHECK_SCRIPT_SIGNATURE,
        FAILED_TO_START_PROVIDER_SERVICES,
        FAILED_TO_START_CONSUMER_SERVICE
    ]



    def __init__(self, config, endpoint_name, task):
        self.config = config
        self.task = task
        self.workspace = Workspace(self.config, endpoint_name, self.task)
        self.logger = getLogger(__name__)

    def _unlock_remote_task_home(self, hostname):
        self.logger.info('>>> Unlock remote task home.')

        script = """
            if [[ -f {lock_file} ]]; then
                rm -f {lock_file}
            fi
            exit 0
        """.format(lock_file=self.workspace.remote.lock_file).rstrip()

        returncode, _, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            self.logger.warn('Failed to unlock remote task home.')

    def _run_local_script(self, script):
        return self._run_script('bash', script)

    def _run_remote_script(self, hostname, script):
        ssh = f"ssh -T -o StrictHostKeyChecking=no {self.workspace.remote.user}@{hostname}"
        bash = split(ssh) + ['bash']
        return self._run_script(bash, script)

    def _run_script(self, bash, script):
        self.logger.debug('Script to execute:\n%s\n', script)
        with subprocess.Popen(
            bash,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8'
        ) as proc:
            outs, errs = proc.communicate(script)
            returncode = proc.returncode
            self.logger.debug('Return code = %s', returncode)
            self.logger.debug('The output is as following:\n%s', outs)
            return returncode, outs, errs

    def _build_docker_images(self, hostname, user_code_address, cname):
        self.logger.info(f">>> build docker images on {hostname}.")
        remote = self.workspace.remote
        script = f"""
            cat ~/.passwd | sudo -S -p '' docker build --no-cache \
                --build-arg user_code_address={user_code_address} \
                --tag={cname}:latest {remote.docker_file}/{self.DOCKERFILE_PREFIX_PATH}{cname}
        """.rstrip()
            #cat ~/.passwd | sudo -S -p '' docker pull {self.NCAT_IMAGE_PATH}

        returncode, _, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            raise WorkflowError('Failed to build Docker images.', error_code=self.FAILED_TO_BUILD_DOCKER_IMAGES)

    def _upload_docker_file(self, hostname):
        self.logger.info('>>> Upload Dockerfile and entrypoint.sh .')
        remote = self.workspace.remote
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("benchmarker/") + len("benchmarker/")]
        dockerfilePath = os.path.abspath(rootPath + 'dockerfile')
        script = f"""
                    if [[ -d {dockerfilePath} ]]; then
                        scp -r \
                            {dockerfilePath}/* \
                            {remote.user}@{hostname}:{remote.docker_file}
                    else
                        echo "Dockerfile not exists."
                        exit 1
                    fi
                    exit 0
                """.rstrip()
        returncode, outs, _ = self._run_local_script(script)
        if returncode == 0:
            return
        if returncode == 1:
            raise WorkflowError('Failed to upload Dockerfile due to file not exists.',  # noqa: E501
                error_code=1051)
        raise WorkflowError('Failed to upload Dockerfile.', error_code=self.FAILED_TO_UPLOAD_DOCKER_FILE)

    def _lock_remote_task_home(self, hostname):
        self.logger.info(f">>> Lock remote task home on {hostname}.")

        remote = self.workspace.remote
        script = """
            if [[ -f {ws.lock_file} ]]; then
                echo "Lock file exists."
                exit 1
            else
                touch {ws.lock_file}
            fi
            exit 0
        """.format(ws=remote).rstrip()

        returncode, outs, _ = self._run_remote_script(hostname, script)
        if returncode == 0:
            return
        if returncode == 1:
            raise WorkflowError('Failed to lock remote task home due to lock file exists.',
                error_code=1041)
        raise WorkflowError(
            'Failed to lock remote task home.',
            error_code=self.FAILED_TO_LOCK_REMOTE_TASK_HOME)

    def _create_remote_task_home(self, hostname):
        self.logger.info(f">>> Create remote task home on {hostname}.")

        remote = self.workspace.remote
        script = """
            mkdir -p {ws.task_home}
            mkdir -p {ws.task_home}/dockerfile
            exit 0
        """.format(ws=remote).rstrip()

        returncode, outs, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            raise WorkflowError(
                'Failed to create remote task home.',
                error_code=self.FAILED_TO_CREATE_REMOTE_TASK_HOME)

    def _lock_local_workspace(self):
        self.logger.info('>>> Lock local workspace.')

        local = self.workspace.local

        path = Path(local.home)
        if not path.exists():
            path.mkdir(parents=True)

        path = Path(local.lock_file)
        try:
            path.touch(exist_ok=False)
        except FileExistsError as err:
            raise WorkflowError(
                'Failed to lock local workspace due to lock file exists.',
                error_code=self.FAILED_TO_LOCK_LOCAL_WORKSPACE) from err
        except Exception as err:
            raise WorkflowError(
                'Failed to lock local workspace.',
                error_code=self.FAILED_TO_LOCK_LOCAL_WORKSPACE) from err

    def _remove_docker_images(self, hostname, cname):
        self.logger.info('>>> Remove Docker images.')

        script = f"""
            cat ~/.passwd | sudo -S -p '' docker rmi -f {cname}
            cat ~/.passwd | sudo -S -p '' docker rmi -f {self.NCAT_IMAGE_PATH}
        """.rstrip()

        returncode, outs, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            self.logger.warn('Failed to remove Docker images.')

    def _unlock_remote_task_home(self, hostname):
        self.logger.info('>>> Unlock remote task home.')

        script = """
            if [[ -f {lock_file} ]]; then
                rm -f {lock_file}
            fi
            exit 0
        """.format(lock_file=self.workspace.remote.lock_file).rstrip()

        returncode, outs, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            self.logger.warn('Failed to unlock remote task home.')

    def _unlock_local_task_home(self):
        self.logger.info('>>> Unlock local workspace.')
        local = self.workspace.local
        try:
            os.remove(local.lock_file)
        except Exception as err:
            self.logger.warn('Failed to unload local workspace. %s', err)

    def _download_logs(self, hostname):
        script = """
            cd {task_home}
            tar -czf ../{file_name} *
            exit 0
        """.format(
            task_home=self.workspace.remote.task_home,
            file_name=self.LOGS_FILE_NAME).rstrip()

        returncode, _, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            self.logger.warn('Failed to generate logs tarball.')

        remote=self.workspace.remote
        file_name=self.LOGS_FILE_NAME
        local=self.workspace.local

        script = f"""
            # noqa: E501

            scp {remote.user}@{hostname}:{remote.task_home}/../{file_name} {local.home}/{hostname}{file_name}
            exit 0
        """.rstrip()

        returncode, outs, _ = self._run_local_script(script)
        if returncode != 0:
            self.logger.warn('Failed to download logs tarball.')

    def _check_signatures(self, hostname, cname, jar_sha256sum, script_sha256):
        self.logger.info('>>> Check signatures.')

        script = f"""
            # noqa: E501

            if [[ -f /tmp/run.cid ]]; then
                cat ~/.passwd | sudo -S -p '' rm /tmp/run.cid
            fi
            [[ $? -ne 0 ]] && exit 100

            cat ~/.passwd | sudo -S -p '' docker run --rm -i --entrypoint='' {cname} bash -c 'sha256sum -c < <(echo {jar_sha256sum})'
            [[ $? -ne 0 ]] && exit 101

            cat ~/.passwd | sudo -S -p '' docker run --rm -i --entrypoint='' {cname} bash -c 'sha256sum -c < <(echo {script_sha256})'
            [[ $? -ne 0 ]] && exit 102
        """.rstrip()

        returncode, outs, _ = self._run_remote_script(hostname, script)
        if returncode == 0:
            return
        elif returncode == 100:
            raise WorkflowError(f"Failed to check signature on {hostname}.", error_code=returncode)
        elif returncode == 101:
            raise WorkflowError(f"Failed to check {hostname} app signature.",
                error_code=self.FAILED_TO_CHECK_IMAGE_APP_SIGNATURE)
        elif returncode == 102:
            raise WorkflowError(f"Failed to check script signature on {hostname}.",
                error_code=self.FAILED_TO_CHECK_SCRIPT_SIGNATURE)
