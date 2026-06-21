import os
import win32gui
import win32process
import psutil
import time

def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        proc = psutil.Process(pid)
        return proc.name(), win32gui.GetWindowText(hwnd)
    except Exception as e:
        return None, None

print("Checking active window...")
print(get_active_window_title())
