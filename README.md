![image](https://github.com/user-attachments/assets/934fa337-49e8-4c3c-b82d-23fd6de1ae3e)
![image](https://github.com/user-attachments/assets/056b0250-4e15-444b-930e-34a08147d302)
![image](https://github.com/user-attachments/assets/5d916790-288e-464f-972b-b2ea5587dbe2)
![image](https://github.com/user-attachments/assets/5d5d9bc1-d436-4336-8934-7d13daa2004a)
### 局域网文件传输助手网页版介绍

#### 一、整体架构与运行逻辑

**1. 基于 PyQt5 构建 GUI 界面**

局域网文件传输助手网页版的客户端界面是使用 PyQt5 框架构建的。通过定义 `ServerManagerApp` 类继承自 `QMainWindow`，在 `__init__` 方法中设置了窗口的基础属性（如标题和大小），并调用 `initUI` 方法来组织界面布局，创建了一个功能分区明确的主窗口。

- **布局设计**：利用 `QVBoxLayout` 和 `QHBoxLayout` 的组合，实现了界面的垂直和水平布局划分。左侧放置了服务器控制和状态相关的组件（如按钮、标签等），右侧用于文件保存路径设置及展示文件接收进度的表格区域。这种布局使得用户可以直观地操作和监控服务器的状态。

**2. 服务器管理功能实现**

为了有效管理服务器进程，定义了 `ServerManager` 类，负责服务器的启动和停止操作。具体来说：

- **启动服务器**：`start_server` 方法使用 `subprocess.Popen` 来运行 `app.py` 启动 Flask 服务器。
- **停止服务器**：`stop_server` 方法通过调用 `process.terminate` 终止服务器进程。
- **状态联动**：`toggle_server` 方法根据服务器当前状态（通过 `server_running` 变量判断）来决定启动或停止服务器，并更新界面上的相应元素（如按钮文本、样式及状态标签），确保服务器状态与界面显示同步。

**3. 异步获取和更新服务器状态机制**

为了实现实时更新服务器状态，采用了异步编程技术：

- **异步请求**：使用 `aiohttp` 库发送异步 GET 请求到 `/status` 接口获取服务器状态信息。
- **定时器**：通过 `QTimer` 定时器每 3 秒触发一次 `async_update_status` 方法，该方法会先检查服务器是否正在运行，若是在运行则计算运行时长并更新对应界面标签，然后调用 `async_get_status` 获取最新状态信息。
- **信号与槽**：当获取到有效的状态信息后，通过自定义的 `data_updated_signal` 信号发射出去，通知主线程执行 `update_ui` 方法更新界面显示内容。

**4. 文件保存路径管理逻辑**

为了方便管理和持久化存储文件保存路径，使用了 `configparser` 模块读写配置文件（`config.ini`）：

- **加载路径**：`load_saved_paths` 方法读取已保存的路径列表，更新下拉框内容，并设置好上传路径。
- **选择路径**：下拉框的选择事件绑定到 `save_selected_path_as_upload_path` 方法，确保用户选择路径后能及时更新配置文件中的上传路径。
- **添加新路径**：`select_path` 方法响应“浏览...”按钮点击事件，允许用户选择新的文件夹路径，并通过 `update_and_save_paths` 方法处理路径列表，限制最多保存 5 条路径且去重，更新下拉框内容、设置当前选中路径并将更新后的路径列表写回配置文件。
- **查看文件夹**：`view_selected_folder` 方法响应“查看文件夹”按钮点击事件，尝试打开当前选中的文件夹。

**5. 设备连接辅助功能**

为了便于设备连接，提供了 `open_device_connection_window` 方法：

- **二维码生成**：该方法尝试运行 `device_connection.py` 打开一个用于设备连接的窗口，展示本地访问地址和服务器 IP 地址，并生成对应的二维码，帮助局域网内的其他设备快速连接到服务器进行文件传输等操作。

#### 二、代码中的关键技术点与细节

**1. 信号与槽机制**

PyQt5 的信号与槽机制用于解耦异步操作与 UI 更新，确保程序响应性能和用户体验。例如，在获取服务器状态后通过 `data_updated_signal` 信号通知主线程更新界面显示。

**2. 异步编程与网络请求**

借助 `aiohttp` 库进行异步网络请求，避免传统同步请求导致的阻塞问题，特别是在需要频繁获取服务器状态的情况下，使整个程序运行更加流畅。

**3. 配置文件读写与路径管理**

通过 `configparser` 库读写 `config.ini` 配置文件，合理管理文件保存路径相关信息，保证用户选择的路径能被有效管理和使用，同时考虑了路径列表的长度限制、去重等细节。

**4. 定时器的运用**

使用 `QTimer` 定时器定时触发状态更新方法，让用户实时看到服务器运行过程中的动态信息变化，无需手动刷新操作。

#### 三、功能

**1. 文件上传功能**

用户可以在网页端向服务器发起文件上传请求（通过 `/upload` 接口），支持一次上传多个文件。服务器会根据配置文件中设定的上传路径保存文件，并返回上传结果提示信息。

**2. 服务器状态查看功能**

客户端能够定时以异步方式获取服务器的实时状态信息（包括上行速率、下行速率、已连接的设备信息以及服务器的运行状态），并在图形界面上更新展示，方便用户了解服务器的工作情况。

**3. 设备连接辅助功能**

提供设备连接窗口，显示本地访问地址和服务器 IP 地址，配备“复制”按钮和二维码，帮助局域网内的其他设备连接到服务器进行文件传输等操作。

**4. 文件保存路径管理功能**

客户端提供了对文件保存路径的管理功能，包括从配置文件中读取路径、新增保存路径、查看文件夹内容以及将选中的路径设置为特定的上传路径等功能。

#### 四、组成部分

**1. 服务器端（基于 Flask 框架）**

- **路由与接口处理部分**：包含 `/upload` 处理文件上传逻辑、`/api/get-upload-url` 提供上传 URL、`/status` 反馈服务器状态等接口。
- **后台线程部分**：通过 `NetworkStatsThread` 类创建的后台线程持续获取和更新网络统计信息（如上传和下载速率），为服务器状态数据提供实时的网络相关指标。
- **配置文件读取部分**：使用 `configparser` 模块读取 `config.ini` 配置文件，从中获取如文件上传路径等相关配置信息。

**2. 客户端（基于 PyQt5 框架）**

- **主窗口部分（ServerManagerApp 类）**：集成服务器控制按钮、状态显示标签、文件保存路径管理组件及设备连接窗口按钮等，通过信号与槽机制及定时器实现与服务器的交互和界面更新。
- **设备连接窗口部分（DeviceConnectionWindow 类）**：以对话框形式呈现，包含显示本地访问地址、IP 地址、二维码等功能组件，辅助局域网内设备连接到服务器进行文件传输等操作。

总之，局域网文件传输助手网页版是一个集成了 Web 应用与图形界面客户端的工具，旨在简化局域网内的文件传输过程，提供直观的操作体验，并确保文件传输的安全性和效率。
### Introduction to the Local Network File Transfer Assistant Web Edition

#### 1. Overall Architecture and Operation Logic

**1.1 GUI Interface Built on PyQt5**

The client interface of the Local Network File Transfer Assistant Web Edition is constructed using the PyQt5 framework. By defining the `ServerManagerApp` class that inherits from `QMainWindow`, we set up basic window properties (such as title and size) in the `__init__` method and call the `initUI` method to organize the layout, creating a main window with clearly defined functional areas.

- **Layout Design**: Utilizing `QVBoxLayout` and `QHBoxLayout` for vertical and horizontal layouts, respectively, we achieve a clear division of interface components. The left side contains server control and status-related elements (like buttons and labels), while the right side manages file save path settings and displays file reception progress in a table area.

**1.2 Server Management Function Implementation**

To efficiently manage server processes, the `ServerManager` class is defined to handle server startup and shutdown operations:

- **Start Server**: The `start_server` method uses `subprocess.Popen` to run `app.py` and start the Flask server.
- **Stop Server**: The `stop_server` method calls `process.terminate` to stop the server process.
- **Status Synchronization**: The `toggle_server` method checks the current server state (via the `server_running` variable) to decide whether to start or stop the server and updates the corresponding UI elements (such as button text, style, and status labels) to ensure synchronization between server status and UI display.

**1.3 Asynchronous Retrieval and Update of Server Status**

To achieve real-time server status updates, asynchronous programming techniques are employed:

- **Asynchronous Requests**: Using the `aiohttp` library to send asynchronous GET requests to the `/status` endpoint to retrieve server status information.
- **Timer**: A `QTimer` timer triggers the `async_update_status` method every 3 seconds. This method first checks if the server is running; if so, it calculates the runtime and updates the corresponding interface label before calling `async_get_status` to fetch the latest status information.
- **Signals and Slots**: When valid status information is obtained, the custom `data_updated_signal` signal is emitted to notify the main thread to execute the `update_ui` method and update the interface display.

**1.4 File Save Path Management Logic**

For easy management and persistent storage of file save paths, the `configparser` module reads and writes to a configuration file (`config.ini`):

- **Load Paths**: The `load_saved_paths` method reads saved path lists from the configuration file, updates the dropdown box content, and sets the upload path.
- **Select Path**: The dropdown box selection event is bound to the `save_selected_path_as_upload_path` method, ensuring timely updates to the upload path in the configuration file when users select a path.
- **Add New Path**: The `select_path` method responds to the "Browse..." button click, allowing users to choose new folder paths. The `update_and_save_paths` method handles the path list, limiting it to 5 unique entries, updates the dropdown box content, sets the current selected path, and writes the updated path list back to the configuration file.
- **View Folder**: The `view_selected_folder` method responds to the "View Folder" button click, attempting to open the currently selected folder.

**1.5 Device Connection Assistance Function**

To facilitate device connections, the `open_device_connection_window` method is provided:

- **QR Code Generation**: This method attempts to run `device_connection.py` to open a device connection window, displaying local access addresses and server IP addresses along with QR codes to help other devices within the local network quickly connect to the server for file transfer operations.

#### 2. Key Technical Points and Details in the Code

**2.1 Signals and Slots Mechanism**

PyQt5's signals and slots mechanism decouples asynchronous operations from UI updates, ensuring program responsiveness and user experience. For example, after retrieving server status, the `data_updated_signal` signal notifies the main thread to update the interface display.

**2.2 Asynchronous Programming and Network Requests**

Using the `aiohttp` library for asynchronous network requests avoids blocking issues associated with traditional synchronous requests, especially in scenarios requiring frequent server status checks, making the entire program run more smoothly.

**2.3 Configuration File Reading and Writing with Path Management**

The `configparser` module reads and writes to the `config.ini` configuration file, managing file save path information effectively, considering details such as path list length limits and duplicates.

**2.4 Timer Usage**

A `QTimer` timer periodically triggers status update methods, allowing users to see dynamic changes in server operation without manual refreshes.

#### 3. Features

**3.1 File Upload Functionality**

Users can initiate file upload requests via the web interface (through the `/upload` endpoint), supporting multiple file uploads at once. The server saves files according to the upload path set in the configuration file and returns upload result notifications.

**3.2 Server Status Viewing Functionality**

The client can asynchronously retrieve real-time server status information (including upload rate, download rate, connected device information, and server operational status) every 3 seconds and update the graphical interface to provide users with an intuitive understanding of server operations.

**3.3 Device Connection Assistance Functionality**

Provides a device connection window that displays local access addresses and server IP addresses, equipped with "Copy" buttons and QR codes, helping other devices within the local network connect to the server for file transfer operations.

**3.4 File Save Path Management Functionality**

The client offers comprehensive file save path management functions, including reading paths from the configuration file, adding new save paths, viewing folder contents, and setting selected paths as specific upload paths.

#### 4. Components

**4.1 Server Side (Based on Flask Framework)**

- **Routing and API Handling**: Includes endpoints like `/upload` for handling file upload logic, `/api/get-upload-url` for providing upload URLs, and `/status` for reporting server status.
- **Background Thread Processing**: A background thread created by the `NetworkStatsThread` class continuously retrieves and updates network statistics (such as upload and download rates), providing real-time network-related metrics for server status data.
- **Configuration File Reading**: The `configparser` module reads the `config.ini` configuration file to obtain relevant configuration information such as file upload paths.

**4.2 Client Side (Based on PyQt5 Framework)**

- **Main Window Component (`ServerManagerApp` Class)**: Integrates server control buttons, status display labels, file save path management components, and a device connection window button. It uses signals and slots mechanisms and timers to interact with the server and update the interface.
- **Device Connection Window Component (`DeviceConnectionWindow` Class)**: Presented as a dialog box, it includes components for displaying local access addresses, IP addresses, and QR codes, assisting devices within the local network in connecting to the server for file transfer operations.

In summary, the Local Network File Transfer Assistant Web Edition integrates a web application with a graphical interface client, aiming to simplify file transfer processes within a local network, provide an intuitive user experience, and ensure the security and efficiency of file transfers.


