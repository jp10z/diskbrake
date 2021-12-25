# IMPORT
import os
from pathlib import Path
import glob
from common.config_controller import get_config, get_section_name_list
from common.logger import Logger
from common.sh_controller import run_sh

# GLOBAL VARIABLES
version = "1.0.0"
processed_state_files = []

# MAIN FUNCTION
def main():

    # CHECK CONFIG FILE EXISTS
    Logger.debug("CHECK CONFIG FILE EXISTS")
    if not config_file_exists(): return

    # CHECK PACKAGE PREREQUISITES
    Logger.debug("CHECK PACKAGE HDPARM")
    if not package_hdparm_is_installed(): return

    # CHECK USER PERMISSIONS
    Logger.debug("CHECK USER PERMISSIONS")
    if not user_is_root(): return

    # READ DEVICES FROM CONFIG
    Logger.debug("READ DEVICES FROM CONFIG")
    device_list = get_device_list()
    if device_list is None: return

    # ITERATE ALL DEVICES
    Logger.debug("ITERATE ALL DEVICES")
    device_number = 0
    for device in device_list:
        device_number += 1
        Logger.info("DEVICE {} OF {} : {}".format(device_number, len(device_list), device))

        # GET CONFIG CYCLES
        Logger.debug("GET CONFIG CYCLES")
        config_cycles = get_config_device_cycles(device)
        if not config_cycles: continue

        # GET UUID FROM CONFIG
        Logger.debug("GET UUID FROM CONFIG")
        uuid = get_config_device_uuid(device)
        if uuid is None: continue
        
        # CHECK IF UUID IS VALID
        Logger.debug("CHECK IF UUID IS VALID")
        if not uuid_is_valid(uuid): continue

        # GET DEV BY UUID
        Logger.debug("GET DEV BY UUID")
        dev = get_dev_by_uuid(uuid)
        if dev is None: continue

        # GET PREVIOUS STATE
        Logger.debug("GET PREVIOUS STATE")
        previous_state = get_previous_state(device, uuid, dev)

        # GET PREVIOUS CYCLES
        Logger.debug("GET PREVIOUS CYCLES")
        cycles = get_previous_cycles(device, uuid, dev)

        # INCREMENT CYCLES COUNT
        Logger.debug("INCREMENT CYCLES COUNT")
        cycles += 1
        Logger.data("NEW CYCLES COUNT: {}".format(cycles))

        # GET CURRENT STATE
        Logger.debug("GET CURRENT STATE")
        current_state = get_current_state(dev)
        if current_state is None: continue

        # IF PREVIOUS != CURRENT
        if previous_state != current_state:
            Logger.debug("IF PREVIOUS != CURRENT")
            Logger.info("{}: DEVICE WITH CHANGES ({}/{})".format(device, 0, config_cycles))

            # RESET CYCLES COUNT
            Logger.debug("RESET CYCLES COUNT")
            cycles = 0
            
            # PING DEVICE
            Logger.debug("PING DEVICE")
            if not ping_device(dev): continue

            # GET NEW CURRENT STATE
            Logger.debug("GET NEW CURRENT STATE")
            current_state = get_current_state(dev)
            if current_state is None: continue

            # SAVE STATE
            Logger.debug("SAVE STATE")
            save_state(device, uuid, dev, current_state, cycles)

        # ELIF PREVIOUS == CURRENT AND CYCLES < CONFIG_CYCLES
        elif previous_state == current_state and cycles < config_cycles:
            Logger.debug("ELIF PREVIOUS == CURRENT AND CYCLES < CONFIG_CYCLES")
            Logger.info("{}: DEVICE WITHOUT CHANGES ({}/{})".format(device, cycles, config_cycles))

            # PING DEVICE
            Logger.debug("PING DEVICE")
            if not ping_device(dev): continue

            # GET NEW CURRENT STATE
            Logger.debug("GET NEW CURRENT STATE")
            current_state = get_current_state(dev)
            if current_state is None: continue

            # SAVE STATE
            Logger.debug("SAVE STATE")
            save_state(device, uuid, dev, current_state, cycles)

        # ELIF PREVIOUS == CURRENT AND CYCLES == CONFIG_CYCLES
        elif previous_state == current_state and cycles == config_cycles:
            Logger.debug("ELIF PREVIOUS == CURRENT AND CYCLES == CONFIG_CYCLES")

            # START SLEEP DEVICE
            Logger.info("{}: START SLEEP ({}/{})".format(device, cycles, config_cycles))
            if not sleep_device(dev): continue

            # GET NEW CURRENT STATE
            Logger.debug("GET NEW CURRENT STATE")
            current_state = get_current_state(dev)
            if current_state is None: continue

            # SAVE STATE
            Logger.debug("SAVE STATE")
            save_state(device, uuid, dev, current_state, cycles)
        
        # ELIF PREVIOUS == CURRENT AND CYCLES > CONFIG_CYCLES
        else:
            Logger.debug("ELIF PREVIOUS == CURRENT AND CYCLES > CONFIG_CYCLES")
            Logger.info("{}: DEVICE PREVIOUSLY ASLEEP".format(device))

            # PRINT CYCLES COUNT
            Logger.debug("PRINT CYCLES COUNT")
            Logger.debug("CYCLE {} OF {}".format(cycles, config_cycles))

            # SAVE STATE
            Logger.debug("SAVE STATE")
            save_state(device, uuid, dev, current_state, cycles)

    Logger.debug("END DEVICE ITERATION")

    # DELETE NOT PROCESSED STATE FILE
    Logger.debug("DELETE NOT PROCESSED STATE FILE")
    delete_not_processed_state_files()

