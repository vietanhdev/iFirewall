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

    # Pass original Referer for subsequent resource requests
    referer = request.headers.get('referer')
    # if referer:
        # proxy_ref = proxied_request_info(referer)
        # headers.update({ "referer" : "http://%s/%s" % (proxy_ref[0], proxy_ref[1])})

    # Fetch the URL, and stream it back
    LOG.debug("Sending %s %s with headers: %s and data %s", method, url, headers, data)
    return requests.request(method, url, params=request.args, stream=True, headers=headers, allow_redirects=False, data=data)

def proxied_request_info(proxy_url):
    """Returns information about the target (proxied) URL given a URL sent to
    the proxy itself. For example, if given:
        http://localhost:5000/p/google.com/search?q=foo
    then the result is:
        ("google.com", "search?q=foo")"""
    parts = urlparse(proxy_url)
    if not parts.path:
        return None
    elif not parts.path.startswith('/p/'):
        return None
    matches = re.match('^/p/([^/]+)/?(.*)', parts.path)
    proxied_host = matches.group(1)
    proxied_path = matches.group(2) or '/'
    proxied_tail = urlunparse(parts._replace(scheme="", netloc="", path=proxied_path))
    LOG.debug("Referred by proxy host, uri: %s, %s", proxied_host, proxied_tail)
    return [proxied_host, proxied_tail]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')