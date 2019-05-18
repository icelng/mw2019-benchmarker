import configparser

DEFAULT_SECTION = "Default"
TIANCHI_SECTION = "Tianchi"
WORKSPACE_SECTION = "Workspace"
SERVICES_SECTION = "Services"
WRK_SECTION = "Wrk"
DOCKER_SECTION = "Docker"
REMOTE_SECTION = "Remote"


class Configuration():

    def __init__(self, config_file):
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read_file(config_file)

    def __get_value(self, key, section=DEFAULT_SECTION):
        return self.config[section][key]

    @property
    def consumer_app_sha256(self):
        return self.__get_value('ConsumerAppSha256')

    @property
    def provider_app_sha256(self):
        return self.__get_value('ProviderAppSha256')

    @property
    def provider_script_sha256(self):
        return self.__get_value('ProviderScriptSha256')

    @property
    def consumer_script_sha256(self):
        return self.__get_value('ConsumerScriptSha256')

    @property
    def access_token(self):
        return self.__get_value('Token', TIANCHI_SECTION)

    @property
    def race_id(self):
        return self.__get_value('RaceId', TIANCHI_SECTION)

    @property
    def task_fetch_url(self):
        tianchi_host = self.__get_value('Host', TIANCHI_SECTION)
        task_fetch_path = self.__get_value('TaskFetchPath', TIANCHI_SECTION)
        return '{}{}'.format(tianchi_host, task_fetch_path)

    @property
    def task_update_url(self):
        tianchi_host = self.__get_value('Host', TIANCHI_SECTION)
        task_update_path = self.__get_value('TaskUpdatePath', 'Tianchi')
        return '{}{}'.format(tianchi_host, task_update_path)

    @property
    def workspace_home(self):
        return self.__get_value('Home', WORKSPACE_SECTION)

    @property
    def remote_host_user(self):
        return self.__get_value('RemoteHostUser', WORKSPACE_SECTION)

    @property
    def provider_small_hostname(self):
        return self.__get_value("AllInOneIp", REMOTE_SECTION)

    @property
    def provider_small_ip(self):
        return self.__get_value("ProviderSmallIp", REMOTE_SECTION)

    @property
    def provider_medium_hostname(self):
        return self.__get_value("AllInOneIp", REMOTE_SECTION)

    @property
    def provider_medium_ip(self):
        return self.__get_value("ProviderMediumIp", REMOTE_SECTION)

    @property
    def provider_large_hostname(self):
        return self.__get_value("AllInOneIp", REMOTE_SECTION)

    @property
    def provider_large_ip(self):
        return self.__get_value("ProviderLargeIp", REMOTE_SECTION)

    @property
    def all_in_one_ip(self):
        return self.__get_value("AllInOneIp", REMOTE_SECTION)

    @property
    def provider_small_port(self):
        return self.__get_value("ProviderSmallPort", REMOTE_SECTION)

    @property
    def provider_medium_port(self):
        return self.__get_value("ProviderMediumPort", REMOTE_SECTION)

    @property
    def provider_large_port(self):
        return self.__get_value("ProviderLargePort", REMOTE_SECTION)

    @property
    def consumer_port(self):
        return self.__get_value("ConsumerPort", REMOTE_SECTION)

    @property
    def consumer_hostname(self):
        return self.__get_value("AllInOneIp", REMOTE_SECTION)

    @property
    def max_attempts(self):
        return self.__get_value('MaxAttempts', SERVICES_SECTION)

    @property
    def sleep_interval(self):
        return self.__get_value('SleepInterval', SERVICES_SECTION)

    @property
    def wrk_threads(self):
        return self.__get_value('Threads', WRK_SECTION)

    @property
    def wrk_timeout(self):
        return self.__get_value('Timeout', WRK_SECTION)

    @property
    def warmup_duration(self):
        return self.__get_value('WarmupDuration', WRK_SECTION)

    @property
    def pressure_duration(self):
        return self.__get_value('PressureDuration', WRK_SECTION)

    @property
    def connections(self):
        return self.__get_value("Connections", WRK_SECTION)

    @property
    def cpu_period(self):
        return self.__get_value('CpuPeriod', DOCKER_SECTION)

    @property
    def small_provider_cpu_quota(self):
        return self.__get_value('SmallProviderCpuQuota', DOCKER_SECTION)

    @property
    def small_provider_memory(self):
        return self.__get_value('SmallProviderMemory', DOCKER_SECTION)

    @property
    def medium_provider_cpu_quota(self):
        return self.__get_value('MediumProviderCpuQuota', DOCKER_SECTION)

    @property
    def medium_provider_memory(self):
        return self.__get_value('MediumProviderMemory', DOCKER_SECTION)

    @property
    def large_provider_cpu_quota(self):
        return self.__get_value('LargeProviderCpuQuota', DOCKER_SECTION)

    @property
    def large_provider_memory(self):
        return self.__get_value('LargeProviderMemory', DOCKER_SECTION)

    @property
    def consumer_cpu_quota(self):
        return self.__get_value('ConsumerCpuQuota', DOCKER_SECTION)

    @property
    def consumer_memory(self):
        return self.__get_value('ConsumerMemory', DOCKER_SECTION)

    @property
    def user_code_address(self):
        return self.__get_value('DefaultCodeAddress')
