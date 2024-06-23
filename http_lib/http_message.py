"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: Class that allows to create easy to use http_ophir messages including responses and requests
"""
# Imports #
import http_lib.constants as consts
import http_lib.functions


class HttpMsg:
    """Create easy to use http_ophir messages including responses and requests"""

    def __init__(self, error_code: int = 200, body: bytes = b"", **headers) -> None:
        """
        The constructor of the HttpMsg class.
        :param error_code: The error code of the message.
        :param body: The body of the message.
        :param headers: The headers of the message - host=127.0.0.1 -> { b"host": b"127.0.0.1"}
        :return: None
        """
        if headers is None:
            headers = dict()
        self.error_code = self.__error_code_finder(error_code)
        self.body = body
        self.headers = http_lib.functions.dict_to_bytes(headers)
        if body != b"":
            self.headers[b"content_length"] = str(len(body)).encode()

    @staticmethod
    def __error_code_finder(error_code: int) -> bytes:
        """
        Returns the error code and message using the error code.
        :param error_code: The error code to be found
        :return bytes: The error code
        """
        return_value = b"-1"
        if error_code in consts.ERROR_CODES.keys():
            try:
                return_value = str(error_code).encode() + b" " + consts.ERROR_CODES[error_code]
            except KeyError:
                consts.HTTP_LOGGER.exception(f"{error_code} is not valid")
                raise KeyError(f"{error_code} is not valid")
            except Exception:
                consts.HTTP_LOGGER.exception(f"error while finding error code")

        return return_value

    def prettify(self) -> None:
        """
        Prints the message in a readable detailed format
        :return: None
        """
        print(f"## HTTP VERSION ##\n{consts.HTTP_VERSION.decode('utf-8')}\n## ERROR CODE ##\n" +
              f"{self.error_code.decode('utf-8')}\n## HEADERS ##\n{self.__build_headers_bytes().decode('utf-8')}\n" +
              f"## BODY ##\n{self.body.decode('utf-8')}")

    def __build_headers_bytes(self) -> bytes:
        """
        Formats the headers into bytes
        :return bytes: Byte string with the headers formatted
        """
        headers = b""
        if self.headers.items():
            for key, value in self.headers.items():
                headers += key.title().replace(b'_', b'-') + b": " + value + consts.HEADER_SEPERATOR
        else:
            consts.HTTP_LOGGER.debug("no headers found")

        return headers

    def build_message_bytes(self) -> bytes:
        """
        Builds the http_ophir message
        :return bytes: The http_ophir message
        """
        headers = self.__build_headers_bytes()
        return consts.HTTP_VERSION + b" " + self.error_code + consts.HEADER_SEPERATOR + headers + \
            consts.HEADER_SEPERATOR + self.body

    def __str__(self) -> str:
        """
        Str dunder function for the HttpMsg class
        :return str: The http_ophir message in full
        """
        return self.build_message_bytes().decode('utf-8')


def auto_test_http_message() -> None:
    """
    Auto test for the HttpMsg class
    :return: None
    """
    http_request_example = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello"
    http_message_test = HttpMsg(body=b"hello", content_type=consts.MIME_TYPES[".txt"])

    assert http_message_test.build_message_bytes() == http_request_example
    assert http_message_test.headers == {b'content_type': b'text/plain', b'content_length': b'5'}
    assert str(http_message_test) == http_request_example.decode()
    assert http_message_test.body == b"hello"
    assert http_message_test.error_code == b"200 OK"
