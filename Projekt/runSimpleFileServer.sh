#!/bin/bash

binOpenssl=$(which openssl)
binPython3=$(which python3)

echo "================================================"
echo "     Init. WebService: SimpleFileServer         "
echo "------------------------------------------------"

if [[ ! -f "key.pem" && ! -f "cert.pem" ]]; then
    echo "Create self signed certificates: key.pem and cert.pem."
${binOpenssl} req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes << EOF
DE
Berlin
Berlin
Simple File Server Python
Developer
localhost
info@do-not-replay.com
EOF
else
    echo "Found: key.pem and cert.pem"
fi

if [[ ! -f "dhparam.pem" ]]; then
    echo "With CPU: Intel i7 4790K - generate time ca. 1 Minute"
    echo "Create file 'dhparam.pem'"
    ${binOpenssl} dhparam -out dhparam.pem 2048
else
    echo "Found: dhparam.pem"
fi

if [[ ! -d "wwwdata" ]]; then
    echo "Create the wwwdata directory"
    mkdir ./wwwdata
else
    echo "Found: Directory-> wwwdata"
fi

if [[ ! -d "wwwdata/userdata" ]]; then
    echo "Create User download and upload directory"
    mkdir ./wwwdata/userdata
else
    echo "Found: Directory-> wwwdata/userdata"
fi

ipAddress=$( ip a s | grep -i 'inet ' | grep -v '127.0.' | awk '{print $2}' | cut -sd '/' -f1 )
if [[ -z $( grep -E "${ipAddress}.*localhost" /etc/hosts ) ]]; then
    echo "ToDo: with root rights add this line to the '/etc/hosts' file."
    echo "${ipAddress} localhost >> /etc/hosts"
    exit 1
else
    echo "Found: '${ipAddress} localhost' in '/etc/hosts'"
fi

echo "------------------------------------------------"
echo "     Init. done.                                "
echo "================================================"
echo ""

${binPython3} ./server.py
