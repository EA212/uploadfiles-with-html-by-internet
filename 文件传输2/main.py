import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox, QComboBox, QCheckBox, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer, QTime, Qt, QSettings, QDir, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QDesktopServices, QPixmap
import asyncio
import aiohttp
import subprocess
import requests
import logging
from threading import Thread
import json
import configparser
import device_connection
import app

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义配置文件路径
CONFIG_FILE = 'config.ini'

class ServerManagerApp(QMainWindow):
    # 定义信号，用于在异步获取数据后，通知主线程更新UI
    data_updated_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("后端服务器管理")
        self.setGeometry(100, 100, 800, 600)

        self.server_running = False
        self.start_time = None


        
        self.initUI()
        
        # 连接信号与槽，当有新数据时更新UI
        self.data_updated_signal.connect(self.update_ui)

    def toggle_server(self):
        if not self.server_running:
            # 启动服务器逻辑
            try:
                server_manager.start_server()
                self.server_running = True
                self.start_time = QTime.currentTime()
                self.toggle_button.setText('停止服务器')
                self.toggle_button.setStyleSheet("background-color: red")
                self.status_label.setText("服务器状态: 正在运行")
            except Exception as e:
                print(f"Error starting server: {e}")
        else:
            # 停止服务器逻辑
            try:
                server_manager.stop_server()
                self.server_running = False
                self.toggle_button.setText('启动服务器')
                self.toggle_button.setStyleSheet("background-color: green")
                self.status_label.setText("服务器状态: 已停止")
            except Exception as e:
                print(f"Error stopping server: {e}")

    async def async_get_status(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:5000/status") as response:
                    if response.status == 200:
                        status_info = await response.json()
                        return status_info
                    else:
                        logger.error(f"Failed to get data from server. Status code: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error occurred: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None

    async def async_update_status(self):
        if self.server_running:
            elapsed_time = QTime(0, 0).addSecs(self.start_time.secsTo(QTime.currentTime()))
            self.duration_label.setText(f"服务时长: {elapsed_time.toString('hh:mm:ss')}")
            status_info = await self.async_get_status()
            if status_info:
                # 发送信号，通知主线程更新UI
                self.data_updated_signal.emit(status_info)

    def update_ui(self, status_info):
        """
        在主线程中更新UI界面的相关信息
        """
        self.up_rate_label.setText(f"上行速率: {status_info.get('upload_rate', 0)} KB/s")
        self.down_rate_label.setText(f"下行速率: {status_info.get('download_rate', 0)} KB/s")
        self.device_info_label.setText(f"设备信息: {', '.join(status_info.get('connected_devices', []))}")
        self.connection_status_label.setText(f"连接状态: {'已连接' if self.server_running else '断开'}")
        for message in status_info.get('log_messages', []):
            self.update_log(message)

    def update_log(self, message):
        print(message)  # 将日志信息打印到控制台

    def initUI(self):
        layout = QVBoxLayout()

        # 设置布局
        top_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 左侧：服务器控制和状态
        self.status_label = QLabel("服务器状态: 已停止", self)
        left_layout.addWidget(self.status_label)

        self.toggle_button = QPushButton('启动服务器', self)
        self.toggle_button.setStyleSheet("background-color: green")
        self.toggle_button.clicked.connect(self.toggle_server)
        left_layout.addWidget(self.toggle_button)

        self.duration_label = QLabel("服务时长: 00:00:00", self)
        left_layout.addWidget(self.duration_label)

        self.up_rate_label = QLabel("上行速率: 未知", self)
        left_layout.addWidget(self.up_rate_label)

        self.down_rate_label = QLabel("下行速率: 未知", self)
        left_layout.addWidget(self.down_rate_label)

        self.device_info_label = QLabel("设备信息: 未知", self)
        left_layout.addWidget(self.device_info_label)

        self.connection_status_label = QLabel("连接状态: 断开", self)
        left_layout.addWidget(self.connection_status_label)

        # 右侧：文件保存路径设置
        self.path_combo = QComboBox(self)
        self.load_saved_paths()
        right_layout.addWidget(QLabel("选择保存路径:"))
        right_layout.addWidget(self.path_combo)

        self.browse_button = QPushButton("浏览...", self)
        self.browse_button.clicked.connect(self.select_path)
        right_layout.addWidget(self.browse_button)

        self.view_folder_button = QPushButton("查看文件夹", self)
        self.view_folder_button.clicked.connect(self.view_selected_folder)
        right_layout.addWidget(self.view_folder_button)

        self.timestamp_checkbox = QCheckBox("保存在时间戳文件夹中", self)
        right_layout.addWidget(self.timestamp_checkbox)

        self.device_connection_button = QPushButton("文件上传服务二维码", self)
        self.device_connection_button.clicked.connect(self.open_device_connection_window)
        right_layout.addWidget(self.device_connection_button)

        # 文件接收进度表格
        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(["#", "文件名", "文件大小", "文件保存位置", "接收速率", "剩余大小", "进度"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setRowCount(0)
        layout.addWidget(self.file_table)

        # 组合左右布局
        top_layout.addLayout(left_layout)
        top_layout.addLayout(right_layout)
        layout.addLayout(top_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 定时器更新服务时长和其他信息，使用异步方式更新状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: asyncio.run(self.async_update_status()))
        self.timer.start(3000)  # 这里调整为每3秒更新一次，可根据实际情况修改
        
    def select_path(self):
        # 打开文件夹选择对话框
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if directory:
            self.update_and_save_paths(directory)

    def update_and_save_paths(self, new_path):
        config = configparser.ConfigParser()
        
        # 读取现有的配置文件
        config.read(CONFIG_FILE, encoding='utf-8')

        # 确保 saved_paths 部分存在
        if not config.has_section('saved_paths'):
            config.add_section('saved_paths')

        # 获取已保存的路径列表
        paths = config.get('saved_paths', 'paths', fallback='').splitlines()

        # 移除空字符串并过滤掉重复路径
        paths = [p for p in paths if p]
        if new_path not in paths:
            if len(paths) >= 5:  # 最多保存 5 条路径
                paths.pop(0)
            paths.append(new_path)

            # 更新组合框内容
            self.path_combo.clear()
            self.path_combo.addItems(paths)
            self.path_combo.setCurrentText(new_path)

            # 将更新后的路径列表保存回配置文件
            config.set('saved_paths', 'paths', '\n'.join(paths))

            # 将最新的路径设置为 upload_path
            config.set('saved_paths', 'upload_path', new_path)

            # 写入配置文件
            with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                config.write(configfile)

    def load_saved_paths(self):
        config = configparser.ConfigParser()
        
        # 读取现有的配置文件
        config.read(CONFIG_FILE, encoding='utf-8')

        # 确保 saved_paths 部分存在
        if not config.has_section('saved_paths'):
            config.add_section('saved_paths')

        # 获取已保存的路径列表
        paths = config.get('saved_paths', 'paths', fallback='').splitlines()

        # 移除空字符串
        paths = [p for p in paths if p]

        # 更新组合框内容
        self.path_combo.clear()
        self.path_combo.addItems(paths)

        # 获取 upload_path，如果不存在则设置为最新的路径
        upload_path = config.get('saved_paths', 'upload_path', fallback='')
        if not upload_path and paths:  # 如果 upload_path 不存在且路径列表不为空
            upload_path = paths[-1]  # 将最新的路径设置为 upload_path
            config.set('saved_paths', 'upload_path', upload_path)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                config.write(configfile)

        # 设置组合框的当前选中项为 upload_path
        if upload_path:
            self.path_combo.setCurrentText(upload_path)

        # 绑定组合框的选择事件
        self.path_combo.currentTextChanged.connect(self.save_selected_path_as_upload_path)

    def save_selected_path_as_upload_path(self, selected_path):
        config = configparser.ConfigParser()
        
        # 读取现有的配置文件
        config.read(CONFIG_FILE, encoding='utf-8')

        # 确保 saved_paths 部分存在
        if not config.has_section('saved_paths'):
            config.add_section('saved_paths')

        # 将选中的路径保存为 upload_path
        config.set('saved_paths', 'upload_path', selected_path)

        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def view_selected_folder(self):
        selected_path = self.path_combo.currentText()
        if selected_path:
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(selected_path))
            except Exception as e:
                print(f"Error opening folder: {e}")



                
    def open_device_connection_window(self):
        try:
            subprocess.Popen(['pythonw', 'device_connection.py'])
        except Exception as e:
            print(f"Error opening device_connection_window: {e}")


class ServerManager:
    def __init__(self):
        self.process = None

    def start_server(self):
        if not self.process:
            self.process = subprocess.Popen(['python', 'app.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            logger.info("Server started")

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process = None
            logger.warning("Server stopped")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerManagerApp()
    window.show()

    # 创建一个全局的ServerManager实例
    server_manager = ServerManager()

    sys.exit(app.exec_())
