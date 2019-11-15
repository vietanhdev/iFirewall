import logging
import time
from functools import wraps
from flask import request, jsonify, render_template
import redis
import requests

class RateLimiter():

    def __init__(self, config):
        
        self.config = config
        self.redis_db = redis.StrictRedis(host=self.config["redis"]["host"], port=self.config["redis"]["port"], db=self.config["redis"]["db"])
        self.logger = logging.getLogger(__name__)


    def rate_limit(self, shared_limit=True):
        def rate_limit_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):

                # Define redis keys
                t = int(time.time())
                closest_minute = t - (t % self.config["global_limit"]["interval"])
                if shared_limit:
                    rate_limit_key = "%s:%s:%s" % ("rate_limit", request.remote_addr, closest_minute)
                else:
                    rate_limit_key = "%s:%s:%s.%s:%s" % ("rate_limit", request.remote_addr,
                                            f.__module__, f.__name__, closest_minute)
                blacklist_key = "%s%s" % ("blacklisted", request.remote_addr)

                # Check for blocked user
                if self.redis_db.exists(blacklist_key):
                    if request.method == "POST":

                        # Check captcha
                        data = {
                            'secret': self.config["recaptcha"]["secret_key"],
                            'response': request.form.get('g-recaptcha-response'),
                            'remoteip': request.access_route[0]
                        }
                        r = requests.post(
                            "https://www.google.com/recaptcha/api/siteverify",
                            data=data
                        )
                        result = r.json()

                        if result['success']:
                            # Remove user from blacklist
                            self.redis_db.delete(blacklist_key)
                            self.redis_db.delete(rate_limit_key)

                            return render_template("redirect.html", homepage=self.config["homepage"])
                        else:

                            # Fail
                            return render_template('blocked.html', g_captcha_site_key=self.config["recaptcha"]["site_key"]), 429
                    else:
                        return render_template('blocked.html', g_captcha_site_key=self.config["recaptcha"]["site_key"], message="Wrong captcha. Try again!"), 429

                # If user is not blocked, check rate limit
                current = self.redis_db.get(rate_limit_key)

                # If user reach the blocking threshold, put user that user to blacklist
                if current and int(current) > self.config["global_limit"]["block_thresh"]:
                    self.redis_db.set(blacklist_key, self.config["global_limit"]["block_time"])
                    return render_template('blocked.html', g_captcha_site_key=self.config["recaptcha"]["site_key"]), 429

                # Check rate limit for a warning
                elif current and int(current) > self.config["global_limit"]["warning_thresh"]:

                    pipe = self.redis_db.pipeline()
                    pipe.incr(rate_limit_key, 1)
                    pipe.expire(rate_limit_key, self.config["global_limit"]["interval"] + 1)
                    pipe.execute()

                    retry_after = self.config["global_limit"]["interval"] - (t - closest_minute)
                    self.logger.info("Hitting rate limit: %s" % (rate_limit_key))
                    resp = jsonify({
                        'code': 429,
                        "message": "Too many requests. Limit %s in %s seconds" % (self.config["global_limit"]["warning_thresh"], self.config["global_limit"]["interval"])
                    })
                    return render_template('slow_down.html'), 429

                else:
                    pipe = self.redis_db.pipeline()
                    pipe.incr(rate_limit_key, 1)
                    pipe.expire(rate_limit_key, self.config["global_limit"]["interval"] + 1)
                    pipe.execute()

                    return f(*args, **kwargs)
            return wrapper
        return rate_limit_decorator
