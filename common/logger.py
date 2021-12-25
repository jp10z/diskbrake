from datetime import datetime
import inspect, traceback
import os
import threading
from pathlib import Path
from common.config_controller import get_config

def get_log_config_path():
    log_path = get_config("LOGS", "PATH")
    if str(log_path).startswith("ERROR: "):
        print("> LOGGER ERROR: PATH CONFIG NOT VALID, ONLY CONSOLE PRINT MODE")
        return None
    return log_path

def get_log_config_level():
    log_level = get_config("LOGS", "LEVEL")
    if str(log_level).startswith("ERROR: "):
        print("> LOGGER: LEVEL CONFIG NOT VALID, USING DEFAULT 4")
        return 4
    else:
        try:
            log_level = int(log_level)
        except:
            print("> LOGGER: LEVEL CONFIG NOT VALID, USING DEFAULT 4")
            return 4
    return log_level

path = get_log_config_path()
level = get_log_config_level()

level_text = {
    1: "CRITICAL",
    2: "ERROR",
    3: "WARNING",
    4: "INFO",
    5: "DATA",
    6: "DEBUG"
}
    

class Logger():
    def critical(text):
        if 1 <= level:
            write_console_and_file(1, text)
    def error(text):
        if 2 <= level:
            write_console_and_file(2, text)
    def warning(text):
        if 3 <= level:
            write_console_and_file(3, text)
    def info(text):
        if 4 <= level:
            write_console_and_file(4, text)
    def data(text):
        if 5 <= level:
            write_console_and_file(5, text)
    def debug(text):
        if 6 <= level:
            write_console_and_file(6, text)
    def trace():
        if 6 <= level:
            write_console_and_file(6, "TRACE: {}".format(get_debug_path(2)))
    def trace_l(level):
        if 6 <= level:
            write_console_and_file(6, "TRACE: {}".format(get_debug_path(level)))
    def exception():
        Logger.error("UNHANDLED EXCEPCION")
        if 6 <= level:
            write_console_and_file(6, str(traceback.format_exc()).replace("\n", " "))

def get_timestamp():
    return datetime.now()

def get_thread_id():
    thread_id = threading.get_native_id()
    return f"{thread_id:06d}"

def get_debug_path(level):
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    return "{}/{}:{}".format(calframe[level][1], calframe[level][3], calframe[level][2])

def write_console_and_file(level, text):
    text = "{} [{}] [{}] {}".format(get_timestamp(), get_thread_id(), level_text.get(level), text).replace("\n", " ")
    print(text)
    if path is None: return
    with open(get_file_name(), "a+") as file:
        file.seek(0)
        data = file.read(100)
        if len(data) > 0 :
            file.write("\n")
        file.write(text)

def get_file_name():
    date = datetime.today().strftime("%Y-%m-%d")
    if not os.path.isdir(path):
        Path(path).mkdir(parents=True, exist_ok=True)
        os.chmod(path, 0o777)
    return "{}/{}.{}.log".format(path, date, f"{os.geteuid():05d}")