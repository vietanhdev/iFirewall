
RATE_LIMITER_CONF = {
    "redis": {
        "host": "redis",
        "port": 6379,
        "db": 0
    },

    "global_limit": {
        "limit": 120,
        "interval": 60
    }
}

SERVERS = [
    {
        "address": "http://web_server_1:80/"
    },
    {
        "address": "http://web_server_2:80/"
    },
    {
        "address": "http://web_server_3:80/"
    },
    {
        "address": "http://web_server_4:80/"
    },
    {
        "address": "http://web_server_5:80/"
    },
]

