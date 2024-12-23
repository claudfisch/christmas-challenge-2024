from os.path import exists as osPathExists, getsize as osPathGetsize, join as osPathJoin
from os import mkdir as osMkdir, remove as osRmdir, listdir as osListdir, stat as osStat
from datetime import datetime
from stat import S_ISDIR as statIsDir, S_ISREG as statIsFile

class Filesystem:
    def __init__( self, paramWorkDirectory: str = "./wwwdata", paramUserDirectory: str = "userdata" ):
        self.workDirectory = paramWorkDirectory
        self.userDirectory = paramUserDirectory

    def __str__( self ):
        return f"The working directory is: {self.workDirectory}"

    def doMove( self, paramSource: str, paramTarget: str ):
        # Can be a file or directory to move
        pass

    def doCopy( self, paramSource: str, paramTarget: str ):
        # Can be a file or directory to copy
        pass

    def madeWorkPath( self, paramTarget: str ):
        return osPathJoin( self.workDirectory, paramTarget )

    def madeUserPath( self, paramTarget: str, paramUsername: str = "guest" ):
        if "%2F" in paramTarget:
            # Only for Download path - replace %2F with Slash - Join the working Directory
            paramTarget = paramTarget.replace( '%2F', '/' )
        return osPathJoin( self.workDirectory, self.userDirectory, paramUsername, paramTarget )

    def checkExists( self, paramTarget: str ):
        # Debugging output
        #print( f"Func. checkExists( param1: {paramTarget} )" )
        if osPathExists( paramTarget ):
            return True
        return False

    def getFileSize(self, paramSourceFile: str ):
        if self.checkExists( paramSourceFile ):
            return osPathGetsize( paramSourceFile )

        # Unknown filesize
        return 0

    def readFile( self, paramSourceFile: str, paramFileAttributes: str = "rb"):
        if self.checkExists( paramSourceFile ):
            with open( paramSourceFile, paramFileAttributes ) as fileHandler:
                return fileHandler.read()
        return False

    def getDateTimeFromTimestamp(self, paramTimestamp: datetime.timestamp):
        return str( datetime.fromtimestamp( paramTimestamp ) ).split( "." )[ 0 ]

    def listDirectory( self, paramTargetDirectory: str ):
        if self.checkExists( paramTargetDirectory ) == False:
            print( "Error - Directory does not exists" )
            return

        directoryInfo = []
        fileInfo = []

        try:
            # Example: os.stat_result(st_mode=, st_ino=, st_dev=, st_nlink=, st_uid=, st_gid=, st_size=, st_atime=, st_mtime=, st_ctime=)

            # Switch between directoryInfo and fileInfo
            tmpSwitcher = None
            for elementDirectoryOrFile in osListdir( paramTargetDirectory ):
                # Get the right directory
                tmpFilePath = osPathJoin( paramTargetDirectory, elementDirectoryOrFile )
                fileStats = osStat( tmpFilePath )
                fileType = None
                if statIsDir( fileStats.st_mode ):
                    fileType = "DIR"
                    tmpSwitcher = directoryInfo
                elif statIsFile( fileStats.st_mode ):
                    fileType = "FILE"
                    tmpSwitcher = fileInfo
                else:
                    fileType = "UNKNOWN"

                tmpSwitcher.append( { "name": elementDirectoryOrFile, "type": fileType, "size": format(fileStats.st_size/1024, ".2f"), "creationDate": self.getDateTimeFromTimestamp( fileStats.st_ctime ), "modifiedDate": self.getDateTimeFromTimestamp( fileStats.st_atime ) } )

            # give the combine info back
            return directoryInfo + fileInfo
        except Exception as e:
            # no directories or files found
            print( f"Error: {repr(e)}" )
            return []

    def makeDirectory( self, paramTargetDirectory: str ):
        if self.checkExists( paramTargetDirectory ) == False:
            try:
                osMkdir( paramTargetDirectory )
            except PermissionError:
                print( "Permission denied! Check the write bit!" )
            except Exception as e:
                print( f"Unknown error occurred: {repr(e)}" )
        else:
            print( "Path already exists!" )

    def removeDirectory( self, paramTargetDirectory: str, paramIsRecursive: bool = False ):
        if paramIsRecursive == False:
            try:
                osRmdir( paramTargetDirectory )
            except:
                print( "Directory can not be removed. It is not empty, yet!" )
                return False
            return True

        # Recursive
        # ToDo: Delete directory with content - other directories or files
        return False
