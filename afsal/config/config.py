from configparser import RawConfigParser
import configparser
import logging


def read_config_values(config_file, term_nm_colors):
    config_parser = RawConfigParser()
    config_parser.read(config_file)

    logging.debug("Reading config file \"" + config_file + "\"")

    config_values = {}


    def __config_get_value(config_fn, section, value_name, default_value):
        ret_value = None
        write_default_value = False

        try:
            ret_value = config_fn(section, value_name)
        except configparser.NoSectionError:
            # Section could not be found -> write it to the config file.
            config_parser[section] = {}
            write_default_value = True
            logging.debug("Config file section [\"" + section + "\"] not found -> writing it to the config file") 
        except configparser.NoOptionError:
            write_default_value = True

        if write_default_value:
            # Option could not be found -> write it to the config file.
            ret_value = default_value
            config_parser[section][value_name] = ret_value
            logging.debug("Config file option [\"" + section + "\"].\"" + value_name + "\" not found -> writing it to the config file")

        config_values[value_name] = config_fn(section, value_name)


    # Default values are specified here.
    __config_get_value(config_parser.getint, "SETTINGS", "NumberOfSubprocesses",             "4")
    __config_get_value(config_parser.getint, "SETTINGS", "NumberOfLinesReqToEnableSubprocs", "1024")
    __config_get_value(config_parser.get,    "SETTINGS", "DisableSubprocesses",              "False")
    __config_get_value(config_parser.get,    "SETTINGS", "GlobalRegexps",                    "False")

    with open(config_file, "w") as config_file:
        config_parser.write(config_file)

    return config_values
