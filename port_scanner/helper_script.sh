IP_LIST=(
        172.20.0.10
        172.20.0.11
        172.20.0.20
        172.20.0.21
        172.20.0.20
        172.20.0.30
        172.20.0.40
)

PORT_RANGE="1-10000"
MAX_THREAD_COUNT="200"
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
