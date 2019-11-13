from config import WEB_SERVER_CONF
from flask import Flask, redirect, send_from_directory, jsonify
import time

task_queue = [] # Save the expiration time for tasks

app = Flask(__name__)

# Routes
@app.route('/')
def root():
  return redirect("/index.html")

@app.route('/server_status')
def server_status():
  global task_queue

  # Remove finished tasks
  task_queue = [t for t in task_queue if t > time.time()]

  if len(task_queue) < WEB_SERVER_CONF["server_queue_size"]:
    return jsonify({
      "online": True,
      "processing_tasks": len(task_queue),
      "server_queue_size": WEB_SERVER_CONF["server_queue_size"]
    })
  else:
    return "503 Service Unavailable", 503

@app.route('/<path:path>')
def serve_file(path):

  global task_queue

  # Remove finished tasks
  task_queue = [t for t in task_queue if t > time.time()]

  if len(task_queue) < WEB_SERVER_CONF["server_queue_size"]:
    task_queue.append(time.time() + WEB_SERVER_CONF["processing_time"])
  else:
    return "503 Service Unavailable", 503

  # send_static_file will guess the correct MIME type
  return send_from_directory("public/", path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)