import os
import shutil
import subprocess
import threading
import time
import logging
import uploadToNotion
try:
    import win32file
except ImportError as e:
    print("Failed to import win32file or win32con:", e)
    # Handle the failure accordingly

UsPython = True

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
logger = logging.getLogger()
file_handler = logging.FileHandler("usb_monitor.log")
console_handler = logging.StreamHandler()  # Add a console handler
logger.addHandler(file_handler)
logger.addHandler(console_handler)

SOURCE_FILE_NAME = "KoboReader.sqlite"
SOURCE_FILE_PATH = ".kobo"
DESTINATION_DIR = os.getcwd()


def copy_file(source, destination):
    try:
        shutil.copy(source, destination)
        logging.info(f"File copied successfully to {destination}")
    except Exception as e:
        logging.error(f"Error copying file: {e}")

def execute_notion_upload(destination_dir):
    try:
        if not os.path.exists(destination_dir):
            logging.warning("Destination directory does not exist")
            return

        os.chdir(destination_dir)
        if UsPython:
            process = subprocess.Popen(
                ["python", "uploadToNotion.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
        else:
            process = subprocess.Popen(
                ["npm", "start"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, encoding='utf-8')
        while True:
            output_line = process.stdout.readline()
            if not output_line and process.poll() is not None:
                break
            print(output_line.strip())  # For real-time output

        if process.returncode == 0:
            logging.info("upload to Notion succeeded")
        else:
            logging.error("upload to Notion failed")

    except Exception as e:
        logging.error(f"Exception: {e}")

def copy_upload_note(source_file):
    copy_file(source_file, DESTINATION_DIR)
    execute_notion_upload(DESTINATION_DIR)

def check_for_file(file_path):
    return os.path.exists(file_path)

def watch_usb_device():
    RetryTimes = 6
    while RetryTimes > 0:
        found, file_name = detect_ereader_connected()
        if found:
            logging.info("Found Devices Start Upload")
            copy_upload_note(file_name)
            break
        else:
            logging.info(f"Still Wait for Available Device: Retry in seconds Remain {RetryTimes} times")
            RetryTimes-=1
            time.sleep(10)
    if RetryTimes == 0:
        logging.error("All retry attempts exhausted. Exiting.")

        

def detect_ereader_connected():
    logging.debug("Trying to detect EReader")
    usb_removable_drives = get_usb_removable_drives()
    if usb_removable_drives:
        logging.debug("USB Removable Drives:")
        for drive in usb_removable_drives:
            file_to_check = os.path.join(drive, SOURCE_FILE_PATH, SOURCE_FILE_NAME)
            if check_for_file(file_to_check):
                logging.info(f"File found in drive {drive}: {file_to_check}")
                return True, file_to_check
            else:
                logging.info(f"File not found in drive {drive}")
    return False, None  # Always return a tuple

def get_usb_removable_drives():
    drive_list = win32file.GetLogicalDrives()
    usb_drives = []
    for i in range(26):
        mask = 1 << i
        if drive_list & mask:
            drive_letter = chr(65 + i) + ":\\"
            if is_usb_removable(drive_letter):
                usb_drives.append(drive_letter)
    return usb_drives

def is_usb_removable(drive_path):
    drive_type = win32file.GetDriveType(drive_path)
    return drive_type == win32file.DRIVE_REMOVABLE

if __name__ == "__main__":
    found, file_name = detect_ereader_connected()
    if found:
        copy_upload_note(file_name)
        print("Update completed. Closing the program.")
    else:
        usb_monitor_thread = threading.Thread(target=watch_usb_device)
        usb_monitor_thread.start()
