import os
import sys
import subprocess
from time import sleep
print("opening google")
os.system("start cmd /k chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\TEGchrome")
sleep(0.3)
print("closing cmd")
os.system("taskkill /f /im cmd.exe")
sleep(1)
print("running code")
subprocess.run(['py','main.py'])

