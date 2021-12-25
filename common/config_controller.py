import os
import configparser

config_file_path = "config.ini"

def validate_config_file():
    if os.path.exists(config_file_path):
        return "OK"
    else:
        return "ERROR: \"{}\" NOT EXISTS".format(config_file_path)

def validate_config(values):
    errors = ""
    for value in values:
        if str(value).startswith("ERROR:"):
            errors = errors + "\n" + value
    if errors == "":
        return True
    else:
        print(errors)
        return False

def get_section(section):
    if validate_config_file() == "OK":
        config_file_data = configparser.ConfigParser()
        config_file_data.read(config_file_path)
        if section in config_file_data:
            return config_file_data[section]
        else:
            return "ERROR: NO \"{}\" SECTION IN CONFIG FILE".format(section)
    else:
        return validate_config_file()

def get_config(section, config):
    section_config = get_section(section)
    if str(section_config).startswith("ERROR:") == False:
        if config in section_config:
            return section_config[config]
        else:
            return "ERROR: NO [{}][{}] IN CONFIG FILE".format(section, config)
    else:
        return section_config

def get_section_name_list():
    if validate_config_file() == "OK":
        black_list = ["DEFAULT", "APP", "LOGS"]
        config_file_data = configparser.ConfigParser()
        config_file_data.read(config_file_path)
        section_name_list = []
        for section in config_file_data:
            if str(section) not in black_list:
                section_name_list.append(str(section))
        return section_name_list
    else:
        return validate_config_file()
