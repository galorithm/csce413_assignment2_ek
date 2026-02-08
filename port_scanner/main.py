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
import ipaddress

def scan_port(host, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        host (str): IP address or hostname to scan
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
        s.connect((host, port))

        # TODO: Close the socket
        s.close()

        # TODO: Return True if connection successful
        return True

    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_range(host, start_port, end_port):
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

    print(f"[*] Scanning {host} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    for port in range(start_port, end_port + 1):
        # TODO: Scan this port
        rc = scan_port(host, port)

        # TODO: If open, add to open_ports list
        if (rc):
            open_ports.append(port)

            # TODO: Print progress (optional)

    return open_ports

# Take the target ip and return a list of ips denoting all the hosts
# that the received ip represents.
#
# - in case of ip like 192.168.9.10, its a single ip so an array
#   consisting of 1 ip would be returned
#
# - in case of ip like 192.168.10.0/24 it denotes a subnet containing
#   256 hosts with subnet mask 192.168.10.0, so an array consisting of
#   all ips with that subnet mask would be returned.
#
# - raises ValueError if the specified ip_str is invalid, e.g
#   192.186.10.0/8 is invalid mask as a valid 8 bit mask would have
#   been 192.0.0.0
def hosts_from_target_ip(target):
    net = ipaddress.ip_network(target)
    return [str(ip) for ip in net.hosts()]

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
            default = "1-1024",
            help = 'range of ports to scan (default is 1 to 1024)'
            )

    cli_arg_parser.add_argument(
            "--timeout",
            default = "1",
            help = "timeout to wait for connection to each port"
            )

    cli_args = cli_arg_parser.parse_args();

    # Parse the --target argument
    target = cli_args.target
    try:
        hosts = hosts_from_target_ip(target)
    except ValueError:
        print(f"[!] Bad target specification")
        sys.exit(1)

    # Parse the --ports argument (by default 1-1024)
    try:
        split_ports_str = cli_args.ports.split("-")
        start_port = int(split_ports_str[0])
        end_port = int(split_ports_str[1])

        if not (start_port >= 1 and
                end_port <= 65535 and
                start_port <= end_port):
            raise ValueError

    except Exception:
        print(f"[!] Bad port range: {cli_args.ports}")
        sys.exit(1)

    # Parse the timeout argument
    try:
        timeout = float(cli_args.timeout)
        if (timeout <= 0):
            raise ValueError
    except Exception:
        print(f"[!] Bad timeout: {cli_args.timeout}")
        sys.exit(1)

    for host in hosts:
        print(f"[*] Starting port scan on {host}")

        open_ports = []
        open_ports = scan_range(host, start_port, end_port)
        print(f"\n[+] Scan complete!")
        print(f"[+] Found {len(open_ports)} open ports:")

        for port in open_ports:
            print(f"    Port {port}: open")


if __name__ == "__main__":
    main()
