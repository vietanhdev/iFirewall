from default_config import DEFAULT_CONFIG
from Config import Config
from flask import Flask, render_template, jsonify, request, redirect, Response, request, abort
import json
import re
from urllib.parse import urlparse, urlunparse
import requests
import logging
import random
from RateLimiter import RateLimiter

app = Flask(__name__)

config = Config(DEFAULT_CONFIG) # Global configuration object

# Initialize Firewall
limiter = RateLimiter(config)

LOG = logging.getLogger("app.py")

# Monitor servers
@app.route('/iwaf_admin', methods=["GET"])
def iwaf_admin():
    return render_template('server_status.html')

# Get configs
@app.route('/iwaf_admin', methods=["POST"])
def iwaf_get_params():
    global config
    return jsonify(config.get_public_params())

# Update configs
@app.route('/iwaf_admin', methods=["PUT"])
def iwaf_update_params():
    params = request.get_json(force=True)
    return config.update_params(params)

# Monitor servers
@app.route('/get_server_status')
def get_server_status():

    global config

    data = []
    for server in config.get()["servers"]:

        try:
            server_status_resp = requests.get(server["server_status_url"])

            if server_status_resp.status_code != 200:
                server_status = {"online": False}
            else:
                server_status = server_status_resp.json()
        except:
            server_status = {"online": False}
            server["online"] = False

        server_status["address"] = server["address"]
        data.append(server_status)

    return jsonify({"data": data})

@app.route('/', methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/<path:url>', methods=["GET", "POST", "PUT", "DELETE"])
@limiter.rate_limit()
def proxy(url=""):

    LOG.debug("%s %s with headers: %s", request.method, url, request.headers)
    r = make_request(url, request.method, dict(request.headers), request.form)
    LOG.debug("Got %s response from %s", r.status_code, url)
    headers = dict(r.raw.headers)

    # Add headers to prevent XSS attack
    # x-xss-protection:1; mode=block
    headers.update({ "x-xss-protection" : "1; mode=block" }) # Force enable XSS Protection of browser
    headers.update({ "X-Frame-Options" : "SAMEORIGIN" }) # Prevent render iframe

    # Add IP address info 
    # https://support.cloudflare.com/hc/en-us/articles/200170986
    found_x_forwarded_for_header = False
    for header in headers:
        if header.lower() == "x-forwarded-for":
            headers[header] += ",{}".format(request.remote_addr)
            found_x_forwarded_for_header = True

    if not found_x_forwarded_for_header:
        headers[header] = str(request.remote_addr)

    def generate():
        for chunk in r.raw.stream(decode_content=False):
            yield chunk
    out = Response(generate(), headers=headers)
    out.status_code = r.status_code
    return out

def make_request(url, method, headers={}, data=None, try_again=True, bad_server_ids=[]):
    """
    Params:
        - bad_server_ids: server ids. Try to avoid these servers
    """

    global config
    online_servers = [s for s in config.get()["servers"] if s["online"] and s["id"] not in bad_server_ids]
    selected_server = random.randint(0, len(online_servers)-1)
    extended_url = online_servers[selected_server]["address"] + url

    # Fetch the URL, and stream it back
    LOG.debug("Sending %s %s with headers: %s and data %s", method, extended_url, headers, data)

    resp = None
    try:
        resp = requests.request(method, extended_url, params=request.args, stream=True, headers=headers, allow_redirects=False, data=data)
    except:
        if try_again:
            resp = make_request(url, method, headers={}, data=None, try_again=False, bad_server_ids=[selected_server])

    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
