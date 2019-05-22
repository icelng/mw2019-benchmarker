from logging import getLogger
from benchmark.model.common import Common
from benchmark.model.workspace import Workspace
from benchmark.model.error import WorkflowError


class Providers(Common):

    def __init__(self, config, hostname, scale, task):
        super(Providers, self).__init__(config, scale, task)
        self.logger = getLogger(__name__)
        #self.hostnames = [ self.config.provider_small_hostname,
        #        self.config.provider_medium_hostname,
        #        self.config.provider_large_hostname]
        #self.scales = ["small", "medium", "large"]
        self.hostnames = [hostname]
        self.scales = [scale]
        self.app_sha256 = self.config.provider_app_sha256
        self.script_sha256 = self.config.provider_script_sha256

    def start(self):
        for hostname, scale in zip(self.hostnames, self.scales):
            self._start(hostname, scale)

    def _start(self, hostname, scale):

        self.logger.info(f">>> Start provider services on {hostname}.")

        #remote = RemoteHost(self.config, scale, self.task)
        remote = self.workspace.remote
        task = self.task
        task_home = remote.task_home
        period = self.config.cpu_period
        max_attempts = self.config.max_attempts
        ncat_image_path = self.NCAT_IMAGE_PATH
        sleep = self.config.sleep_interval

        if scale == "small":
            cpu_set = self.config.small_provider_cpu_set
            quota = self.config.small_provider_cpu_quota
            memory = self.config.small_provider_memory
            provider_port = self.config.provider_small_port
        elif scale == "medium":
            cpu_set = self.config.medium_provider_cpu_set
            quota = self.config.medium_provider_cpu_quota
            memory = self.config.medium_provider_memory
            provider_port = self.config.provider_medium_port
        else:
            cpu_set = self.config.large_provider_cpu_set
            quota = self.config.large_provider_cpu_quota
            memory = self.config.large_provider_memory
            provider_port = self.config.provider_large_port

                #--cpu-period={period} \
                #--cpu-quota={quota} \

        script = f"""
            PROVIDER_HOME={task_home}/provider-{scale}
            rm -rf $PROVIDER_HOME
            mkdir -p $PROVIDER_HOME/logs
            cat ~/.passwd | sudo -S -p '' docker run -d \
                --net=host \
                --name=provider-{scale} \
                --cpuset-cpus={cpu_set} \
                --cidfile=$PROVIDER_HOME/run.cid \
                --memory={memory} \
                --ulimit nofile=4096:20480 \
                -p {provider_port}:{provider_port} \
                -v $PROVIDER_HOME/logs:/root/runtime/logs \
                provider provider-{scale}
        """.rstrip()

                #cat ~/.passwd | sudo -S -p '' \
                #    docker run --network host --rm {ncat_image_path} \
        script += f"""
            # noqa: E501

            ATTEMPTS=0
            MAX_ATTEMPTS={max_attempts}
            while true; do
                echo "Trying to connect provider-small..."
                ncat -v -w 1 --send-only {hostname} {provider_port}; r1=$?

                if [[ $r1 -eq 0 ]]; then
                    exit 0
                fi
                if [[ $ATTEMPTS -eq $MAX_ATTEMPTS ]]; then
                    echo "Cannot connect to some of the provider services after $ATTEMPTS attempts."
                    exit 1
                fi
                ATTEMPTS=$((ATTEMPTS+1))
                echo "Waiting for {sleep} seconds... ($ATTEMPTS/$MAX_ATTEMPTS)"
                sleep {sleep}
            done
        """.rstrip()

        returncode, _, _ = self._run_remote_script(hostname, script)
        if returncode != 0:
            raise WorkflowError('Failed to start provider services.', error_code=self.FAILED_TO_START_PROVIDER_SERVICES)

    def build_docker_images(self):
        for hostname in self.hostnames:
            self._build_docker_images(hostname, self.config.user_code_address,"provider")

    def upload_docker_file(self):
        for hostname in self.hostnames:
            self._upload_docker_file(hostname)

    def lock_remote_task_home(self):
        for hostname in self.hostnames:
            self._lock_remote_task_home(hostname)

    def create_remote_task_home(self):
        for hostname in self.hostnames:
            self._create_remote_task_home(hostname)

    def stop(self):
        for hostname in self.hostnames:
            self._stop(hostname)

    def _stop(self, hostname):
        self.logger.info('>>> Stop provider services.')

        template = """
            # noqa: E501

            CID_FILE={task_home}/provider-{scale}/run.cid
            if [[ -f $CID_FILE ]]; then
                CID=$(cat $CID_FILE)
                cat ~/.passwd | sudo -S -p '' docker stop $CID
                cat ~/.passwd | sudo -S -p '' docker logs $CID > {task_home}/provider-{scale}/logs/docker.log
                cat ~/.passwd | sudo -S -p '' docker rm $CID
                rm -f $CID_FILE
            else
                echo "CID file $CID_FILE not found."
            fi
        """.rstrip()

        for scale in self.scales:
            script = template.format(task_home=self.workspace.remote.task_home, scale=scale)  # noqa: E501
            script += """
                exit 0
            """.rstrip()

            returncode, _, _ = self._run_remote_script(hostname, script)
            if returncode != 0:
                self.logger.warn('Failed to stop provider services.')

    def remove_docker_images(self):
        for hostname in self.hostnames:
            self._remove_docker_images(hostname, "provider")

    def unlock_remote_task_home(self):
        for hostname in self.hostnames:
            self._unlock_remote_task_home(hostname)

    def download_logs(self):
        for hostname in self.hostnames:
            self._download_logs(hostname)

    def check_signatures(self):
        for hostname in self.hostnames:
            self._check_signatures(hostname, "provider", self.app_sha256, self.script_sha256)

