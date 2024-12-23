from webserver import WebServer

# change this IP-Address if it not only local.
webServerIpAddress = "127.0.0.1"

# Change to your favourite port.
webServerPort = 8443

# Create a new object from my own created class.
webService = WebServer( webServerIpAddress, webServerPort )

while True:
    # Listen for incoming connections, again..again or it is Ctrl+C hitting!
    if webService.listen() == 3:
        break

# Destroy the created class to save the memory from usedspace of the object.
del webService


