"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: This is the app class. It will handle the webapp and the path.
"""
# Imports #
import socket
import time

import select
import http_lib.constants as consts
import logging
import re
import http_lib.http_parser
import os

# global vars #
global readable_socks_list, writeable_socks_list, exception_socks_list


class App:
    """The Base for the web app."""

    # ---------- Constructor ---------- #
    def __init__(self):
        """
        Constructor of class
        :return: None
        """
        self.routes = dict()
        self.four_o_four = consts.FOUR_O_FOUR
        self.__closed = False

    # ---------- Decorators ---------- #
    def route(self, route: bytes, permission_cookie: bytes = "None"):
        """
        Route decorator - adds the route to the routes' dictionary.
        :param permission_cookie: The cookie name that allows permission to page.
        :param route: the route for the uri
        :return: what the original function needs to return
        """

        def add_to_route_dict(original_function):
            """
            This is the decorator function
            :param original_function: original function that decorator decorates
            :return: what the original function needs to return
            """
            try:
                self.routes[route] = original_function, permission_cookie
            except TypeError:
                consts.HTTP_LOGGER.debug("routes is not initialized.")

            def wrapper_function(*args, **kwargs):
                """
                This is the wrapper function.
                """
                raise Exception("This is a route function. It cannot be run.")

            return wrapper_function

        return add_to_route_dict

    # ---------- Private functions ---------- #
    @staticmethod
    def __receive_message(client_socket: socket, client_addr: str) -> bool or http_lib.http_parser.HttpParser:
        """
        Receives a message from a client
        :param client_socket: The client socket
        :param client_addr: The client ip address
        :return bool or HttpParser: False if the message is invalid, HttpParser with the message
        """
        try:
            message = b""

            # Multiple receives to eliminate server blocking without too many requests with the timeout #
            time_start = time.time()
            while b"\r\n\r\n" not in message and time.time() - time_start < consts.RECV_TIMEOUT:
                msg = b""
                try:
                    client_socket.settimeout(.5)
                    msg = client_socket.recv(consts.RECV_LENGTH)
                except socket.timeout:
                    consts.HTTP_LOGGER.debug("Got timeout on socket receive")
                else:
                    consts.HTTP_LOGGER.debug("Success on socket receive.")

                if not msg:
                    continue
                message += msg

            try:
                content_length = int(re.search(rb'Content-Length: (\d+)', message).group(1))
                # Check if body was already received #
                if len(message.split(b'\r\n\r\n')) > 1 and len(message.split(b'\r\n\r\n')[1]) != content_length:
                    body = b''
                    # Receiving body #
                    while len(body) < content_length:
                        chunk = client_socket.recv(consts.RECV_LENGTH)
                        if not chunk:
                            logging.debug("Ended body receive")
                            break
                        body += chunk

                    message += body

            except AttributeError:
                consts.HTTP_LOGGER.debug("The message does not have Content-Length header")

            except Exception as e:
                consts.HTTP_LOGGER.exception(e)

            return http_lib.http_parser.HttpParser(message, client_addr)

        except Exception as e:
            consts.HTTP_LOGGER.exception(e)

    def __handle_client(self, request: http_lib.http_parser.HttpParser, client_socket: socket) -> None:
        """
        Handles the client input.
        :param request: The request that the server got.
        :param client_socket: The client socket.
        :return: None
        """
        response: http_lib.http_message

        if request is not None and request.URI is not None:
            if request.URI in self.routes.keys() and \
                    (self.routes[request.URI][1] == "None" or
                     (request.COOKIES and self.routes[request.URI][1] in request.COOKIES.keys())):
                response = self.routes[request.URI][0](request)

            elif not os.path.isfile(request.URI[1:].replace(b"%20", b" ")):
                with open(self.four_o_four, 'rb') as file:
                    response = http_lib.http_message.HttpMsg(error_code=404,
                                                           headers={"content_type": consts.MIME_TYPES[".html"]},
                                                           body=file.read())
            # If uri does not have a special path #
            else:
                # extract requested file type from URL (html, jpg etc)
                file_type = os.path.splitext(request.URI)[1]

                # generate proper HTTP header
                file_data: bytes
                with open(request.URI[1:].replace(b"%20", b" "), 'rb') as f:
                    file_data = f.read()
                response = http_lib.http_message.HttpMsg(headers={"content_type": consts.MIME_TYPES[file_type.decode()]},
                                                       body=file_data)

            consts.HTTP_LOGGER.info(f"Request to {request.URI} got response of {response.error_code}")
            client_socket.send(response.build_message_bytes())

    # ---------- Public functions ---------- #
    def set_four_o_four(self, route: str) -> None:
        """
        Sets the route to the 404 page.
        :param route: The route to the 404 page html.
        :return: None
        """
        if isinstance(route, str):
            self.four_o_four = route
        else:
            raise TypeError("Function must get a string that holds the route to the 404 html file")

    def close_app(self) -> None:
        """
        Shuts down the server and closes the server
        :return: None
        """
        self.__closed = True
        consts.HTTP_LOGGER.debug("Closing app.")

    def run(self, port=consts.PORT, host=consts.IP) -> None:
        """
        Starts the http server.
        :return: None
        """
        global readable_socks_list, writeable_socks_list, exception_socks_list

        # Setting up the socket #
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(.5)

        sock.bind((host, port))
        sock.listen()

        socket_list = {sock: host}

        try:
            while not self.__closed:
                readable_socks_list, writeable_socks_list, exception_socks_list = select.select(list(socket_list.keys()),
                                                                                                list(socket_list.keys()),
                                                                                                list(socket_list.keys()),
                                                                                                .1)
                for notified_socket in readable_socks_list:
                    if notified_socket == sock:  # checking for new connection #
                        consts.HTTP_LOGGER.debug("Getting new connection")
                        client_socket, client_addr = sock.accept()
                        logging.info(consts.NEW_CLIENT.format(client_addr[0], client_addr[1]))
                        client_socket.settimeout(.5)
                        socket_list[client_socket] = client_addr[0]  # Adding the socket to the connected clients #
                    else:
                        try:
                            consts.HTTP_LOGGER.debug("Starting receive")
                            message: http_lib.http_parser.HttpParser = self.__receive_message(notified_socket,
                                                                                              socket_list[notified_socket])
                            consts.HTTP_LOGGER.info(b"Got Request: " + message.URI if message.URI else "None")
                            self.__handle_client(message, notified_socket)

                        except Exception as e:
                            consts.HTTP_LOGGER.exception(e)

                        finally:
                            notified_socket.close()
                            del socket_list[notified_socket]
        finally:
            consts.HTTP_LOGGER.debug("Closing main socket.")
            sock.close()
            consts.HTTP_LOGGER.debug("Main socket closed.")

