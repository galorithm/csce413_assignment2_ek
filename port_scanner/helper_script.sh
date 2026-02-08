# List of ips to scan ports for (selected based
# on the docker-compose.yml file)
IP_LIST=(
        172.20.0.10
        172.20.0.11
        172.20.0.20
        172.20.0.21
        172.20.0.22
        172.20.0.30
        172.20.0.40
)

PORT_RANGE="0-65535"
MAX_THREAD_COUNT="400"
MAX_TIMEOUT="0.2"

for IP in "${IP_LIST[@]}"; do
    echo "=============================="
    echo "[*] Scanning $ip"
    echo "=============================="

    python3 ./main.py \
        --target "$IP" \
        --ports "$PORT_RANGE" \
        --threads "$MAX_THREAD_COUNT" \
        --timeout "$MAX_TIMEOUT"
    echo
done
