class Task():

    def __init__(self, dict):
        self.team_id = dict['teamId']
        self.task_id = dict['taskid']
        self.image_path = dict['imagepath']

    def __repr__(self):
        data = []
        for k, v in self.__dict__.items():
            data.append('{}={}'.format(k, v))
        return '{}({})'.format(self.__class__.__name__, ', '.join(data))
