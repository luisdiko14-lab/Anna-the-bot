from flask import Flask, render_template, jsonify
import os
import psutil
import platform

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    return jsonify({
        "status": "Online",
        "cpu": f"{psutil.cpu_percent()}%",
        "ram": f"{psutil.virtual_memory().percent}%",
        "platform": platform.system(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
