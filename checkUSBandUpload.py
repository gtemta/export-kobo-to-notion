import collections 
import collections.abc
import os
import shutil
import time
import threading
import subprocess
try:
    import win32file
    import win32con
    import win32gui
    import win32event
except ImportError as e:
    print("Failed to import win32file or win32con:", e)
    # Handle the failure accordingly




# 定義要複製的文件和目的地目錄
source_fileName = "KoboReader.sqlite"
source_filePath = ".kobo"

destination_dir = "E:\\koboNotion\\export-kobo-to-notion\\"
destination_file_name = "KoboReader.sqlite"

def copy_file(source, destination):
    try:
        shutil.copy(source, destination_dir)
        print(f"copy document success {destination_dir}")
    except Exception as e:
        print(f"copy file encounter error：{e}")

def execute_notion_upload(destination_dir):
    try:
        
        if not os.path.exists(destination_dir):
            print("Target do NOT EXIST")
            return

        # Check is already in destination_dir
        os.chdir(destination_dir)

        
        process = subprocess.Popen(["npm", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
        # Real time result form npm start
        while True:
            output_line = process.stdout.readline()
            if not output_line and process.poll() is not None:
                break
            print(output_line.strip())

        # Check npm status
        if process.returncode == 0:
            print("npm start SUCCESS")
        else:
            print("npm start FAILURE")

    except Exception as e:
        print(f"Exception：{e}")


def copy_upload_note(source_file):
    copy_file(source_file, destination_dir)
    execute_notion_upload(destination_dir)

def check_for_file(file_path):
    return os.path.exists(file_path)

def watch_usb_device():
    while True:
        detect_EReader_connected()
        time.sleep(10)  # Sleep for 10 seconds

def get_drive_letters(drive_list):
    drives = []
    for i in range(26):  # 26 letters in the English alphabet (A-Z)
        mask = 1 << i
        if drive_list & mask:
            drives.append(chr(65 + i) + ":\\")  # Convert bitmask to drive letter (A-Z)
    return drives

def is_usb_removable(drive_path):
    drive_type = win32file.GetDriveType(drive_path)
    return drive_type == win32file.DRIVE_REMOVABLE

def get_usb_removable_drives():
    drive_list = win32file.GetLogicalDrives()
    usb_drives = []
    
    for i in range(26):  # Check from A: to Z: drives
        mask = 1 << i
        if drive_list & mask:
            drive_letter = chr(65 + i) + ":\\"
            if is_usb_removable(drive_letter):
                usb_drives.append(drive_letter)
    
    return usb_drives

def detect_EReader_connected():
    print("Try Detect EReader")
    drive_type_removable = 2
    drive_list = win32file.GetLogicalDrives()
    bitmask = 1
    usb_removable_drives = get_usb_removable_drives()
    if usb_removable_drives:
        print("USB Removable Drives:")
        for drive in usb_removable_drives:
            file_to_check = os.path.join(drive, source_filePath, source_fileName)
            if check_for_file(file_to_check):
                print(f"File found in drive {drive}: {file_to_check}")
                return True, file_to_check
            else:
                print(f"File not found in drive {drive}")
        return False, None

    # if drive_list > 0:
    #     if drive_list & bitmask:
    #         drive_name = f"{chr(65 + bin(bitmask).count('1') - 1)}:\\"
    #         drive_type = win32file.GetDriveType(drive_name)
    #         if drive_type == drive_type_removable:
    #             print(f"Detected removable drive: {drive_name}")

    #             # Here you can perform operations for the connected drive
    #             # For instance, copy files, launch an application, etc.
    #     drive_list >>= 1
    #     bitmask <<= 1

if __name__ == "__main__":
    # For Windows-specific modules:
    found, fileName = detect_EReader_connected()
    if found:
        copy_upload_note(fileName)
        print("更新完畢，關閉程式")
    else:
        usb_monitor_thread = threading.Thread(target=watch_usb_device)
        usb_monitor_thread.start()
