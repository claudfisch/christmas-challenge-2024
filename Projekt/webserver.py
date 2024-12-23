# python default imports
from enum import Enum
from os.path import exists as osPathExists
from socket import socket, AF_INET, SOCK_STREAM
from ssl import SSLContext, PROTOCOL_TLS_SERVER, OP_NO_TLSv1, OP_NO_TLSv1_1, OP_NO_SSLv2, OP_NO_SSLv3

# my own python imports
from filesystem import Filesystem

class PostForm(Enum):
    USERNAME = 'txtUsername'
    PASSWORD = 'txtPassword'
    SUBMIT = 'btnSubmit'
    RESET = 'btnReset'
    DOWNLOAD = 'FilePath'
    UPLOAD = 'Filename'
    ENCTYPEMULTIPART = 'multipart/form-data'

class HtmlStatusCode(Enum):
    OK = "HTTP/1.1 200 OK\r\n"
    FORBIDDEN = "HTTP/1.1 403 Forbidden\r\n"
    NOTFOUND = "HTTP/1.1 404 Not Found\r\n"
    CONFLICT = "HTTP/1.1 409 Conflict\r\n"

class ContentType(Enum):
    OCTETSTREAM = 'application/octet-stream'
    # Image
    PNG = 'image/png'
    JPEG = 'image/jpeg'
    GIF = 'image/gif'
    SVG = 'image/svg+xml'
    WEBP = 'image/webp'
    # Audio
    MP3 = 'audio/mpeg'
    WAV = 'audio/wav'
    OGG = 'audio/ogg'
    # Video
    MP4 = 'video/mp4'
    WEBM = 'video/webm'
    # Document
    JS = 'application/x-javascript'
    JSON = 'application/json'
    TXT = 'text/plain'
    PDF = 'application/pdf'
    XML = 'application/xml'
    # Archive
    ZIP = 'application/zip'
    GZIP = 'application/gzip'

