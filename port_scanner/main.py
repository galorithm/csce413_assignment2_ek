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
import concurrent.futures
from enum import Enum
import time

class PortInfo:
    class Status(Enum):
        CLOSED = 0
        OPEN = 1

    def __init__(self, port):
        self.port = port
        self.status = self.Status.CLOSED.value
        self.banner = None
        self.time_ms = None

def recv_banner(s):
    """
    Try to receive a banner from the connected server.

    Call this just after successfully connecting the socket.

    Args:
       s (socket object) - socket connected to server

    Returns
       banner string (max 1024 bytes) from the server, None
       if was unable to receive any.

       Doesn't throw an exception
    """
    banner = None
    try:
        # Covers services such as ssh, mysql which send us data
        banner = s.recv(1024).decode('utf-8', errors = 'ignore')
    except:
        # catch the exception, don't let it terminate the function
        pass

    if banner:
        return banner

    # Server didn't send any banner by himself, try HTTP maybe ?
    try:
        s.sendall(b"GET / HTTP/1.1\r\n"
                  b"Host: eshanvm\r\n"
                  b"\r\n")
        banner = s.recv(1024).decode('utf-8', errors= 'ignore')
    except:
        # catch the exception, don't let it terminate the app/function
        pass

    return banner


def scan_port(host, port, timeout):
    """
    Scan a single port on the target host

    Args:
        host (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: PortInfo object if port is open, None otherwise
    """
    port_info = PortInfo(port)

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

        start_time = time.perf_counter();
        # TODO: Try to connect to target:port
        s.connect((host, port))
        end_time = time.perf_counter();
        port_info.time_ms = (end_time - start_time) * 1000

        # connection successful
        port_info.status = PortInfo.Status.OPEN.value

        port_info.banner = recv_banner(s)

        try:
            s.close()
        except:
            # Don't let this close failure lead to False return
            # as successful connect means port is open so even if
            # close fails, we should return true and not false
            pass

        # TODO: Return True if connection successful
        return port_info

    except (socket.timeout, ConnectionRefusedError, OSError):
        return None


def scan_range(host, start_port, end_port, timeout = 1.0, max_threads = 1):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of PortInfo objects containing info about open ports,
    """
    open_port_info_arr = []

    print(f"[*] Scanning {host} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    with concurrent.futures.ThreadPoolExecutor(max_workers = max_threads) as executor:
        # Submit/schedule all jobs right now, the thread pool mangaer
        # (i.e. executor) will take care of ensuring there are max max_threads
        # running at a time to handle different jobs
        future_port_map = {}
        for port in range(start_port, end_port + 1):
            # scheduling scan_port(host, port, timeout)
            future = executor.submit(scan_port, host, port, timeout)
            future_port_map[future] = port

        # This is a blocking loop !, will block till all futures report
        # completion (or failure/exception)
        for future in concurrent.futures.as_completed(future_port_map):
            port = future_port_map[future]

            try:
                port_info = future.result()
                if port_info:
                    open_port_info_arr.append(port_info)
            except Exception as err:
                print(f"future for port {port} reported exception {err} !")
                pass

    return open_port_info_arr

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

    cli_arg_parser.add_argument(
            "--threads",
            default = "1",
            help = "max thread count to query ports concurrently"
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

        if not (start_port >= 0 and
                end_port <= 65535 and
                start_port <= end_port):
            raise ValueError

    except Exception:
        print(f"[!] Bad port range: {cli_args.ports}")
        sys.exit(1)

    # Parse the timeout argument
    try:
        timeout = float(cli_args.timeout)
        if (timeout <= 0): raise ValueError
    except Exception:
        print(f"[!] Bad timeout: {cli_args.timeout}")
        sys.exit(1)

    # Parse the threads argument
    try:
        max_threads = int(cli_args.threads)
        if (max_threads < 0): raise ValueError
    except Exception:
        print(f"[!] Bad max thread count: {cli_args.threads}")
        sys.exit(1)

    # Iterate over hosts to scan them
    for host in hosts:
        print(f"[*] Starting port scan on {host}")

        open_port_info_arr = []
        open_port_info_arr = scan_range(host, start_port, end_port, timeout, max_threads)
        print(f"\n[+] Scan complete!")
        print(f"[+] Found {len(open_port_info_arr)} open ports:")

        for port_info in open_port_info_arr:
            print(f"    Port {port_info.port}: open, "
                  f"time to connect: {port_info.time_ms} ms", end = '')
            if port_info.banner:
                print(f", banner: {port_info.banner}")

            print()

if __name__ == "__main__":
    main()
