import pyudev

def detect_usb_devices():
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
    detect_usb_devices()