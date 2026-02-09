#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import subprocess
import select

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(protected_port, client_ip):
    """Open the protected port using firewall rules for client_ip."""
    logging.info(f"Trying to open firewall for port {protected_port} "
                 f"for client {client_ip}")

    try:
        iptables_cmd = [
                # INPUT 1 to insert rule at top of input chain
                # (first in precendence)
                "iptables", "-I", "INPUT", "1",
                            "-p", "tcp", # for tcp connections
                            "-s", client_ip, # with source ip = client ip
                            "--dport", f"{protected_port}", # destination port
                            "-j", "ACCEPT" #  action to take: ACCEPT connection
                ]

        # True: raise exception if subprocess error code indicates failure
        subprocess.run(iptables_cmd, check = True)

        logging.info(f"Opened firewall for port {protected_port} "
                     f"for client {client_ip}")
    except Exception as err:
        logging.error(f"Failed to open firewall port for port {protected_port}, "
                      f"for client {client_ip}: "
                      f"{err}")

def close_protected_port(protected_port, client_ip):
    """Close the protected port using firewall rules."""
    logging.info(f"Trying to close firewall for port {protected_port} "
                 f"for client {client_ip}")

    try:
        # This rule is to delete (-D) the INPUT rule specified while
        # opening the protected port for the client in open_protected_port()
        iptables_cmd = [
                "iptables", "-D", "INPUT",
                            "-p", "tcp",
                            "-s", client_ip,
                            "--dport", f"{protected_port}",
                            "-j", "ACCEPT"
                            ]

        # check True to raise exceptions if the subprocess return
        # code indicates failure
        subprocess.run(iptables_cmd, check = True)

        logging.info(f"Opened firewall for port {protected_port} "
                     f"for client {client_ip}")
    except Exception as err:
        logging.error(f"Failed to close firewall port for port {protected_port}, "
                      f"for client {client_ip}: "
                      f"{err}")

# Get a knock server binded to the recevied port
def get_knock_server_socket(port):
    # (IPV4 + UDP) knock server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # listen for connections on any interface for that port
    s.bind(("0.0.0.0", port))

    # operate in non blocking mode - we'll use select to wait instead of
    # blocking on recv()
    s.setblocking(False)

    return s

# Reset the client state to indicate that the current knock is the client's
# first knock in the knock sequence.
#
# In case no client state exists, the state will get added for the client.
def reset_client_state(client_state_map, client_ip):
    client_state_map[client_ip] = (0, time.time())

# Handle client_ip's knock on knocked_port
# and update client_state_map based on sequence, window_seconds
# and if the client has completed knock sequence successfully in
# time (based on window_seconds) then open the firewall's protected_port
# for this particular client
def handle_client_knock(*, client_state_map,
                        knocked_port, client_ip,
                        sequence, window_seconds, protected_port):
    logging.info(f"Received a knock on port {knocked_port} from client {client_ip}")

    if client_ip not in client_state_map:
        # Client has never knocked before, add a default state for it
        reset_client_state(client_state_map, client_ip)

    knock_index, last_knock_time = client_state_map[client_ip]
    if time.time() - last_knock_time > window_seconds:
        # knock time window has expired, client took too long between
        # the last knock and this knock, reset his state so that the
        # further analysis believes that this is his first valid knock
        knock_index = 0

    expected_port = sequence[knock_index]
    if knocked_port != expected_port:
        reset_client_state(client_state_map, client_ip)
        return

    knock_index += 1
    if knock_index == len(sequence):
        logging.info(f"Client {client_ip} knocked complete sequence correctly "
                     "in time")
        open_protected_port(protected_port, client_ip)

        reset_client_state(client_state_map, client_ip)
    else:
        # Update the client's stored tate 
        client_state_map[client_ip] = (knock_index, time.time())

def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # Create UDP or TCP listeners for each knock port.
    knock_server_sockets = []
    for port in sequence:
        s = get_knock_server_socket(port)
        knock_server_sockets.append(s)
        logger.info(f"UDP knock server listening on port: {port}")

    # Map to track state of all knocking clients
    client_state_map = {}

    while True:

        # select returns:
        # rsockets, wsockets, xsockets
        #
        # we just care about rsockets
        ready_sockets, _, _ = select.select(
                knock_server_sockets, # wait for read on this list
                [], # wait for write on this list
                [], # wait for exception on this list
                1   # timeout
                )

        for s in ready_sockets:
            # Get the client's ip based on request
            data, client_addr = s.recvfrom(1024)
            client_ip = client_addr[0] # addr of form (ip, port)

            # Get the port of the server which received the knock
            server_addr = s.getsockname()
            knocked_port = server_addr[1] # addr of form (ip, port)

            handle_client_knock(
                    client_state_map = client_state_map,
                    knocked_port = knocked_port, client_ip = client_ip,
                    sequence = sequence,
                    window_seconds = window_seconds,
                    protected_port = protected_port
                    )

def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
