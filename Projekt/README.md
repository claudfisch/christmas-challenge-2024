# Documentation

## Overview of the made work
[-] File management: The server should support basic file storage and retrieval. (Download/Upload works but moving around not.)
[-] Authentication: Provide options for protected and unprotected files. (Usersystem was planned but not enough time - only guest user)
[x] Encryption: Include functionality to encrypt and decrypt files during storage (PLAIN-TEXT) or transfer (SAVE SSL-TLS)
[x] Access: The file server should be accessible via a web application that runs on a Linux server.

## 1. How to setup my project
The bash-script 'runSimpleFileServer.sh' made it executeable with "chmod u+x ./*.sh"
- key.pam and cert.pam (Self-Signed-Certificates) will be created. ( Should be edited if you do not want German DE Berlin in the Certificate )
- Also dhparam.pem will be created. 
- Directory structure will be created if they not exists: ./wwwdata/userdata
- IP-Address is displayed and it should be in the '/etc/hosts' file at the end write down AND also write it down into the file: server.py.
- Is all above positiv than the 'server.py' will be executed if python3 is installed.

## 2. Python script list
- server.py ( Should do the task to run each service like 'WebServer' and other but I do not have enough time for it )
- webserver.py ( Here is my complete Web-Server-Service with SSL-Encryption, Upload-File, Download-File, Single-User-Guest (no time for cookies) )
- filesytem.py ( Aktion about create, delete, modify or update a file and directory but some action could not placed here like Upload/Download )

## 3. URL Paths
In the address bar of your webbrowser type https://your-ip-address:8443 if you have not changed it in server.py!

- / : (GET) Main page where Signup or list directory with a hyperlink reachable
- /favicon.ico : (GET) show only the image was placed into the folder "./wwwdata/images/favicon\_server\_32x32.ico"
- /list : (GET) Show current files and directories but directories could not entered, not yet. Single upload of a file and download works. But a little bit is not correct, yet.
- /signup : (GET) Here should new user created but they are not stored, yet.
- /register : (POST) From /signup jumps into this and the creation magic should begin but it is only a possitive message displayed.
- /signin : (GET) Is empty and with a pass declared
- /logout : (GET) Is empty, too.
- /download : (POST) Choose a file and hit the download button.
- /upload: (POST) Choose a file from your device and it the upload button.

## 4. Here is the list of all my imports for my python project
Python default imports
- from enum import Enum
- from os.path import exists
- from socket import socket, AF\_INET, SOCK\_STREAM
- from ssl import SSLContext, PROTOCOL\_TLS\_SERVER, OP\_NO\_TLSv1, OP\_NO\_TLSv1\_1, OP\_NO\_SSLv2, OP\_NO_SSLv3

Python own class imports
- from webserver import WebServer
- from filesystem import Filesystem

## 5. Conclusion
I have a lot of fun for this programming project. A little bit short but I entered it to late.
My first directory was created at "Monday, 16. December 2024 15:03:01 CET".
It should be a challange for me because I use only base python bibliotheks without create a python-enviroment and without pip install anything.
That this can be run on the fly.

My half clean code comes later.
Bye.

