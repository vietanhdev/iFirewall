from threading import Lock


class Config:

    def __init__(self, default_config):
        self.config = default_config
        self.data_lock = Lock()

    def get(self):
        self.data_lock.acquire()
        config = self.config.copy()
        self.data_lock.release()
        return config
    
    def get_param(self, key):
        self.data_lock.acquire()
        value = self.config[key]
        self.data_lock.release()
        return value

    def set_param(self, key, value):
        self.data_lock.acquire()
        self.config[key] = value
        self.data_lock.release()
    