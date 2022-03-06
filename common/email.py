class EmailInfo:
    def __init__(self):
        self.subject = ''
        self.content = ''
        self.attaches = []
        self.receivers = []


class AttachInfo:
    def __init__(self):
        self.file_name = ''
        self.file_location = ''
