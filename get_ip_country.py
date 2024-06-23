"""
    AUTHOR: Ophir Nevo Michrowski.
    DESCRIPTION: Handles all the things related to getting the ips country.
"""
# Imports #
import time
import global_vars
import requests
from ipaddress import ip_address

# Constants #
RESET_IPSTACK_REQUEST_COUNT_INTERVAL = 3600

# Other Vars #
ipstack_current_request_count = 0


def check_reset_request_count() -> None:
    """
    Checks if the ipstack_current_request_count needs to be reset.
    :return: None
    """
    global ipstack_current_request_count
    if time.time() - global_vars.ApiVars.ipstack_max_requests_per_hour[1] >= RESET_IPSTACK_REQUEST_COUNT_INTERVAL:
        ipstack_current_request_count = 0
        global_vars.ApiVars.ipstack_max_requests_per_hour[1] += 3600  # Add an hour to the timestamp


def get_ip_country(ip: str) -> dict:
    """
    Gets the ip information from the given ip
    :param ip: the users ip
    :return dict: dataset including the ipCountry, vendor, latency, & the ip it self.
    """
    global ipstack_current_request_count
    check_reset_request_count()

    response = None
    latency = 0
    vendor = list(global_vars.ApiConsts.VENDORS.keys())[0]
    try:
        # Use the second vendor #
        if ipstack_current_request_count == global_vars.ApiVars.ipstack_max_requests_per_hour[0]:
            response = requests.get(global_vars.ApiConsts.API_KEY_IPAPI % ip)
            vendor = list(global_vars.ApiConsts.VENDORS.keys())[1]

        # Use the first vendor #
        else:
            response = requests.get(global_vars.ApiConsts.API_KEY_IPSTACK % ip)
            ipstack_current_request_count += 1

        latency = response.elapsed.total_seconds() * 1000
        global_vars.ApiVars.database.add_latency(latency, vendor)

    except requests.RequestException as e:
        global_vars.LogConsts.LOGGER.error(e)

    response = response.json()
    if 'error' not in response.keys():
        res = {
            "ip": ip,
            "CountryName": response["country_name"] if not ip_address(ip).is_private else "Localhost",
            "apiLatency": latency,
            "vendor": vendor
        }
    else:
        res = {'error': response["error"], "reason": response["reason"]}

    return res
