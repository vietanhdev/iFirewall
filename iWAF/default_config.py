DEFAULT_CONFIG = {

    "homepage": "http://localhost:8080/",

    "redis_host": "redis",
    "redis_port": 6379,
    "redis_db": 0,

    "rate_limit_interval": 60,
    "rate_limit_warning_thresh": 20,
    "rate_limit_block_thresh": 30,
    "rate_limit_block_time": 300,
    "rate_limit_ddos_thresh": 5,
    "rate_limit_ddos_interval": 60,
    "rate_limit_ddos_blocking_time": 60,
    "rate_limit_whitelist_expiration_time": 10*60,
    "rate_limit_under_attack": False,

    "recaptcha_site_key": "6LcJ1sIUAAAAALGo16uZMmfKYR-cfxswil-NZTBB",
    "recaptcha_secret_key": "6LcJ1sIUAAAAACdmJ4Eyy1OInCiR4v2LS-zy3CXz",

    "servers": [
        {
            "id": 1,
            "address": "http://web_server_1:80/",
            "server_status_url": "http://web_server_1:80/server_status",
            "online": True
        },
        {
            "id": 2,
            "address": "http://web_server_2:80/",
            "server_status_url": "http://web_server_2:80/server_status",
            "online": True
        },
        {
            "id": 3,
            "address": "http://web_server_3:80/",
            "server_status_url": "http://web_server_3:80/server_status",
            "online": True
        },
        {
            "id": 4,
            "address": "http://web_server_4:80/",
            "server_status_url": "http://web_server_4:80/server_status",
            "online": True
        },
        {
            "id": 5,
            "address": "http://web_server_5:80/",
            "server_status_url": "http://web_server_5:80/server_status",
            "online": True
        },
    ]
}
