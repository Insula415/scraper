import os
from time import sleep
from tkinter import Tk
from tkinter.filedialog import askdirectory

print("Please select your directory")

path = askdirectory(title='Please select your directory')
print(path)

with open("chrome.txt", "w") as f:
    f.writelines(path)
    f.close()

# making a directory
main_dir = "bin"
os.mkdir(main_dir,mode = 0o666) 
print("Directory '% s' built" % main_dir)
sleep(2)
ano_dir = "upload"
os.mkdir(ano_dir,mode = 0o666) 
print("Directory '% s' built" % ano_dir)
sleep(2)
os.system("start cmd /k pip install -r requirements.txt")
sleep(1)
os.system("taskkill /f /im cmd.exe")