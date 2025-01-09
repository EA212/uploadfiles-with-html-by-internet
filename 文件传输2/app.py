from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
import os
import time
import psutil
import configparser 
import threading
import re

app = Flask(__name__, static_folder='static')

# 设置静态文件路径，假设favicon.ico放在static文件夹下
STATIC_FOLDER = './static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)
def get_upload_path():
    config = configparser.ConfigParser()
    config.read('config.ini')  # 读取根目录下的config.ini文件
    config.read('config.ini', encoding='utf-8')  # 这里指定编码为utf-8进行读取
    return config.get('saved_paths', 'upload_path')

# 文件上传接口
@app.route('/upload', methods=['POST'])
def upload_file():
    upload_path = get_upload_path()
    print(f"文件将上传至路径: {upload_path}")
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    if 'files[]' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files[]')
    success = False
    errors = {}

    for file in files:
        if file.filename == '':
            errors[file.filename] = 'File name is empty.'
            continue

        try:
            filename = file.filename
            file.save(os.path.join(upload_path, filename))
            success = True
        except Exception as e:
            errors[file.filename] = str(e)

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded, but some files encountered errors.'
        return jsonify(errors), 207
    elif success:
        return jsonify({"message": "Files successfully uploaded"}), 200
    else:
        return jsonify(errors), 400
    
@app.route('/api/get-upload-url', methods=['POST'])
def get_upload_url():
    # 构建上传URL，这里假设你已经有了一个'/upload'接口用于文件上传
    upload_url = url_for('upload_file', _external=True)  # 获取完整的外部URL
    return jsonify({"uploadUrl": upload_url}), 200

# 根路径，渲染HTML页面
@app.route('/')
def index():
    return render_template('index.html')

# 处理favicon.ico请求
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 已有的/status接口
# 创建一个后台线程来持续更新网络统计信息
class NetworkStatsThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.upload_rate = 0
        self.download_rate = 0
        self.last_time = time.time()
        self.last_upload_bytes = psutil.net_io_counters().bytes_sent
        self.last_download_bytes = psutil.net_io_counters().bytes_recv

    def run(self):
        while True:
            current_time = time.time()
            net_io_counters = psutil.net_io_counters()
            current_upload_bytes = net_io_counters.bytes_sent
            current_download_bytes = net_io_counters.bytes_recv

            elapsed_time = current_time - self.last_time
            if elapsed_time > 0:
                self.upload_rate = (current_upload_bytes - self.last_upload_bytes) / elapsed_time / 1024
                self.download_rate = (current_download_bytes - self.last_download_bytes) / elapsed_time / 1024

            self.last_time = current_time
            self.last_upload_bytes = current_upload_bytes
            self.last_download_bytes = current_download_bytes

            time.sleep(1)

# 初始化并启动后台线程
network_stats_thread = NetworkStatsThread()
network_stats_thread.start()

@app.route('/status')
def status():
    try:
        return jsonify({
            "connected_devices": ["Device1", "Device2"],  # 动态获取这部分信息
            "log_messages": ["Log message 1", "Log message 2"],  # 动态获取这部分信息
            "upload_rate": network_stats_thread.upload_rate,
            "download_rate": network_stats_thread.download_rate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
