#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import socket
import sys
import argparse

def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        # TODO: Create a socket

        # Assuming TCP (SOCK_STREAM) since most of the services I assume
        # the assignment wants me to scan are TCP based (SSH, HTTP), not
        # UDP
        #
        # AF_INET as the docker compose file's ips suggest that
        # IPV4 is being used and not IPV6
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO: Set timeout
        s.settimeout(timeout)

        # TODO: Try to connect to target:port
        s.connect((target, port))

        # TODO: Close the socket
        s.close()

        # TODO: Return True if connection successful
        return True

    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_range(target, start_port, end_port):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    for port in range(start_port, end_port + 1):
        # TODO: Scan this port
        rc = scan_port(target, port)

        # TODO: If open, add to open_ports list
        if (rc):
            open_ports.append(port)

            # TODO: Print progress (optional)

    return open_ports


def main():
    """Main function"""
    # TODO: Parse command-line arguments
    # TODO: Validate inputs
    # TODO: Call scan_range()
    # TODO: Display results

    cli_arg_parser = argparse.ArgumentParser(
            prog='port_scanner',
            description='scan a bunch of ports'
            )

    cli_arg_parser.add_argument(
            '--target',
            required = True,
            help = 'ip of the machine to scan ports for '
            )

    cli_arg_parser.add_argument(
            "--ports",
            default="1-1024",
            help = 'range of ports to scan (default is 1 to 1024)'
            )

    cli_args = cli_arg_parser.parse_args();

    # Parse the --target argument
    target = cli_args.target

    # Parse the --ports argument (by default 1-1024)
    try:
        split_ports_str = cli_args.ports.split("-")
        start_port = int(split_ports_str[0])
        end_port = int(split_ports_str[1])

        if not (start_port >= 1 and
                end_port <= 65535 and
                start_port <= end_port):
            raise ValueError

    except Exception as err:
        print(f"Bad port range: {cli_args.ports}")

    print(f"[*] Starting port scan on {target}")

    open_ports = scan_range(target, start_port, end_port)

    print(f"\n[+] Scan complete!")
    print(f"[+] Found {len(open_ports)} open ports:")
    for port in open_ports:
        print(f"    Port {port}: open")


if __name__ == "__main__":
    main()
