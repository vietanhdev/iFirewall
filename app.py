from config import IFIREWALL_CONF
from flask import Flask, render_template, jsonify
app = Flask(__name__)

from iFirewall.iFirewall import iFirewall

# Initialize Firewall
ifw = iFirewall(IFIREWALL_CONF)

@app.route('/')
@ifw.rate_limit(limit=10, interval=60)
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')