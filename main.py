"""
    AUTHOR: Ophir Nevo Michrowski.
    DESCRIPTION: Handles the routes
"""
# Imports #
import db_handler
import http_lib
import time
import os
import logging
import sys
import global_vars
from get_ip_country import get_ip_country as gic
import metrics

# Constants #
APP = http_lib.app.App()

NOT_FOUND_RESPONSE = http_lib.http_message.HttpMsg(error_code=404)
HELP_MESSAGE = """This program is a proxy server that has two functions:
    getIpCountry: will return the country of the user's ip,
    metrics: will return a dataset with latencies sorted to percentiles from two different vendors.

to run the server you need to give the program a number argument that will be the max amount of requests in a hour
from the first vendor.
"""


@APP.route(b"/getIpCountry")
def get_ip_country_request(request: http_lib.http_parser.HttpParser) -> http_lib.http_message.HttpMsg:
    """
    Handle the user request for the country ip.
    :param request: the user request
    :return: dataset including the ipCountry, vendor, latency, & the ip it self.
    """
    error_code = 200
    search_result = gic(request.SRC)
    if "error" in search_result:
        error_code = 500

    return http_lib.http_message.HttpMsg(error_code=error_code, content_type=http_lib.constants.MIME_TYPES[".json"],
                                         body=str(search_result).encode())


@APP.route(b"/metrics")
def metrics_request(request: http_lib.http_parser.HttpParser) -> http_lib.http_message.HttpMsg:
    """
    Handle the metrics request.
    :param request: The user request
    :return: Dataset including latencies by percentages: percentile50, percentile75, percentile95, percentile99
             for each vendor.
    """
    return http_lib.http_message.HttpMsg(content_type=http_lib.constants.MIME_TYPES[".json"],
                                         body=str(metrics.generate_metrics()).encode())


# Call the function with your API URLs
def main() -> None:
    """
    The main function of the project.
    :return: None
    """
    global_vars.ApiVars.database = db_handler.LatencyDatabase()
    global_vars.ApiVars.database.search_and_add_vendor(list(global_vars.ApiConsts.VENDORS.keys())[0])  # ipstack
    global_vars.ApiVars.database.search_and_add_vendor(list(global_vars.ApiConsts.VENDORS.keys())[1])  # ipapi
    APP.run()


if __name__ == '__main__':
    # Checking for given variables #
    try:
        system_arguments = sys.argv
        if system_arguments[1] == "help":
            print(HELP_MESSAGE)
            sys.exit()

        global_vars.ApiVars.ipstack_max_requests_per_hour = [int(system_arguments[1]), time.time()]

    except ValueError as e:
        global_vars.LogConsts.LOGGER.error("No system argument was given")
        print("Must give a number argument for server to run. if help is needed give \"help\" arg.")
        sys.exit()

    # Asserts #
    http_lib.http_setup()
    db_handler.database_auto_tests()

    # Logging Setup #
    if not os.path.isdir(global_vars.LogConsts.LOG_DIR):
        os.makedirs(global_vars.LogConsts.LOG_DIR)
    file_handler = logging.FileHandler(global_vars.LogConsts.LOG_FILE)
    file_handler.setFormatter(logging.Formatter(global_vars.LogConsts.LOG_FORMAT))

    global_vars.LogConsts.LOGGER.setLevel(global_vars.LogConsts.LOG_LEVEL)
    global_vars.LogConsts.LOGGER.addHandler(file_handler)

    global_vars.LogConsts.LOGGER.info("Initiated logger & auto tests done")

    # Calling teh main function #
    main()
