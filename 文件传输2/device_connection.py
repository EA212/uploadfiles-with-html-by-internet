import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QGuiApplication
import qrcode
from io import BytesIO
import socket


class DeviceConnectionWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("连接设备设置")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        # 显示本地访问地址和服务器IP地址
        local_host_layout, local_host_copy_button = self.create_address_widget("本地访问: http://127.0.0.1:5000")
        layout.addLayout(local_host_layout)
        layout.addWidget(local_host_copy_button)

        host_name = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(host_name)
        except socket.error as e:
            local_ip = "无法获取IP地址"
        ip_layout, ip_copy_button = self.create_address_widget(f"服务器IP地址: {local_ip}")
        layout.addLayout(ip_layout)
        layout.addWidget(ip_copy_button)

        # 生成并显示二维码
        if local_ip != "无法获取IP地址":
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"http://{local_ip}:5000")
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            qr_label = QLabel(self)
            qr_label.setPixmap(pixmap)
            layout.addWidget(qr_label)

        close_button = QPushButton("关闭", self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def create_address_widget(self, text):
        address_layout = QHBoxLayout()
        address_label = QLabel(text)
        copy_button = QPushButton("复制")
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(text))
        address_layout.addWidget(address_label)
        address_layout.addWidget(copy_button)
        return address_layout, copy_button

    def copy_to_clipboard(self, text):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceConnectionWindow()
    window.show()
    sys.exit(app.exec_())
