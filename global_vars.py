"""
    AUTHOR: Ophir Nevo Michrowski.
    DESCRIPTION: Holds the global constants
"""
import logging


class ApiConsts:
    API_KEY_IPAPI = "https://ipapi.co/%s/json/"
    API_KEY_IPSTACK = "http://api.ipstack.com/%s?access_key=298da56bf87712d26bd7523373620a0c"
    VENDORS = {'ipstack': API_KEY_IPSTACK, 'ipapi': API_KEY_IPAPI}


class LogConsts:
    LOGGER = logging.getLogger("main_logger")
    LOG_LEVEL = logging.DEBUG
    LOG_DIR = r"Logs"
    LOG_FILE = LOG_DIR + r"/main.log"
    LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"


class ApiVars:
    ipstack_max_requests_per_hour: list[int, float] = [34, 43345543.45]
    database = None
