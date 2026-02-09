#!/usr/bin/env python3
"""Starter template for the honeypot assignment."""

import logging
import os
import time
import socket
import urllib.parse

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
    # request_data is the data returned by recv called on socket
    # connected to the client
    def __init__(self, client_ip, client_port, request_data):
        self.client_ip = client_ip
        self.client_port = client_port

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

# return a 404 not found response
def page_not_found_404_response(request_info):
    response_body = """
        <html>
            <head><title>404 Not Found</title></head>
            <body>
                <h1>404 Not Found</h1>
                <p>The requested URL {0} was not found on this server.</p>
            </body>
        </html>
        """.format(request_info.path)  # Dynamic path in the message

    response_header = """
        HTTP/1.1 404 Not Found\r\n
        Server: Apache/2.4.66 (Ubuntu)\r\n
        Content-Type: text/html; charset=UTF-8\r\n
        Content-Length: {0}\r\n
        Connection: close\r\n
        """.format(len(response_body))


    response_str = (f"{response_header}"
                     "\r\n"
                    f"{response_body}")
    return response_str.encode()

# If path is /file?path=resume.txt serve the resume file,
# else 404 not found
def dummy_file_response(request_info):
    # Parse the query string to extract the path parameter
    query_str = urllib.parse.urlparse(request_info.path).query
    query_params = urllib.parse.parse_qs(query_str)

    # Check if path exists in the query string and if it's resume.txt
    if not ('path' in query_params and query_params['path'][0] == 'resume.txt'):
        return page_not_found_404_response(request_info)

    resume_data = """
    Name: Eshan
    Email: hibyegoodbye@tamu.edu
    Phone: 420420420420
    Education: Bachelor's in Computer Science
    Skills: Programming
    """

    response_header = ("HTTP/1.1 200 OK\r\n"
                       "Server: Apache/2.4.66 (Ubuntu)\r\n"
                       "Content-Type: text/plain\r\n"
                       f"Content-Length: {len(resume_data)}\r\n"
                       "Connection: close\r\n")

    response_str = (f"{response_header}"
                     "\r\n"
                     f"{resume_data}")
    return response_str.encode()

# Return a dummy response based on the received
# RequestInfo object
def dummy_response(request_info):
    body_content = None
    if request_info.path == "/" or request_info.path.startswith("/home"):
        body_content = (
                "Home Page of Eshan's personal website"
                )
    elif request_info.path.startswith("/contact"):
        body_content = (
                "Phone number: 420420420420 <br/>"
                "Address: Ujjain <br/>"
                "Email: hibyegoodbye@tamu.edu<br/>"
                )
    elif request_info.path.startswith("/file"):
        return dummy_file_response(request_info)
    else:
        return page_not_found_404_response(request_info)

    response_body = ("<html>"
                       "<body>"
                        f"{body_content}"
                       "</body>"
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

# Based on request info, detect and log attacks
def detect_and_log_attacks(request_info):
    if not request_info.path.startswith("/file"):
        return

    # The file end point may be vulnerable to directory traversal
    # attack, see if attacker tries to do that
    query_str = urllib.parse.urlparse(request_info.path).query
    query_params = urllib.parse.parse_qs(query_str)

    if not ('path' in query_params):
        return page_not_found_404_response(request_info)

    file_path = query_params["path"][0]
    if ".." in file_path:
        logger = logging.getLogger("Honeypot")
        logger.warning(
                f"[ATTACK ??] Potential DIRECTORY TRAVERSAL: from "
                f"client {request_info.client_ip}:{request_info.client_port}"
                f" for file {file_path} via end point {request_info.path}")

# Handle a request received from the client
def handle_client(client_connected_sock, client_addr):
    logger = logging.getLogger("Honeypot")
    client_ip = client_addr[0]
    client_port = client_addr[1]

    logger.info(f"[REQUEST] from client ip={client_ip}:{client_port} ")
    start_time = time.time()

    try:
        request_data = client_connected_sock.recv(4096)
        request_info = RequestInfo(client_ip, client_port, request_data)

        logger.info(f"  Method: {request_info.method}")
        logger.info(f"  Path: {request_info.path}")
        logger.info(f"  Header: \n{request_info.header}")
        if request_info.body: logger.info(f"  Body: \n{request_info.body}")

        detect_and_log_attacks(request_info)

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
