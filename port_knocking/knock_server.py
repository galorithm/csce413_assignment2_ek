#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import subprocess

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
                            "--dport", str(protected_port), # destination port
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

def close_protected_port(protected_port):
    """Close the protected port using firewall rules."""
    # TODO: Remove firewall rules for protected_port.
    logging.info("TODO: Close firewall for port %s", protected_port)


def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # TODO: Create UDP or TCP listeners for each knock port.
    # TODO: Track each source IP and its progress through the sequence.
    # TODO: Enforce timing window per sequence.
    # TODO: On correct sequence, call open_protected_port().
    # TODO: On incorrect sequence, reset progress.

    while True:
        time.sleep(1)


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
