import logging
import time
from functools import wraps
from flask import request, jsonify, render_template
import redis
import requests

class RateLimiter():

    def __init__(self, config):
        
        self.config = config
        self.redis_db = redis.StrictRedis(host=self.config.get_param("redis_host"), port=self.config.get_param("redis_port"), db=self.config.get_param("redis_db"))
        self.logger = logging.getLogger(__name__)

    def is_under_attack(self):
        ddos_flag_key = "ddos_detected"
        return self.redis_db.exists(ddos_flag_key) or self.config.get_param("rate_limit_under_attack")

    def rate_limit(self, shared_limit=True):
        def rate_limit_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):

                # Define keys
                t = int(time.time())
                closest_minute_rate_limit = t - (t % self.config.get_param("rate_limit_interval"))
                rate_limit_key = "%s:%s:%s" % ("rate_limit", request.remote_addr, closest_minute_rate_limit)

                ddos_flag_key = "ddos_detected"
                closest_minute_ddos_detect = t - (t % self.config.get_param("rate_limit_ddos_interval"))
                ddos_detect_key = "%s:%s" % ("ddos_detect", closest_minute_ddos_detect)

                # Increase traffic to monitor DDOS
                pipe = self.redis_db.pipeline()
                pipe.incr(ddos_detect_key, 1)
                pipe.expire(ddos_detect_key, self.config.get_param("rate_limit_ddos_interval") + 1)
                pipe.execute()

                # DDOS detection
                current_rate_global = self.redis_db.get(ddos_detect_key)
                if current_rate_global and int(current_rate_global) > self.config.get_param("rate_limit_ddos_thresh"):
                    self.redis_db.set(ddos_flag_key, 1, ex=self.config.get_param("rate_limit_ddos_blocking_time"))

                blacklist_key = "%s%s" % ("blacklisted", request.remote_addr)
                whilelist_key = "%s%s" % ("whitelisted", request.remote_addr)


                under_ddos_attack = self.redis_db.exists(ddos_flag_key) or self.config.get_param("rate_limit_under_attack")

                # Block all user not in whitelist when under attack
                # Or Block user if exceed rate limit
                blocking_mode = None
                if under_ddos_attack:
                    if not self.redis_db.exists(whilelist_key):
                        blocking_mode = "DDOS_PROTECT"
                if self.redis_db.exists(blacklist_key):
                    blocking_mode = "RATE_LIMIT_PROTECT"


                # User is blocked
                if blocking_mode is not None:
                    if request.method == "POST":

                        # Check captcha
                        data = {
                            'secret': self.config.get_param("recaptcha_secret_key"),
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
                            self.redis_db.set(rate_limit_key, 0)

                            # Add user to whitelist
                            self.redis_db.set(whilelist_key, 1, ex=self.config.get_param("rate_limit_whitelist_expiration_time"))

                            return render_template("redirect.html", homepage=self.config.get_param("homepage"))
                        else:

                            # Fail
                            return render_template('blocked.html', g_captcha_site_key=self.config.get_param("recaptcha_site_key"), message="Wrong captcha. Try again!", blocking_mode=blocking_mode), 429
                    else:
                        return render_template('blocked.html', g_captcha_site_key=self.config.get_param("recaptcha_site_key"), blocking_mode=blocking_mode), 429

                # If user is still not blocked, check rate limit
                current_rate_user = self.redis_db.get(rate_limit_key)

                # If user reach the blocking threshold, put user that user to blacklist
                if current_rate_user and int(current_rate_user) > self.config.get_param("rate_limit_block_thresh"):
                    self.redis_db.set(blacklist_key, 1, ex=self.config.get_param("rate_limit_block_time"))
                    return render_template('blocked.html', g_captcha_site_key=self.config.get_param("recaptcha_site_key"), blocking_mode="RATE_LIMIT_PROTECT"), 429

                # Check rate limit for a warning
                if current_rate_user and int(current_rate_user) > self.config.get_param("rate_limit_warning_thresh"):

                    pipe = self.redis_db.pipeline()
                    pipe.incr(rate_limit_key, 1)
                    pipe.expire(rate_limit_key, self.config.get_param("rate_limit_interval") + 1)
                    pipe.execute()

                    return render_template('slow_down.html'), 429

                # Increase traffic count
                pipe = self.redis_db.pipeline()
                pipe.incr(rate_limit_key, 1)
                pipe.expire(rate_limit_key, self.config.get_param("rate_limit_interval") + 1)
                pipe.execute()

                return f(*args, **kwargs)
            return wrapper
        return rate_limit_decorator