def config_file_exists():
    if os.path.isfile("config.ini"):
        Logger.debug("TRUE")
        return True
    else:
        Logger.debug("FALSE")
        Logger.error("NO CONFIG FILE FOUND")
        return False

def user_is_root():
    exec_user = f"{os.geteuid():05d}"
    Logger.debug("USER {}".format(exec_user))
    if exec_user != "00000":
        Logger.error("THIS SCRIPT MUST BE EXECUTED AS ROOT")
        return False
    else:
        return True

def package_hdparm_is_installed():
    if not os.path.isfile("/usr/sbin/hdparm"):
        Logger.error("UNIX PACKAGE \"hdparm\" IS NOT INSTALLED")
        return False
    else:
        Logger.debug("UNIX PACKAGE \"hdparm\" OK")
        return True

def get_device_list():
    device_list = get_section_name_list()
    if len(device_list) == 0:
        Logger.warning("NO DEVICES IN CONFIG FILE")
        return None
    Logger.data("device_list: {}".format(device_list))
    return device_list

def get_config_device_uuid(device):
    uuid = get_config(device, "UUID")
    if str(uuid).startswith("ERROR: "):
        Logger.error(uuid)
        return None
    return uuid

def get_config_device_cycles(device):
    cycles = get_config(device, "CYCLES")
    if str(cycles).startswith("ERROR: "):
        Logger.error(cycles)
        return None
    else:
        try:
            cycles = int(cycles)
            if cycles <= 0:
                Logger.error("INVALID CYCLES IN CONFIG FILE, CANNOT BE LESS THAN 0")
                return None
            if cycles == 1:
                Logger.warning("USING CYCLES = 1 IS DANGERIOUS, TRY TO USE A LARGER VALUE")
            return cycles
        except:
            Logger.error("INVALID CYCLES IN CONFIG FILE, NOT NUMERIC")
            return None

def uuid_is_valid(uuid):
    results = run_sh("(ls /dev/disk/by-uuid/{} >> /dev/null 2>&1 && echo yes) || echo no".format(uuid))
    if results["errors"] is not None:
        Logger.error("UNHANDLED ERROR")
        return False
    elif results["results"] == "no":
        Logger.warning("DEVICE NOT FOUND")
        return False
    return True

def get_dev_by_uuid(uuid):
    results = run_sh("ls -l /dev/disk/by-uuid/{}".format(uuid))
    if results["errors"] is not None or results["results"] is None:
        Logger.trace()
        Logger.error("UNHANDLED ERROR")
        return None
    partition = results["results"].split("->")[1].replace("../", "").strip()
    results = run_sh("basename \"$(readlink -f \"/sys/class/block/{}/..\")\"".format(partition))
    if results["errors"] is not None:
        Logger.trace()
        Logger.error("UNHANDLED ERROR")
        return None
    return results["results"]

def get_previous_state(device, uuid, dev):
    path = get_config("APP", "STATES_FILE_PATH")
    path = "{}/{}_{}_{}".format(path, device, uuid, dev)
    if os.path.exists(path):
        file = open(path, "r")
        previous_state = file.read().split(";")[0]
        file.close()
        Logger.data("PREVIOUS STATE: {}".format(previous_state))
        return previous_state
    else:
        Logger.data("PREVIOUS STATE: None")
        return None

def get_previous_cycles(device, uuid, dev):
    path = get_config("APP", "STATES_FILE_PATH")
    path = "{}/{}_{}_{}".format(path, device, uuid, dev)
    if os.path.exists(path):
        file = open(path, "r")
        cycles = file.read().split(";")[1]
        file.close()
        Logger.data("PREVIOUS CYCLES: {}".format(cycles))
        return int(cycles)
    else:
        Logger.data("PREVIOUS CYCLES: 0")
        return 0

def get_current_state(dev):
    results = run_sh("cat /sys/block/{}/stat | tr -dc \"[:digit:]\"".format(dev))
    if results["errors"] is not None:
        Logger.error("UNHANDLED ERROR")
        return None
    current_state =  results["results"]
    Logger.data("CURRENT STATE: {}".format(current_state))
    return current_state

def ping_device(dev):
    results = run_sh("/usr/sbin/hdparm -C /dev/{}".format(dev))
    if results["errors"] is not None:
        Logger.error("UNHANDLED ERROR")
        return False
    return True

def sleep_device(dev):
    results = run_sh("/usr/sbin/hdparm -y /dev/{}".format(dev))
    if results["errors"] is not None:
        Logger.error("UNHANDLED ERROR")
        return False
    return True

def save_state(device, uuid, dev, state, cycles):
    path = get_config("APP", "STATES_FILE_PATH")
    Path(path).mkdir(parents=True, exist_ok=True)
    path = "{}/{}_{}_{}".format(path, device, uuid, dev)
    file = open(path, 'w')
    file.write("{};{}".format(state, cycles))
    file.close()
    processed_state_files.append(path)

def delete_not_processed_state_files():
    path = get_config("APP", "STATES_FILE_PATH")
    Path(path).mkdir(parents=True, exist_ok=True)
    path = "{}/*".format(path)
    files = glob.glob(path)
    for file in files:
        if file not in processed_state_files:
            Logger.debug("REMOVE: {}".format(file))
            os.remove(file)

# INIT FUNCTION
if __name__ == "__main__":
    Logger.info("-- INIT v{}".format(version))
    try:
        main()
    except Exception as e:
        Logger.exception(e)
    Logger.debug("END APP")
