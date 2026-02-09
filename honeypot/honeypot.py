#!/usr/bin/env python3
"""Starter template for the honeypot assignment."""

import logging
import os
import time
import socket

LOG_PATH = "/app/logs/honeypot.log"


def setup_logging():
    os.makedirs("/app/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )


def run_honeypot():
    logger = logging.getLogger("Honeypot")
    logger.info("Honeypot starter template running.")
    logger.info("TODO: Implement protocol simulation, logging, and alerting.")

    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # When restarted let it bind immediately instead of waiting on the
    # TIME_WAIT state (easier to demo/debug after server close/start)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    listen_sock.bind(("0.0.0.0", 80))
    listen_sock.listen()

    while True:
        client_connected_sock, client_addr = listen_sock.accept()
        handle_client(client_connected_sock, client_addr)

# Class to represent a received http request
class RequestInfo:
    def __init__(self, request_data):
        self.raw_data = request_data
        self.data = request_data.decode(errors = 'ignore');

        self.method = self._method_from_data()
        self.path = self._path_from_data()

        self.header = self._header_from_data()
        self.body = self._body_from_data()

    def _method_from_data(self):
        first_line = self.data.splitlines()[0]
        method = first_line.split()[0]
        return method

    def _path_from_data(self):
        first_line = self.data.splitlines()[0]
        path = first_line.split()[1]
        return path

    def _header_from_data(self):
        # split at most 1 time
        split_header_and_body = self.data.split("\r\n\r\n", 1)
        return split_header_and_body[0]

    def _body_from_data(self):
        # split at most 1 time
        split_header_and_body = self.data.split("\r\n\r\n", 1)
        if len(split_header_and_body) > 1:
            return split_header_and_body[1]
        else:
            # It is valid for body to be empty
            return ""

# Return a dummy response based on the received
# RequestInfo object
def dummy_response(request_info):

    response_body = ("<html>"
                     "<body>Ujjain is the city of gods</body>"
                     "</html>")

    response_header = ("HTTP/1.1 200 OK\r\n"
                       "Server: Apache/2.4.66 (Ubuntu)\r\n"
                       "Content-Type: text/html\r\n"
                       f"Content-Length: {len(response_body)}\r\n"
                       "Connection: close\r\n")

    response_str = (f"{response_header}"
                     "\r\n"
                    f"{response_body}")
    return response_str.encode()

# Handle a request received from the client
def handle_client(client_connected_sock, client_addr):
    logger = logging.getLogger("Honeypot")
    client_ip = client_addr[0]
    client_port = client_addr[1]

    logger.info(f"[REQUEST] from client ip={client_ip}:{client_port} ")
    start_time = time.time()

    try:
        request_data = client_connected_sock.recv(4096)
        request_info = RequestInfo(request_data)

        logger.info(f"  Method: {request_info.method}")
        logger.info(f"  Path: {request_info.path}")
        logger.info(f"  Header: \n{request_info.header}")
        if request_info.body: logger.info(f"  Body: \n{request_info.body}")

        response = dummy_response(request_info)
        client_connected_sock.sendall(response)
    except Exception as err:
        logger.info(f"[EXCEPTION] while handling client "
                    f"{client_ip}:{client_port}, : {err}")
        raise
    finally:
        client_connected_sock.close()

        response_time = time.time() - start_time
        logger.info(f"[DISCONNECT] from client ip={client_ip}:{client_port}, "
                    f"time stayed connected: {response_time}")


if __name__ == "__main__":
    setup_logging()
    run_honeypot()
