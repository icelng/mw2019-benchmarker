import datetime
import random
import re
import time

from functools import partial
from logging import getLogger

from benchmark.model.providers import Providers
from benchmark.model.consumers import Consumers
from benchmark.model.common import Common
from benchmark.model.error import WorkflowError

class Workflow(Common):

    def __init__(self, config, task):
        super(Workflow, self).__init__(config, task)
        self.logger = getLogger(__name__)
        self.qps_pattern = re.compile(
            '^QPS:\s*(\d*\.\d*)', re.M | re.I)
        self.qps_result = 0

        self.providers = Providers(config, task)
        self.consumers = Consumers(config, task)

        self.logger.info('local workspace = %s', self.workspace.local)
        self.logger.info('remote workspace = %s', self.workspace.remote)

    def run(self):
        start = time.time()

        result = None
        try:
            self._lock_local_workspace()
            self.create_remote_task_home()
            self.lock_remote_task_home()
            self.upload_docker_file()
            self.build_docker_images()
            self.check_signatures()
            self.providers.start()
            self.consumers.start()
            self._warmup_then_pressure()
        except WorkflowError as err:
            result = {
                'status': -err.error_code,
                'is_valid': 1 if err.error_code in self.VALID_ERRORS else 0,
                'message': err.message,
                'rank': self.qps_result,
                'scoreJson': {
                    'qps': self.qps_result
                }
            }
            self.logger.exception('Failed to execute workflow.')
        finally:
            # self.stop_services()
            self._cleanup()
            self._collect_data()

        end = time.time()
        self.logger.info(
            'Time used: %s',
            datetime.timedelta(seconds=(end - start)))

        if result is not None:
            return result

        return {
            'status': 0,
            'is_valid': 1,
            'message': 'Success',
            'rank': self.qps_result,
            'scoreJson': {
                'qps': self.qps_result
            }
        }

    def create_remote_task_home(self):
        self.providers.create_remote_task_home()
        self.consumers.create_remote_task_home()

    def lock_remote_task_home(self):
        self.providers.lock_remote_task_home()
        self.consumers.lock_remote_task_home()

    def upload_docker_file(self):
        self.providers.upload_docker_file()
        self.consumers.upload_docker_file()

    def build_docker_images(self):
        self.providers.build_docker_images()
        self.consumers.build_docker_images()

    def check_signatures(self):
        self.providers.check_signatures()
        self.consumers.check_signatures()

    def _warmup_then_pressure(self):
        template = """
            sleep {sleep}
            wrk -t{threads} -c{connections} -d{duration} -T{timeout} \
                --script=./benchmark/wrk.lua \
                --latency http://{hostname}:{port}/invoke
            exit 0
        """.rstrip()
        tpl = partial(
            template.format,
            timeout=self.config.wrk_timeout,
            hostname=self.config.consumer_hostname,
            port=self.config.consumer_port)

        connections = self.config.connections
        self.logger.info('>>> Warmup.')
        script = ''
        script += tpl(
            sleep=5,
            threads=self.config.wrk_threads,
            connections=connections,
            duration=self.config.warmup_duration)

        returncode, outs, _ = self._run_local_script(script)
        if returncode != 0:
            raise WorkflowError(
                'Failed to warmup applications.',
                error_code=self.FAILED_TO_WARMUP_APPLICATIONS)

        self.logger.info(f">>> Pressure with {connections} connections.")
        script = ''
        script += tpl(
            sleep=5, threads=self.config.wrk_threads,
            connections=connections,
            duration=self.config.pressure_duration)
        returncode, outs, _ = self._run_local_script(script)
        if returncode != 0:
            raise WorkflowError(
                f"Failed to pressure applications with {connections} connections.",
                error_code=self.FAILED_TO_PRESSURE_APPLICATIONS)

        qps = self._extract_qps(outs)
        self.logger.info('QPS = %s', qps)
        self.qps_result = qps

    def _extract_qps(self, outs):
        match = self.qps_pattern.search(outs)
        if match is None:
            return -1
        return float(match.group(1))

    def stop_services(self):
        self.consumers.stop()
        self.providers.stop()

    def _cleanup(self):
        self.providers.remove_docker_images()
        self.consumers.remove_docker_images()
        self.providers.unlock_remote_task_home()
        self.consumers.unlock_remote_task_home()
        self._unlock_local_task_home()


    def _collect_data(self):
        self.logger.info('>>> Collect data.')
        self._compute_result()
        self.download_logs()

    def download_logs(self):
        self.providers.download_logs()
        self.consumers.download_logs()

    def _compute_result(self):
        self.logger.info('Result: QPS with %s connections.', self.qps_result)
        return self.qps_result
