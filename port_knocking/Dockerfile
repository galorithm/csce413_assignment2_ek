FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends iptables iproute2 \
    && apt-get install -y openssh-server \
    && rm -rf /var/lib/apt/lists/*

# ssh service related settings
RUN mkdir -p /var/run/sshd
EXPOSE 2222

COPY knock_server.py knock_client.py ./
COPY start_sshd_and_knock_server.sh ./

RUN chmod +x ./start_sshd_and_knock_server.sh

CMD ["./start_sshd_and_knock_server.sh"]
