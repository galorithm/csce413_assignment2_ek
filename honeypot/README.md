### Honeypot Design

1. An HTTP server honeypot.py which logs to a honeypot/logs/honeypot.log file

2. The honeypot server is running on port 80 on the honeypot container, however to the host it is exposed against 8080

3. After startup, the honeypot bind a listening socket to port 80 on 0.0.0.0 ip

4. On receiving a client’s request, the honeypot:
  - logs the client details
  - parses the HTTP request and then logs its details (stored in a RequestInfo class object)
  - /home or / end point exposed to return html indicating its my home page
  - /contact end point exposed to return html containing my contact details
  - /file?path=example.txt end point exposed to return file contents (only /file?path=resume.txt supported to return response containing my resume data)
  - For other end points the honeypot returns a 404 not found response

5. The honeypot is capable of detecting potential directory traversal attacks by monitoring what path user specifies in their `/file?path=<path here>` request. If the path contains .., the honeypot logs it as a warning inside the log file.

6. After sending response to the client, honeypot disconnects from it and logs the disconnection.



