import json
import os
import winreg

APP_NAME = "Late4Bus"

def get_exe_path() -> str:
    import sys
    return sys.executable if getattr(sys, "frozen", False) else ""

def set_startup(enabled: bool):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                             0, winreg.KEY_SET_VALUE)
        if enabled:
            exe = get_exe_path()
            if exe:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def get_startup_enabled() -> bool:
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                             0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def _get_config_path():
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    app_dir = os.path.join(app_data, "Late4Bus")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "config.json")

CONFIG_PATH = _get_config_path()

DEFAULT_CONFIG = {
    "api_key": "",
    "bus_stops": [],
    "mrt_stations": [],
    "widget": {
        "x": 100,
        "y": 100,
        "refresh_interval": 30
    }
}

# bus_stops entry shape:
# {
#     "stop_code": "42239",
#     "stop_name": "Aft Jln Jurong Kechil",
#     "road": "Toh Tuck Rd",
#     "services": ["41", "77"]   <-- empty list means show all
# }

# mrt_stations entry shape:
# {
#     "station_code": "EW23",
#     "station_name": "Clementi",
#     "line": "EWL",
#     "directions": [
#         { "label": "Towards Pasir Ris", "key": "towards_pasir_ris" }
#     ]
# }


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        # backfill missing keys
        for key, val in DEFAULT_CONFIG.items():
            if key not in data:
                data[key] = val
        return data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def is_first_run():
    return not os.path.exists(CONFIG_PATH) or not get_api_key()


def save_widget_position(x: int, y: int):
    config = load_config()
    config["widget"]["x"] = x
    config["widget"]["y"] = y
    save_config(config)

def _save_widget_geometry(x: int, y: int, w: int, h: int):
    config = load_config()
    config["widget"]["x"] = x
    config["widget"]["y"] = y
    config["widget"]["width"] = w
    config["widget"]["height"] = h
    save_config(config)

def get_api_key() -> str:
    return load_config().get("api_key", "")

def save_api_key(key: str):
    config = load_config()
    config["api_key"] = key.strip()
    save_config(config)