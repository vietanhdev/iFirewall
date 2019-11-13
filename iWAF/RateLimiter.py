import logging
import time
from functools import wraps

from flask import request, jsonify, render_template
import redis

class RateLimiter():

    def __init__(self, config):
        
        self.config = config
        self.redis_db = redis.StrictRedis(host=self.config["redis"]["host"], port=self.config["redis"]["port"], db=self.config["redis"]["db"])
        self.logger = logging.getLogger(__name__)


    def rate_limit(self, limit=10, interval=60, shared_limit=True, key_prefix="rl"):
        def rate_limit_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                t = int(time.time())
                closest_minute = t - (t % interval)
                if shared_limit:
                    key = "%s:%s:%s" % (key_prefix, request.remote_addr, closest_minute)
                else:
                    key = "%s:%s:%s.%s:%s" % (key_prefix, request.remote_addr,
                                            f.__module__, f.__name__, closest_minute)
                current = self.redis_db.get(key)

                if current and int(current) > limit:
                    retry_after = interval - (t - closest_minute)
                    self.logger.info("Hitting rate limit: %s" % (key))
                    resp = jsonify({
                        'code': 429,
                        "message": "Too many requests. Limit %s in %s seconds" % (limit, interval)
                    })
                    return render_template('blocked.html'), 429
                else:
                    pipe = self.redis_db.pipeline()
                    pipe.incr(key, 1)
                    pipe.expire(key, interval + 1)
                    pipe.execute()

                    return f(*args, **kwargs)
            return wrapper
        return rate_limit_decorator
