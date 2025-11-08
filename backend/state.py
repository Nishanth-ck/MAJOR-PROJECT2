import json
import os

STATE_FILE = "state.json"

DEFAULT_STATE = {
    "monitor_folders": [
        r"C:\Users\NISHANTH CK\Desktop\monitor_here"
    ],
    "backup_folder": r"C:\Users\NISHANTH CK\Desktop\backup_here",
    "startMonitoring": False
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_STATE.copy()

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)




