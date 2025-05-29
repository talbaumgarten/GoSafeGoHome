import subprocess
import os


# Set the paths to your frontend and backend directories
BACKEND_DIR = os.path.abspath("./backend/")
FRONTEND_DIR = os.path.abspath("./frontend/")

import threading
import os
import time

def run_frontend(path):
    os.chdir(path + "/frontend")
    os.system("npm start")

def run_backend(path):
    os.chdir(path + "/backend")
    os.system("uvicorn main:app --reload")

# ==== MAIN THREAD STARTS BOTH ====
if __name__ == "__main__":
    path = os.path.abspath(os.getcwd())
    backend_thread = threading.Thread(target=run_backend, args=[path])
    backend_thread.start()
    time.sleep(3)
    frontend_thread = threading.Thread(target=run_frontend, args=[path])
    frontend_thread.start()

    backend_thread.join()
    frontend_thread.join()