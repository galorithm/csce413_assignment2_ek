# Honeypot Analysis

## Summary of Observed Attacks

First, start the honeypot using: `docker compose up honeypot –build`

Then, from another terminal, use curl to access the honeypot (via Dockerfile, I have exposed port 8080 on host which forwards traffic to container’s 80 port where the honeypot listens) with directory traversal attack: `curl http://localhost:8080/file?path=../resume.txt`

An example of a capture on doing so is shown below:
```
2026-02-09 23:53:24,706 - INFO - [REQUEST] from client ip=172.20.0.1:35924
2026-02-09 23:53:24,706 - INFO -   Method: GET
2026-02-09 23:53:24,706 - INFO -   Path: /file?path=../resume.txt
2026-02-09 23:53:24,707 - INFO -   Header:
GET /file?path=../resume.txt HTTP/1.1^M
Host: localhost:8080^M
User-Agent: curl/8.5.0^M
Accept: */*
2026-02-09 23:53:24,707 - WARNING - [ATTACK ??] Potential DIRECTORY TRAVERSAL: from client 172.20.0.1:35924 for file ../resume.txt via end point /file?path=../resume.txt
2026-02-09 23:53:24,708 - INFO - [DISCONNECT] from client ip=172.20.0.1:35924, time stayed connected: 0.0014979839324951172
```

### Recommendations

One can search through the logs for ATTACK to find all occurrences of potential attacks by malicious clients.

