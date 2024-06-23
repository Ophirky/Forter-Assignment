"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: This file contains all the needed constants for the HTTP packet
"""
import logging

# HTTP necessities #
HTTP_VERSION = b"HTTP/1.1"
HEADER_SEPERATOR = b"\r\n"
BODY_SEPERATOR = HEADER_SEPERATOR * 2

# Other #
RECV_TIMEOUT = 3

# Logging #
LOG_LEVEL = logging.ERROR
LOG_DIR = r"Logs"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
LOG_FILE_NAME = LOG_DIR + r"\http_logs.log"
HTTP_LOGGER_NAME = "http_log"
HTTP_LOGGER = logging.getLogger(HTTP_LOGGER_NAME)

# Headers #
LOCATION_HEADER = b"Location: %s"
CONTENT_TYPE_HEADER = b"Content-Type: %s"
CONTENT_LEN_HEADER = b"Content-Length: %d"
HOST_HEADER = b"Host: %s"

# Dictionaries #
REQUEST_TYPES = {
    "get": b"GET",
    "post": b"POST",
    "put": b"PUT",
    "delete": b"DELETE"
}

ERROR_CODES = {
    200: b"OK",
    500: b"INTERNAL SERVER ERROR",
    302: b"MOVED TEMPORARILY",
    403: b"FORBIDDEN",
    404: b"NOT FOUND",
    400: b"BAD REQUEST",
    301: b"MOVED PERMANENTLY",
    401: b"UNAUTHORIZED",
    405: b"METHOD NOT ALLOWED",
    413: b"PAYLOAD TOO LARGE",
    502: b"BAD GATEWAY",
    503: b"SERVICE UNAVAILABLE"
}

MIME_TYPES = {
    ".html": "text/html;charset=utf-8",
    ".jpg": "image/jpeg",
    ".css": "text/css",
    ".js": "text/javascript; charset=UTF-8",
    ".txt": "text/plain",
    ".ico": "image/x-icon",
    ".gif": "image/jpeg",
    ".png": "image/png",
    ".ttf": "font/ttf",
    ".json": "application/json",
    "sse": "text/event-stream"
}

# Socket Related #
RECV_LENGTH = 1024
PORT = 80
IP = "0.0.0.0"

# Logging level - info #
NO_BODY = "Message has no body."
NEW_CLIENT = "{}:{} connected."
TESTS_RUN = "Auto tests were run."
FOUR_O_FOUR = "http_lib/html_defaults/404.html"