class WebServer:
    def __init__( self, paramHost: str, paramPort: int, paramCert: str = "cert.pem", paramKey: str = "key.pem", paramDH: str = "dhparam.pem" ):
        print("Run WebServer")
        # init filesystem
        self.filesystemService = Filesystem()

        # Needed for redirect method <meta ... refresh... />
        # Security risk if they fished from the HTML-Header from socket - it could manuipulated!
        self.host = paramHost
        self.port = paramPort

        # Standard Socket configuration
        self.webSocket = socket( AF_INET, SOCK_STREAM )
        self.webSocket.bind(( paramHost, paramPort ))
        self.webSocket.listen( 1 )

        # SSL Configuration
        self.sslContext = SSLContext( PROTOCOL_TLS_SERVER )
        self.sslContext.load_cert_chain( certfile=paramCert, keyfile=paramKey )

        # For a better security like a apache2-web-server
        if osPathExists( paramDH ):
            # Cipher Suites: Diffie-Hellman and Elliptic-Curve key transfer
            self.sslContext.set_ciphers( "ECDHE+AESGCM:ECDHE+CHACHA20:ECDHE+SHA256" )

            # Set ECDHE-Curve
            self.sslContext.set_ecdh_curve( "prime256v1" )

            # Diffie-Hellman
            self.sslContext.load_dh_params(paramDH)

            # disable unsecure protocols
            self.sslContext.options |= OP_NO_TLSv1
            self.sslContext.options |= OP_NO_TLSv1_1
            self.sslContext.options |= OP_NO_SSLv2
            self.sslContext.options |= OP_NO_SSLv3

        self.sslSocket = self.sslContext.wrap_socket( self.webSocket, server_side=True )

        # Web - Server favicon.ico filename with path
        self.favicon = 'images/favicon_server_32x32.ico'

        # Set chunk size ; Experiment with chunk sizes but result the same caos by the upload.
        self.chunkSize = 8192
        #self.chunkSize = 4096
        #self.chunkSize = 2048
        #self.chunkSize = 1024
        #self.chunkSize = 512
        #self.chunkSize = 256
        #self.chunkSize = 128

    def __del__( self ):
        print( "Close WebServer" )
        self.sslSocket.close()
        self.webSocket.close()

    def listen(self):
        try:
            clientSocket, clientAddress = self.sslSocket.accept()
        except KeyboardInterrupt:
            print( "Keyboard interrupt: Ctrl+C" )
            return 3
        except:
            return -1
        self.filterClientRequest( clientSocket )

    # Exapmle URL for headerfieldnames: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
    def getHeader( self, paramCode: HtmlStatusCode, paramType: str, paramLength: float ):
        headerContent = f"""Content-Type: {paramType}\r\nContent-Length: {paramLength}\r\n\r\n"""
        return f"""{paramCode.value}{headerContent}"""

        # Old code - not casecade able!
        #match paramCode:
        #    case 200:
        #        return f"""HTTP/1.1 200 OK\r\n{headerContent}"""
        #    case 403:
        #        return f"""HTTP/1.1 403 Forbidden\r\n{headerContent}"""

    def getHeaderDownloadFile( self, paramCode: HtmlStatusCode, paramType: str, paramLength: float, paramSourceFilePath: str ):
        # Default download header for a webserver
        headerContent = f"""Content-Type: {paramType}\r\nContent-Length: {paramLength}\r\nContent-Disposition: attachment; filename="{paramSourceFilePath.split( '/' )[ -1 ]}"\r\n\r\n"""
        return f"""{paramCode.value}{headerContent}"""

        # Old code - not casecade able! - write it twice is ugly
        #match paramCode:
        #    case 200:
        #        return f"""HTTP/1.1 200 OK\r\n{headerContent}"""
        #    case 403:
        #        return f"""HTTP/1.1 403 Forbidden\r\n{headerContent}"""

    def send( self, paramClientSocket: socket, paramCode: HtmlStatusCode, paramType: str, paramHtmlContent: str ):
        contentForClient = None
        match paramType:
            case 'image/x-icon':
                header = self.getHeader( paramCode, paramType, len( paramHtmlContent ) ).encode( 'utf-8' )
                # Create a bytearray to combine easiely the header with the image content.
                byteData = bytearray()
                byteData.extend( header )
                byteData.extend( paramHtmlContent )
                paramClientSocket.sendall( byteData )

            case 'text/html; charset=utf-8':
                header = self.getHeader( paramCode, paramType, len( paramHtmlContent.encode( 'utf-8' ) ) )
                contentForClient = f"""{header}{paramHtmlContent}""".encode( 'utf-8' )

        if contentForClient != None:
            paramClientSocket.sendall( contentForClient )

    def filterClientRequest( self, paramClientSocket: socket ):
        # The value must to 864 to get readable header data with a little bit of attached upload file.
        # That is compatible with decode utf-8 like PDF with 'UnicodeDecodeError: 'utf-8' codec can't decode byte 0x9c'.
        # I hope that is enough???
        request = paramClientSocket.recv( 864 ).decode( 'utf-8' )

        # Debugging output
        print( request )
        #return

        try:
            # This block is need if curl call the web-address is not enough data for split.
            # Example: curl -I -k [Protocol]://[IP]:[PORT]
            method, path, _ = request.splitlines()[ 0 ].split( " " )

            # Debugging output
            #print(method, path)
        except:
            print(f"Error: {repr( request )}")
            return -1

        if '?' in path:
            # If data is send by the path
            # Example Once-Data: ?key1=value1
            # Example More-Data: ?key1=value1&key2=value2

            path, urlParameters = path.split( '?' )
            if '&' in urlParameters:
                # Get a nice dictionary of all data in the path
                urlParameters = dict( nameEqualsValue.split( '=' ) for nameEqualsValue in urlParameters.split( '&' ) )

            elif '=' in urlParameters:
                # Get a nice dictionary of once data in the path
                urlParameters = dict( urlParameters.split( '=' ) )

        if method != 'GET' and method != 'POST':
            # Say forbidden if a wrong method is used!
            self.send( paramClientSocket, HtmlStatusCode.FORBIDDEN, "text/html; charset=utf-8", """<!DOCTYPE html><html lang="en"><body><b>Only GET-AND-POST-Requests allowed!</b><hr /></body></html>""" )
            return -1

        postData = None
        if method == 'POST':
            # Split header and body data for better information grabbing
            submitHeader, submitBody = request.split('\r\n\r\n', 1)

            if path != '/upload':
                # Get a nice dictionary of the input form that was given from the user
                postData = dict(nameEqualsValue.split('=') for nameEqualsValue in submitBody.split('&'))

        match path:
            case '/favicon.ico':
                # Debugging output
                # print( "Asking for favicon" )
                faviconImage = self.filesystemService.readFile( self.filesystemService.madeWorkPath( self.favicon ) )
                if type(faviconImage) != type(bool):
                    # Debugging output
                    #print( "Byte-Read: /favicon.ico" )
                    self.send( paramClientSocket, HtmlStatusCode.OK, "image/x-icon", faviconImage )

            case '/':
                self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html lang="en"><head><link rel="icon" type="image/x-icon" href="/favicon.ico"><title>SimpleFileServerPython</title></head><body><b>Welcome Guest</b><hr /><br /><a href='/list'>Show your files!</a><br /><br /><a href='/signup'>Sign Up</a></body></html>""" )
                return

            case '/signup':
                self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title></head><body><h2>Register a new User to the Simple File Server Python</h2><form action='/register' method='POST'>
                          <input type='text' name='{PostForm.USERNAME.value}' placeholder='{PostForm.USERNAME.name}' />
                          <input type='password' name='{PostForm.PASSWORD.value}' placeholder='{PostForm.PASSWORD.name}' />
                          <input type='submit' name='{PostForm.SUBMIT.value}' value='Register' />
                          <input type='reset' name='{PostForm.RESET.value}' value='Reset' />
                          </form><hr /><br /><pre>Form is disabled. The Submit-Button is not functional because it always is positiv message that a new user created.<br />But it is not the case! Sorry, for that -.-</pre></body></html>""" )
                return

            case '/register':
                # ToDo: not enough time to complete the functionallity
                if postData == None:
                    # Error - no user form data
                    self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title></head><body><h2>Signup could not complete an unknown error occured!</h2></body></html>""" )
                    print("Error: method POST")
                    return

                # Debugging output
                #print(postData)

                backToUrl = f"https://{self.host}:{self.port}"
                self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title><meta http-equiv='refresh' content='5;url={backToUrl}' /></head><body><h2>Signup successfull!</h2><pre>Page refresh in 5 seconds or click <a href='/list'>here</a>!</pre></body></html>""" )

            case '/signin':
                # ToDo: not enough time to implement
                pass

            case '/logout':
                # ToDo: not enough time to implement
                pass

            case '/list':
                userFilePath = self.filesystemService.madeUserPath("")
                FolderFiles = self.filesystemService.listDirectory( userFilePath )
                # Debugging output
                #print( FolderFiles )

                # Create all rows for folder and files.
                # But for time saveing only files
                tableData = ""
                for data in FolderFiles:
                    tableData += f"""<tr><td>{data[ "type" ]}</td><td>{data[ "name" ]}</td><td>{data[ "size" ]} KB</td><td>{data[ "creationDate" ]}</td><td>{data[ "modifiedDate" ]}</td><td><form action='/download' method='POST'><input type='hidden' name='{PostForm.DOWNLOAD.value}' value='{data[ "name" ]}' /><input type='submit' name='{PostForm.SUBMIT.value}' value='Download' /></form></td></tr>"""

                self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title></head><body><h2>Upload new file:</h2><form action='/upload' method='POST' enctype='{PostForm.ENCTYPEMULTIPART.value}'><input type='file' name='{PostForm.UPLOAD.value}' placeholder='File (*.*)' /><input type='submit' name='{PostForm.SUBMIT.value}' value='Upload' /></form><hr /><h2>List of files</h2><table border='1'><tr><th>Type</th><th>Name</th><th>Size</th><th>Creation Date</th><th>Modified Date</th></tr>{tableData}</table></body></html>""" )

            case '/download':
                if postData == None:
                    # Error - no download file selected
                    self.send( paramClientSocket, HtmlStatusCode.NOTFOUND, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title></head><body><h2>Download file not found!</h2></body></html>""" )
                    return
                self.downloadFile( paramClientSocket, postData[PostForm.DOWNLOAD.value])

            case '/upload':
                if self.uploadFile( paramClientSocket, submitHeader, submitBody ):
                    # Upload was positive
                    backToUrl = f"https://{self.host}:{self.port}/list"
                    self.send( paramClientSocket, HtmlStatusCode.OK, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title><meta http-equiv='refresh' content='5;url={backToUrl}' /></head><body><h2>Upload completed!</h2><pre>Page refresh in 5 seconds or click <a href='/list'>here</a>!</pre></body></html>""" )
                    return

                # Upload error
                self.send( paramClientSocket, HtmlStatusCode.NOTFOUND, "text/html; charset=utf-8", f"""<!DOCTYPE html><html><head><title>SimpleFileServerPython</title></head><body><h2>Upload file not found!</h2></body></html>""" )
                return

    def findContentOfHeader(self, paramHeader: str, paramSearch: str):
        # Find the right spot of the header response (request)?
        try:
            return [ headerResultLine.split( ": " )[ 1 ] for headerResultLine in paramHeader.split( "\r\n" ) if headerResultLine.startswith( paramSearch ) ][ 0 ]
        except:
            # If not found send nothing back
            return ""

    def downloadFile( self, paramClientSocket: socket, paramSourceFilePath: str ):
        # Set it to the right user directory
        userFilePath = self.filesystemService.madeUserPath( paramSourceFilePath )

        # Debugging output
        #print( f"User-Path: {userFilePath}" )

        if self.filesystemService.checkExists( userFilePath ) == False:
            # Do nothing if the file not exists
            print( "Error: File not found!" )
            return

        with open( userFilePath, 'rb' ) as downloadFileHanlder:
            # Create header, that the browser knows the total file size of the download
            downloadFileSize = self.filesystemService.getFileSize( userFilePath )
            if downloadFileSize == 0:
                # Filesize 0 no file to download
                print( "Error: Filesize is 0 bytes!" )
                return

            # Create the download header and send it to the client - How big the file is
            header = self.getHeaderDownloadFile( HtmlStatusCode.OK, ContentType.OCTETSTREAM.value, downloadFileSize, userFilePath )
            paramClientSocket.sendall( header.encode( 'utf-8' ) )

            # Read file as chunks
            # The operator := does set a value and give it out; both at same time. Nice :-)
            while chunk := downloadFileHanlder.read( self.chunkSize ):
                paramClientSocket.sendall( chunk )

    def uploadFile( self, paramClientSocket: socket, paramSubmitHeader: str, paramSubmitBody: str ):
        # ToDo: Upload works part-wise: File is too large as should be!

        # Filter filesize
        uploadFileLength = int( self.findContentOfHeader( paramSubmitHeader, "Content-Length" ) )

        try:
            # None textfiles need only 864 bytes. complicated. Symtome defense. Trial and error.
            # Like PDFs
            submitBoundaryHeader, submitBoundaryBody = paramSubmitBody.split('\r\n\r\n', 1)
        except:
            # Textfiles need 1024 bytes
            # receive the next 160 bytes for already 1024 bytes
            paramSubmitBody += paramClientSocket.recv( 160 ).decode( 'utf-8' )
            submitBoundaryHeader, submitBoundaryBody = paramSubmitBody.split('\r\n\r\n', 1)

        # Filter the filename and filetype - extensions check.
        uploadFilename = str( self.findContentOfHeader( submitBoundaryHeader, "Content-Disposition" ) ).split( "; filename=" )[ 1 ].replace( '"', '' )
        uploadFiletype = str( self.findContentOfHeader( submitBoundaryHeader, "Content-Type" ) )

        # Get boundary for break upload part
        uploadBoundary = str( self.findContentOfHeader( paramSubmitHeader, "Content-Type" ) ).split( "; boundary=" )[ 1 ]

        filetypeFound = ContentType( uploadFiletype )

        # Debugging output
        #print( f"func: uploadFile()" )
        #print( f"Filename: {uploadFilename}" )
        #print( f"Filetype: {uploadFiletype}" )
        #print( f"Filelength: {uploadFileLength}" )
        #print( f"Boundary: {uploadBoundary}" )

        if filetypeFound.name != uploadFilename.split( "." )[ 1 ].upper():
            # Filetype does not match!
            # Upload unallowed
            return ( False, HtmlStatusCode.CONFLICT, "Error: Filetype is not the same!" )

        # Reduce the filesize because extra data is added to the size
        # Body attached with boundary after the regular file
        tooMuchBytes = len( f"""{uploadBoundary}\r\nContent-Disposition: form-data; name="btnSubmit"\r\n\r\nUpload\r\n{uploadBoundary}\r\nContent-Disposition: form-data; name="FilePath"\r\n\r\n{uploadFilename}\r\n{uploadBoundary}--\r\n""".encode( 'utf-8' ) )
        uploadFileLength -= tooMuchBytes

        # Debugging output
        #print( f"After Reduce the upload file size: {uploadFileLength}" )

        # Upload allowed
        # Check header: Content-Range (for resume upload?)
        contentRange = self.findContentOfHeader( submitBoundaryHeader, "Content-Range" )

        # Get already loaded bytes
        # Example URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Range
        # Example: Content-Range: bytes 200-1000/67589
        startByte = 0
        if contentRange:
            startByte = int( contentRange.split( " " )[ 1 ].split( "-" )[ 0 ] )

        # Set it to the right user directory
        userFilePath = self.filesystemService.madeUserPath( uploadFilename )

        # if file exists append or it does not exists create a new one
        fileWriteMode = 'ab' if self.filesystemService.checkExists( userFilePath ) else 'wb'

        with open( userFilePath, fileWriteMode ) as writeFileHandler:
            if startByte > 0:
                # Check filesize - that the correct continue begins - otherwise terminate the upload
                currentFileSize = self.filesystemService.getFileSize( userFilePath )
                if currentFileSize != startByte:
                    return ( False, HtmlStatusCode.CONFLICT, "Error: Mismatched Start Byte" )
            else:
                if len(submitBoundaryBody) > 0:
                    writeFileHandler.write( submitBoundaryBody.encode( 'utf-8' ) )
                    # Received data missing BoundaryHeader and BoundaryBody are possible
                    # But why is so many bytes missing the last len(...\r\n...)??? No Idea, not yet!!! No Time to waste
                    startByte = len( submitBoundaryBody.encode( 'utf-8' ) ) + len( submitBoundaryHeader.encode( 'utf-8' ) ) + len( '\r\n\r\n\r\n\r\n\r\n\r\n'.encode( 'utf-8' ) )

            # Read file at position and continue with store at that position
            received = startByte
            while received < uploadFileLength:
                # Debugging output
                #print( f"Received size: {received} | uploadFileLength: {uploadFileLength}")

                if ( received + self.chunkSize ) > uploadFileLength:
                    # Debugging output
                    #print( f"{received + self.chunkSize} > {uploadFileLength}" )
                    #print( f"uploadFileLength - received = {uploadFileLength - received}" )

                    # The last puzzle is received from the socket. Break the while-loop
                    chunk = paramClientSocket.recv( uploadFileLength - received )
                    writeFileHandler.write( chunk )
                    break

                # Debugging output
                #print(" Continue normal chunk-size ")

                chunk = paramClientSocket.recv( self.chunkSize )
                writeFileHandler.write( chunk )
                received += len( chunk )

                if not chunk:
                    break

            return ( True, HtmlStatusCode.OK, "Upload completed!" )
