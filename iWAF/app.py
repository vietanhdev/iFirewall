from config import RATE_LIMITER_CONF
from flask import Flask, render_template, jsonify, request, redirect, Response, request, abort
import json
import re
from urllib.parse import urlparse, urlunparse
import requests
import logging

app = Flask(__name__)

from RateLimiter import RateLimiter

# Initialize Firewall
limiter = RateLimiter(RATE_LIMITER_CONF)

ORIGIN_SERVER = "http://web_server_1:80/"

CHUNK_SIZE = 1024
LOG = logging.getLogger("app.py")


@app.route('/', methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/<path:url>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy(url=""):

    url = ORIGIN_SERVER + url

    LOG.debug("%s %s with headers: %s", request.method, url, request.headers)
    r = make_request(url, request.method, dict(request.headers), request.form)
    LOG.debug("Got %s response from %s",r.status_code, url)
    headers = dict(r.raw.headers)
    def generate():
        for chunk in r.raw.stream(decode_content=False):
            yield chunk
    out = Response(generate(), headers=headers)
    out.status_code = r.status_code
    return out

def make_request(url, method, headers={}, data=None):
    url = '%s' % url

    # Fetch the URL, and stream it back
    LOG.debug("Sending %s %s with headers: %s and data %s", method, url, headers, data)
    return requests.request(method, url, params=request.args, stream=True, headers=headers, allow_redirects=False, data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')