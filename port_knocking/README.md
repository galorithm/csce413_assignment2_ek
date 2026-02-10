## Port Knocking Starter Template

This directory is a starter template for the port knocking portion of the assignment.

### What you need to implement
- Pick a protected service/port (default is 2222).
- Define a knock sequence (e.g., 1234, 5678, 9012).
- Implement a server that listens for knocks and validates the sequence.
- Open the protected port only after a valid sequence.
- Add timing constraints and reset on incorrect sequences.
- Implement a client to send the knock sequence.

### Getting started
1. Implement your server logic in `knock_server.py`.
2. Implement your client logic in `knock_client.py`.
3. Update `demo.sh` to demonstrate your flow.
4. Run from the repo root with `docker compose up port_knocking`.

### Example usage
```bash
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012
```


### Design decisions:

1. (Via Dockerfile) A docker container `port_knocking` (ip 172.20.0.40) runs the SSH service on port 2222 along with the `knock_server.py` (the port to protect and knock order can be modified by the CLI but I use the default port and order for this setup)

2. `knock_client.py` can be used by a client to knock on the 172.20.0.40 (target configurable via CLI) and knock on the knock server in the desired port order.

3. Once the knock client knocks in the correct sequence within a timeframe (10s by default, can be specified to knock server via CLI), the port is opened for the client after which it can access it.

### Server Implementation:

1. The docker container port knocking on startup starts an sshd server on port 2222 and starts the `knock_server.py`

2. The `knock_server.py` first uses iptables command (via subprocess.run) to add a firewall rule to drop all incoming packets to port 2222 (configurable via CLI) so that no one can access it.

3. Then, the knock server starts UDP servers on the ports present in the correct knock sequence to listen for knocks on them.

4. The knock server maintains a `client_state_map` to map state for each client (client’s ip used as a key to map to its state).

5. A client’s state contains information about:
- where the client is in the knock sequence (i.e. which index starting from 0) and
- the time at which it last knocked

4. Using select (i.e. polling), it waits on the UDP servers for knocks. When any of those UDP servers receives a knock (i.e. technically data), it updates the client state for the client which sent the knock.

5. Updating the client state may mean:
- resetting it to start state (new client or knock timeout expired or wrong knock based on sequence) at index 0, or
- progressing it to the next state in sequence (index++) if the knocked port was the correct knock based on the expected sequence, or
- providing it access to the port (if the client’s knocks were in proper sequence in proper time)

6. If the client completed its knock in correct sequence within the max timeout window, then the a firewall rule is added which allows that particular client to access the protected port.

### Client Implementation:

1. Client (`knock_client.py`) takes a sequence of ports to knock via CLI argument
2. For each port in that sequence, the client opens a UDP client socket and sends the request to the knoc server for that port


