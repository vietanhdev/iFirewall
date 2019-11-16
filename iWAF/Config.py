from threading import Lock


class Config:

    PUBLIC_PARAMS = ["rate_limit_interval",
        "rate_limit_warning_thresh",
        "rate_limit_block_thresh",
        "rate_limit_block_time",
        "rate_limit_ddos_thresh",
        "rate_limit_ddos_interval",
        "rate_limit_whitelist_expiration_time",
        "rate_limit_under_attack",
        "servers",
        "homepage"
    ]

    def __init__(self, default_config):
        self.config = default_config
        self.data_lock = Lock()

    def get(self):
        self.data_lock.acquire()
        config = self.config.copy()
        self.data_lock.release()
        return config

    def get_public_params(self):
        config = {}
        self.data_lock.acquire()
        for key in self.PUBLIC_PARAMS:
            config[key] = self.config[key]
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

    def update_params(self, params):
        return "Updated successfully!"
    