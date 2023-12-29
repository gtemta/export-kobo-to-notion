import collections 
import collections.abc
import os
import shutil
import time
import win32file
import win32con
import threading
import subprocess
import pyudev



# 定義要複製的文件和目的地目錄
source_file = "K:\\.kobo\\KoboReader.sqlite"
destination_dir = "E:\\koboNotion\\export-kobo-to-notion\\"
destination_file_name = "highlights.sqlite"

def copy_file(source, destination):
    try:
        shutil.copy(source_file, destination_dir + new_file_name)
        print(f"文件已成功複製到 {destination_dir + new_file_name}")
    except Exception as e:
        print(f"複製文件時出錯：{e}")

def execute_notion_upload():
    # 定義Node.js專案目錄
    nodejs_project_dir = "/path/to/your/nodejs/project"

    # 確保腳本的當前工作目錄設置為Node.js專案目錄
    os.chdir(nodejs_project_dir)

    try:
        # 使用subprocess運行npm start命令
        subprocess.Popen(["npm", "start"])
        print("已觸發 npm start 命令")
    except Exception as e:
        print(f"觸發 npm start 命令時出錯：{e}")

def copy_upload_note():
    copy_file(source_file, destination_dir)
    execute_notion_upload()

def watch_usb_device():
    while True:
        try:
            # 監聽USB設備插入事件
            result = win32file.ReadDirectoryChangesW(
                "K:\\",  # 監聽的監控目錄，這裡使用D:作為USB監控根目錄，根據實際情況更改
                1,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME,
                None,
                None,
            )

            for action, file_name in result:
                if action == 1:  # 1 表示文件被創建（插入USB）
                    print(f"檢測到USB設備插入：{file_name}")
                    if os.path.basename(file_name) == "USB_FILE_NAME":  # 檢查插入的USB設備是否符合條件
                        copy_upload_note()

        except Exception as e:
            print(f"監聽USB設備時出錯：{e}")

def detect_EReader_connected():
    context = pyudev.Context()

    # 監聽USB設備的插入事件
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    for device in iter(monitor.poll, None):
        if device.action == 'add':  # 檢測到USB設備插入
            print(f"檢測到USB設備插入：{device.device_node}")
            print(f"裝置名稱：{device.get('DEVNAME')}")

            # 在此處添加您想要執行的操作，例如複製文件、啟動應用程序等

if __name__ == "__main__":
    if (detect_EReader_connected()):
        copy_upload_note()
    else:
        usb_monitor_thread = threading.Thread(target=watch_usb_device)
        usb_monitor_thread.start()