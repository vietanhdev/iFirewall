
RATE_LIMITER_CONF = {

    "homepage": "http://localhost:8080/",

    "redis": {
        "host": "redis",
        "port": 6379,
        "db": 0
    },

    "global_limit": {
        "interval": 1000,
        "warning_thresh": 10,
        "block_thresh": 20,
        "block_time": 120,
        "ddos_thresh": 120
    },

    "recaptcha": {
        "site_key": "6LcJ1sIUAAAAALGo16uZMmfKYR-cfxswil-NZTBB",
        "secret_key": "6LcJ1sIUAAAAACdmJ4Eyy1OInCiR4v2LS-zy3CXz"
    }
}

SERVERS = [
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

