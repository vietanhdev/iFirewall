
RATE_LIMITER_CONF = {
    "redis": {
        "host": "redis",
        "port": 6379,
        "db": 0
    },

    "global_limit": {
        "limit": 1000,
        "interval": 100
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

