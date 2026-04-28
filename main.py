# main.py — launch the bakery app from PyCharm green button
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, "app.py"])
