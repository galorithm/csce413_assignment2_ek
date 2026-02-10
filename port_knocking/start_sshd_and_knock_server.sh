#!/bin/bash

echo "Starting sshd as a background process"
/usr/sbin/sshd -D -p 2222 &

echo "Starting the knock server"
python3 knock_server.py


