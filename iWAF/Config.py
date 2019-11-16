from threading import Lock
import redis

class Config:

    PUBLIC_PARAMS = ["rate_limit_interval",
        "rate_limit_warning_thresh",
        "rate_limit_block_thresh",
        "rate_limit_block_time",
        "rate_limit_ddos_thresh",
        "rate_limit_ddos_interval",
        "rate_limit_whitelist_expiration_time",
        "rate_limit_under_attack",
        "rate_limit_ddos_blocking_time",
        "servers",
        "homepage"
    ]

    def __init__(self, default_config):
        self.config = default_config
        self.data_lock = Lock()
        self.redis_db = redis.StrictRedis(host=self.config["redis_host"], port=self.config["redis_port"], db=self.config["redis_db"])

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

        for key in params:
            
            # Int params
            if key in ["rate_limit_interval",
                "rate_limit_warning_thresh",
                "rate_limit_block_thresh",
                "rate_limit_block_time",
                "rate_limit_ddos_thresh",
                "rate_limit_ddos_interval",
                "rate_limit_ddos_blocking_time",
                "rate_limit_whitelist_expiration_time"]:
            
                try:
                    value = int(params[key])
                    if value <= 0:
                        return "Wrong value for %s!" % key
                    self.set_param(key, value)
                except:
                    return "Wrong value for %s!" % key

            elif key == "rate_limit_under_attack":
                try:
                    value = bool(params[key])
                    self.set_param(key, value)
                except:
                    return "Wrong value for %s!" % key

            elif key == "servers":
                try:
                    servers = []
                    for i in range(len(params["servers"])):
                        servers.append({
                            "id": i+1,
                            "address": params["servers"][i],
                            "server_status_url": params["servers"][i] + "server_status",
                            "online": True
                        })
                    self.set_param(key, servers)
                except:
                    return "Wrong value for %s!" % key

            elif key == "reset_protection_db": # Clear protection database
                for key in self.redis_db.scan_iter("*"):
                    self.redis_db.delete(key)
                return "Cleared database successfully!"



        return "Updated successfully!"
    