
RATE_LIMITER_CONF = {
    "redis": {
        "host": "redis",
        "port": 6379,
        "db": 0
    },

    "global_limit": {
        "interval": 1000,
        "limit": 10,
        "block_threh": 20,
        "block_time": 120
    },

    "recaptcha": {
        "site_key": "6LcJ1sIUAAAAALGo16uZMmfKYR-cfxswil-NZTBB",
        "secret_key": "6LcJ1sIUAAAAACdmJ4Eyy1OInCiR4v2LS-zy3CXz"
    }
}

SERVERS = [
    {
        "address": "http://web_server_1:80/",
        "server_status_url": "http://web_server_1:80/server_status",
        "online": True
    },
    {
        "address": "http://web_server_2:80/",
        "server_status_url": "http://web_server_2:80/server_status",
        "online": True
    },
    {
        "address": "http://web_server_3:80/",
        "server_status_url": "http://web_server_3:80/server_status",
        "online": True
    },
    {
        "address": "http://web_server_4:80/",
        "server_status_url": "http://web_server_4:80/server_status",
        "online": True
    },
    {
        "address": "http://web_server_5:80/",
        "server_status_url": "http://web_server_5:80/server_status",
        "online": True
    },
]

