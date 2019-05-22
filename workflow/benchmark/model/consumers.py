from logging import getLogger
from benchmark.model.workspace import Workspace
from benchmark.model.error import WorkflowError
from benchmark.model.common import Common


class Consumers(Common):
    def __init__(self, config, task):
        super(Consumers, self).__init__(config, 'consumer', task)
        self.logger = getLogger(__name__)
        self.hostname = self.config.consumer_hostname
        self.app_sha256 = self.config.consumer_app_sha256
        self.script_sha256 = self.config.consumer_script_sha256

    def start(self):
        self.logger.info('>>> Start consumer service.')

        consumer_port = self.config.consumer_port
        task_home = self.workspace.remote.task_home
        period = self.config.cpu_period
        quota = self.config.consumer_cpu_quota
        cpu_set = self.config.consumer_cpu_set
        memory = self.config.consumer_memory
        image_path = self.task.image_path
        max_attempts = self.config.max_attempts
        ncat_image_path = self.NCAT_IMAGE_PATH
        sleep = self.config.sleep_interval
        provider_small_ip = self.config.provider_small_ip
        provider_medium_ip = self.config.provider_medium_ip
        provider_large_ip = self.config.provider_large_ip

                #--cpu-period={period} \
                #--cpu-quota={quota} \

        script = f"""
            # noqa: E501

            CONSUMER_HOME={task_home}/consumer
            rm -rf $CONSUMER_HOME
            mkdir -p $CONSUMER_HOME/logs
            cat ~/.passwd | sudo -S -p '' docker run -d \
                --net=host \
                --name=consumer \
                --cpuset-cpus={cpu_set} \
                --cidfile=$CONSUMER_HOME/run.cid \
                --memory={memory} \
                --ulimit nofile=4096:20480 \
                -p {consumer_port}:{consumer_port} \
                --add-host=provider-small:{provider_small_ip} \
                --add-host=provider-medium:{provider_medium_ip} \
                --add-host=provider-large:{provider_large_ip} \
                -v $CONSUMER_HOME/logs:/root/runtime/logs \
                consumer
        """

                #cat ~/.passwd | sudo -S -p '' \
                #    docker run --network host --rm {ncat_image_path} \

        script += f"""
            # noqa: E501

            ATTEMPTS=0
            MAX_ATTEMPTS={max_attempts}
            while true; do
                echo "Trying to connect consumer..."
                ncat -v -w 1 --send-only localhost {consumer_port}; r1=$?
                if [[ $? -eq 0 ]]; then
                    exit 0
                fi
                if [[ $ATTEMPTS -eq $MAX_ATTEMPTS ]]; then
                    echo "Cannot connect to consumer service after $ATTEMPTS attempts."
                    exit 1
                fi
                ATTEMPTS=$((ATTEMPTS+1))
                echo "Waiting for {sleep} seconds... ($ATTEMPTS/$MAX_ATTEMPTS)"
                sleep {sleep}
            done
        """.rstrip()

        returncode, outs, _ = self._run_remote_script(self.hostname, script)
        if returncode != 0:
            raise WorkflowError('Failed to start consumer service.',
                error_code=self.FAILED_TO_START_CONSUMER_SERVICE)

    def build_docker_images(self):
        self._build_docker_images(self.hostname, self.config.user_code_address,"consumer")

    def upload_docker_file(self):
        self._upload_docker_file(self.hostname)

    def lock_remote_task_home(self):
        self._lock_remote_task_home(self.hostname)

    def create_remote_task_home(self):
        self._create_remote_task_home(self.hostname)

    def stop(self):
        self.logger.info('>>> Stop consumer service.')
        task_home=self.workspace.remote.task_home
        script = f"""
            # noqa: E501

            CID_FILE={task_home}/consumer/run.cid
            if [[ -f $CID_FILE ]]; then
                CID=$(cat $CID_FILE)
                cat ~/.passwd | sudo -S -p '' docker stop $CID
                cat ~/.passwd | sudo -S -p '' docker logs $CID > {task_home}/consumer/logs/docker.log
                cat ~/.passwd | sudo -S -p '' docker rm $CID
                rm -f $CID_FILE
            else
                echo "CID file $CID_FILE not found."
            fi
            exit 0
        """.rstrip()

        returncode, outs, _ = self._run_remote_script(self.hostname, script)
        if returncode != 0:
            self.logger.warn('Failed to stop consumer service.')

    def remove_docker_images(self):
        self._remove_docker_images(self.hostname, "consumer")

    def unlock_remote_task_home(self):
        self._unlock_remote_task_home(self.hostname)

    def download_logs(self):
        self._download_logs(self.hostname)

    def check_signatures(self):
        self._check_signatures(self.hostname, "consumer", self.app_sha256, self.script_sha256)
