import os
import socket


class Workspace():

    def __init__(self, config, endpoint_name, task):
        self.local = LocalHost(config, task)
        self.remote = RemoteHost(config, endpoint_name, task)


class LocalHost():

    def __init__(self, config, task, expanduser=True):
        self.hostname = socket.gethostname()

        self.home = config.workspace_home
        self.home = os.path.expanduser(self.home)

        self.lock_file = '{}/{}'.format(self.home, '.lock')
        self.docker_file = '{}/{}'.format(self.home, 'dockerfile')

    def __repr__(self):
        s = ', '.join(['{}={}'.format(k, v) for k, v in self.__dict__.items()])
        return '{}({})'.format(self.__class__.__name__, s)


class RemoteHost():

    def __init__(self, config, endpoint_name, task):
        self.user = config.remote_host_user

        self.home = config.workspace_home
        self.team_home = '{}/{}'.format(self.home, task.team_id)
        self.task_home = '{}/{}/{}'.format(self.team_home, task.task_id, endpoint_name)

        self.lock_file = '{}/{}'.format(self.task_home,  '.lock')
        self.docker_file = '{}/{}'.format(self.task_home,  'dockerfile')


    def __repr__(self):
        s = ', '.join(['{}={}'.format(k, v) for k, v in self.__dict__.items()])
        return '{}({})'.format(self.__class__.__name__, s)
