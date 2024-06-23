"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: This file holds the database handler.
"""
import os.path
import sqlite3

import global_vars

# Constants #
DB_DIR = r"databases"
DB_PATH = DB_DIR + r"\latencies.db"
TABLE_NAME = "LATENCIES"
LATENCY_COLUMN = "LATENCIES"


class LatencyDatabase:
    """Handles the database for the latencies"""

    @staticmethod
    def __create_table() -> None:
        """
        creates the latency table and file
        :return: None
        """
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(f"CREATE TABLE {TABLE_NAME} (VENDOR TEXT PRIMARY KEY NOT NULL, {LATENCY_COLUMN} TEXT);")

    def __init__(self) -> None:
        """
        Constructor of the class
        """
        if not os.path.isdir(DB_DIR):
            os.makedirs(DB_DIR)
        if not os.path.isfile(DB_PATH):
            self.__create_table()

    def get_data(self) -> dict[str, tuple[float]]:
        """
        Gets all the latencies from the db
        :return: dict[str, list[float]]
        """
        with sqlite3.connect(DB_PATH) as connection:
            all_data = connection.execute(f"SELECT * FROM {TABLE_NAME}")

        res = dict()
        if all_data:
            for vendor in all_data:
                res[vendor[0]] = tuple([float(latency) for latency in vendor[1].split(", ")]) if vendor[1] else []

        return res

    def add_latency(self, latency: float, vendor: str) -> None:
        """
        Will add to the database a latency according to a vendor.
        :param vendor: The vendor that had the latency.
        :param latency: The latency.
        :return: None
        """
        if not isinstance(latency, float):
            global_vars.LogConsts.LOGGER.error("Latency must be of type float")
            return

        data = self.get_data()
        try:
            vendor_latencies = list(data[vendor])
            vendor_latencies.append(latency)
        except KeyError:
            global_vars.LogConsts.LOGGER.error("Vendor does not exist")
            return

        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                f"UPDATE {TABLE_NAME} SET {LATENCY_COLUMN} = '{', '.join([str(x) for x in vendor_latencies])}' WHERE VENDOR = '{vendor}'")

    def add_vendor(self, vendor: str) -> None:
        """
        Adds a vendor to the db.
        :param vendor: The vendor to add.
        :return: None
        """
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(f"INSERT INTO {TABLE_NAME} (VENDOR, {LATENCY_COLUMN}) VALUES ('{vendor}', NULL)")

    def search_vendor(self, vendor: str) -> bool:
        """
        Will check if a vendor is in the db.
        :param vendor: The vendor to check.
        :return: Whether the vendor is in the db
        """
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE VENDOR = ?", (vendor,))
            res = cursor.fetchone() is not None
        return res

    def search_and_add_vendor(self, vendor: str) -> None:
        """
        Will search for a vendor and if he is not there will add it.
        :param vendor: the vendor to check
        :return: None
        """
        if not self.search_vendor(vendor):
            self.add_vendor(vendor)

    def delete_vendor(self, vendor: str) -> None:
        """
        This will delete a vendor from the database.
        :param vendor: The vendor to delete.
        :return: None
        """
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(f"DELETE FROM {TABLE_NAME} WHERE VENDOR = '{vendor}'")


def database_auto_tests() -> None:
    """
    Testing the database manager
    :return: None
    """
    tmp = LatencyDatabase()
    assert not tmp.search_vendor('test')
    tmp.add_vendor('test')
    assert tmp.search_vendor('test')
    tmp.add_latency(0.0, "test")
    tmp.add_latency(56.23, "test")
    tmp.delete_vendor('test')
    assert not tmp.search_vendor('test')
