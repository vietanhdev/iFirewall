
from flask import Flask, redirect, send_from_directory

app = Flask(__name__)

# Routes
@app.route('/')
def root():
  return redirect("/index.html")

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return send_from_directory("public/", path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)