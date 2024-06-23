"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: HTTP protocol package. Includes (http parser and formatter, http request builder)
"""
import logging
import os.path
import http_lib.constants as consts
import http_lib.http_parser
import http_lib.http_message
import http_lib.app
import http_lib.functions
import http_lib.constants


def http_setup() -> None:
    """
    Function that contains all the auto_checks for the http package and sets up logger
    :return: None
    """
    http_lib.http_parser.auto_test_http_parser()
    http_lib.http_message.auto_test_http_message()

    # is_valid_request auto tests #
    request: bytes = b"GET /index.html HTTP/1.1\r\nHost: 192.168.37.45\r\n\r\n"
    request_invalid: bytes = b"GET /index.html HTTP/1.1\r\nHost:192.168.37.45\r\n\r\n"
    assert is_valid_request(request)["valid"], is_valid_request(request)["reason"]
    assert not is_valid_request(request_invalid)["valid"]

    # Start logger #
    if not os.path.isdir(consts.LOG_DIR):
        os.makedirs(consts.LOG_DIR)

    consts.HTTP_LOGGER.setLevel(consts.LOG_LEVEL)
    file_handler = logging.FileHandler(consts.LOG_FILE_NAME)
    file_handler.setFormatter(logging.Formatter(consts.LOG_FORMAT))
    consts.HTTP_LOGGER.addHandler(file_handler)

    consts.HTTP_LOGGER.info("http_lib initiated")


def is_valid_request(request: bytes) -> dict[bool, str] or dict[bool]:
    """
    Checks if a http request is valid.
    :param request: the request to validate.
    :return dict[bool, string]: {"valid": True/False, "reason":"reason"}
    """
    # Making sure that the argument is correct #
    if not isinstance(request, bytes):
        return {"valid": False, "reason": "request data type must be bytes"}

    # Split the request into lines #
    lines = request.decode('utf-8').split('\r\n')

    # Check if there's at least one line (the request line) and a blank line separating headers and body #
    if len(lines) < 2 or b'\r\n\r\n' not in request:
        return {"valid": False, "reason": "At least one line (the request line) and a blank line separating headers "
                                          "and body are needed."}

    # Check the request line for the correct number of elements and separators #
    request_line_parts = lines[0].split(' ')
    if len(request_line_parts) < 3:
        return {"valid": False, "reason": "Incorrect number of elements or separators."}

    # Ensure method, path, and HTTP version are correctly separated #
    method, path, version = request_line_parts[0], request_line_parts[1], request_line_parts[-1]
    if method.encode() not in consts.REQUEST_TYPES.values():
        return {"valid": False, "reason": f"{method} is not a real method in http_lib."}

    # Check if the request has a http version #
    if not method or not path or not version.startswith('HTTP/'):
        return {"valid": False, "reason": "Request must have http_lib version."}

    # Check headers for correct formatting
    is_host_header = False
    for header in lines[1:-2]:  # Ignoring the request line and the last two elements (the last header and the body)
        if ': ' not in header:
            return {"valid": False, "reason": f"{header} header does not contain colon-space separator."}
        if "Host" in header:
            is_host_header = True  # Mandatory host header is in the request

    # Check if the request has mandatory host header #
    if not is_host_header:
        return {"valid": False, "reason": "Host header is mandatory."}

    # Return true if the request is valid #
    return {"valid": True}


def read_file(path: str) -> http_message:
    """
    Create a request for a html page.
    :param path: the path to the html.
    :return http_message: the http formatted message containing the html file.
    """
    if not os.path.isfile(path):
        consts.HTTP_LOGGER.Exception("File not found.")
        raise FileNotFoundError("File not found.")
    else:
        with open(path, 'rb') as f:
            return f.read()
