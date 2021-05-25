import sys
import re
import socket
import pathlib
import os
import ntpath

list_of_args = sys.argv

#argument check
if len(sys.argv) != 5:
    sys.stderr.write("Wrong number of arguments\n")
    sys.exit(1)

if list_of_args[1] != '-n':
    if list_of_args[1] != '-f':
        sys.stderr.write("Wrong argument 1, it must be \"-f of -n\"\n")
        sys.exit(1)
    else:
        #arguments in order -f, -n
        if  re.match("^fsp://([a-zA-Z0-9]|-|_|\.|/|\*)+$", list_of_args[2]) is None:
            sys.stderr.write("Wrong argument 2, it must be valid surl\n")
            sys.exit(1)
        if list_of_args[3] != '-n':
            sys.stderr.write("Wrong argument 3, it must be \"-n of -f\"\n")
            sys.exit(1)
        if  re.match("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\:[0-9]+$", list_of_args[4]) is None:
            sys.stderr.write("Wrong argument 4, it must be valid IP with PORT\n")
            sys.exit(1)
        ipAndPortArg = list_of_args[4]
        surlArg = list_of_args[2]
else:
    #arguments in order -n, -f
    if  re.match("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\:[0-9]+$", list_of_args[2]) is None:
        sys.stderr.write("Wrong argument 2, it must be valid IP with PORT\n")
        sys.exit(1)
    if list_of_args[3] != '-f':
        sys.stderr.write("Wrong argument 3, it must be \"-n of -f\"\n")
        sys.exit(1)
    if  re.match("^fsp://([a-zA-Z0-9]|-|_|\.|/|\*)+$", list_of_args[4]) is None:
        sys.stderr.write("Wrong argument 4, it must be valid surl\n")
        sys.exit(1)
    ipAndPortArg = list_of_args[2]
    surlArg = list_of_args[4]

#FSP protocol
def FSP(serverFile):
    #this is used if we want to download all files from server    
    isDownloadAll = False
    if serverFile == "*":
        serverFile = "index"
        isDownloadAll = True

    queryFSP = bytes("GET " + serverFile + " FSP/1.0\r\n" + "Hostname: " + serverName + "\r\n" + "Agent: xhruzt00\r\n\r\n", "utf-8")
    #TCP communication
    try:
        sockFSP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockFSP.connect((ipFSP, portFSP))
        sockFSP.sendall(queryFSP)
        #If message is not recieved after 30 seconds client ends
        sockFSP.settimeout(30.0)
        #this is used because sometimes recieved content is corrupted
        frags = []
        while True: 
                chunk = sockFSP.recv(10000)
                if not chunk: 
                        break
                frags.append(chunk)
        sockFSP.close()

    except:
        sys.stderr.write("[FSP]Answer from server not recieved\n")
        sys.exit(1)

    #return message parsing
    #this will gain return code of message
    returnCode = frags[0].decode().split(" ")
    returnCode = returnCode[1].split("\r\n")

    #removes first part of message(header) and then content of message is added to bytes
    frags.pop(0)
    #contains only content from message
    outputBytes = b''.join(frags)
    
    if returnCode[0] == "Success":
        #this will be accessed if we want to find all files
        if isDownloadAll == True:
            try:
                files = outputBytes.decode().split("\r\n")
            except:
                sys.stderr.write("Error with gaining names of all files\n")
                sys.exit(1)
            #remove empty lines and keep only files
            files = [fil for fil in files if fil.strip()]
            #handle all files on server
            for f in files:
                FSP(f)
            sys.exit(0)
        #if success, save content to file with same name as original file from server, else write error answer from server
        try:
            # make directory for outputs
            # if filename contains path remove it   
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                pathOfServerFile, serverFile = ntpath.split(serverFile)
                dir_path = os.path.join(script_dir, 'output')
            except:
                sys.stderr.write("Path to output directory couldn't be created\n")
                sys.exit(1)      
            try:
                os.makedirs(dir_path)      
            except:
                #directory already exists
                pass
            #save files to output directory
            #parameter wb is used because it can rewrite already existing file, if x is used it can only create new file
            fileToSave = open(os.path.join(dir_path, serverFile), 'wb')
            fileToSave.write(outputBytes)
            fileToSave.close()
        except:
            sys.stderr.write("File couldn't be created\n")
            sys.exit(1)
    else:
        sys.stderr.write("[FSP] File not found " + outputBytes.decode() + "\r\n")
        sys.exit(1)

#NSP--------------------------------
ipAndPort = ipAndPortArg.split(":")
ipNSP = ipAndPort[0]
portNSP = int(ipAndPort[1])
#get server and file from SURL
serverAndFile = surlArg.replace("fsp://", "").split("/",1)
serverName = serverAndFile[0]
serverFile = serverAndFile[1]

#query for NSP protocol
queryNSP = "WHEREIS " + serverName

#UDP communication
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockNSP:
    try:
        sockNSP.sendto(bytes(queryNSP, "utf-8"), (ipNSP, portNSP))
        #If answer is not recieved after 30 seconds client ends
        sockNSP.settimeout(30.0)
        dataNSP = sockNSP.recv(4096)
    except:
        sys.stderr.write("[NSP]Answer from server not recieved\n")
        sys.exit(1)

    ipAndPortFromNSP = dataNSP.decode().split(" ")
    #if OK correct communication, else syntax error or server was not found
    if ipAndPortFromNSP[0] == "OK":
        ipAndPortForFSP =ipAndPortFromNSP[1].split(":")
        ipFSP = ipAndPortForFSP[0]
        portFSP = int(ipAndPortForFSP[1])
        FSP(serverFile)
    else:
        sys.stderr.write("[NSP] Server not found " + dataNSP.decode() + "\r\n")
        sys.exit(1)