"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: Holds the functions for the metrics route
"""
# Imports #
import global_vars
from numpy import percentile
import requests


def measure_latency(vendor: str):
    """
    Measures latency of a vendor.
    :param vendor: the vendor to check
    :return: the measured latency
    """
    # not incrementing the request counter because it is not a user request #
    return requests.get(global_vars.ApiConsts.VENDORS[vendor]).elapsed.total_seconds() * 1000


def generate_metrics() -> dict[str, dict[str, float]]:
    """
    Generates metrics holding the latencies according to percentiles and vendors.
    :return: dict that holds all the vendors and latencies according to percentiles - dict[str, dict[str, float]]
    """
    db_data = global_vars.ApiVars.database.get_data()
    print(db_data)
    res = dict()
    for vendor, latencies in db_data.items():
        latency = measure_latency(vendor)
        if latencies:
            latencies = list(latencies)
            latencies.append(latency)
        else:
            latencies = [latency]
        print(latencies)

        global_vars.ApiVars.database.add_latency(latency, vendor)
        res[vendor] = {
            "percentile50": percentile(latencies, 50),
            "percentile75": percentile(latencies, 75),
            "percentile95": percentile(latencies, 95),
            "percentile99": percentile(latencies, 99)
        }
    return res
