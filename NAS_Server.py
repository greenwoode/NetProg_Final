from socket import *

import socket
import threading
import os.path
import time
import sys

# Def used to quit/close connection
def quit(connectionSocket):
    connectionSocket.close()

# Def used to send contents of a specified directory
def sendContents(directory, connectionSocket):
    # Makes a list of contents in directory
    contents = os.listdir(directory)
    # Case where directory is empty
    if len(contents) == 0:
        connectionSocket.send("1".encode())
        connectionSocket.send("Empty".encode())
    else:
        # For loop that sends all the items in the list
        # Sending length of list so client knows when to stop recving
        connectionSocket.send((str(len(contents))).encode())
        for x in contents:
            connectionSocket.send(x.encode())
            time.sleep(0.01)

# Def used for login interaction
def login(connectionSocket):
    try:
        # Query for username, loops back if username incorrect
        username = connectionSocket.recv(4096).decode()
        # Looks for user's data in users folder
        directory = (os.path.abspath(os.curdir) + '\\Users\\' + username)
        # User data found
        if os.path.exists(directory):
            file_object = open(directory, 'rb')
            # fetching user password to store on variable
            password = file_object.read(1024).decode()
            # Sends client msg that validates username
            connectionSocket.send("auth".encode())
            msg = connectionSocket.recv(4096).decode()
            # Receiving password
            if msg == "password":
                pw = connectionSocket.recv(4096).decode()
                # verifying password is correct
                if pw == password:
                    connectionSocket.send("logged in".encode())
                    user = username
                    print(user + " Logged in")
                    folderDir = (os.path.abspath(os.curdir) + '\\UserFolders\\' + username + '\\')
                    # sending user current directory
                    connectionSocket.send(folderDir.encode())
                    # sending user list of items in directory
                    sendContents(folderDir, connectionSocket)
                    # Returns true to set loggedIn as true
                    return True
                # Incorrect Password Case
                else:
                    connectionSocket.send("ERROR".encode())
                    connectionSocket.send("Incorrect Password.".encode())
            # Invalid command case
            else:
                connectionSocket.send("ERROR".encode())
                connectionSocket.send("Invalid arg".encode())
        # User data not found
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("No such username found.".encode())
        # Returns false to set loggedIn to false if not logged in successfully
        return False
    except Exception as exc:
        print(sys.exc_info()[0])

# Def used for registering new users
def register(connectionSocket):
    # receiving username
    username = connectionSocket.recv(4096).decode()
    directory = (os.path.abspath(os.curdir) + '\\Users\\' + username)
    # If username file exists
    if os.path.exists(directory):
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Username is already taken.".encode())
    # If username is not taken
    else:
        # Sends message notifying clientside that username not taken
        connectionSocket.send("auth".encode())
        connectionSocket.send("Username is available.".encode())
        # Takes in desired pw
        password = connectionSocket.recv(4096).decode()
        # Writes file with user data
        fileObj = open(directory, 'wb')
        fileObj.write(password.encode())
        # Creates user folder
        folderDir = (os.path.abspath(os.curdir) + '\\UserFolders\\' + username + '\\')
        os.makedirs(os.path.dirname(folderDir))
        if os.path.exists(directory):
            connectionSocket.send(
                "You can now log in with your new ID. Please log in after a minute wiht the login command.".encode())
            fileObj.flush()
        else:
            connectionSocket.send("Unknown Error".encode())

# Def for getting contents of directory
def getContents(connectionSocket):
    # Recvs directory to get content of
    folderDir = connectionSocket.recv(4096).decode()
    sendContents(folderDir, connectionSocket)

# Def for navigating into a folder
def folder(connectionSocket):
    folderDir = connectionSocket.recv(4096).decode()
    # checking for folder directory's existence
    if os.path.exists(folderDir):
        # Checking if directory is a folder, may be redundant due to folders ending in \\
        if os.path.isdir(folderDir):
            # Sends client msg that directory is valid, sends contents
            connectionSocket.send("auth".encode())
            sendContents(folderDir, connectionSocket)
        # Directory is not a folder
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("Item is not a folder".encode())
    # Invalid directory
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder not found".encode())

# Def for downloading
def download(connectionSocket):
    # Directory of file to be downloaded by client
    filePath = connectionSocket.recv(4096).decode()
    # Checking if file exists
    if os.path.exists(filePath):
        # Sends client directory is good
        connectionSocket.send("auth".encode())
        # Opens file to read from
        contentToSend = open(filePath, 'rb')
        # Sends file size to let client know when to stop downloading
        connectionSocket.send(str(os.path.getsize(filePath)).encode())
        time.sleep(0.01)
        toSend = contentToSend.read(1024)
        connectionSocket.send(toSend)
        # Sending file
        while (toSend):
            toSend = contentToSend.read(1024)
            connectionSocket.send(toSend)
        contentToSend.close()
    # File does not exist
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("File not found".encode())

# Def for making a folder
def makeFolder(connectionSocket):
    # Directory for new folder
    folderDir = connectionSocket.recv(4096).decode()
    # Case where directory is empty and can make folder
    if not os.path.exists(folderDir):
        # Sending client msg that directory is ok, making folder
        connectionSocket.send("auth".encode())
        os.makedirs(os.path.dirname(folderDir))
    # Case where directory is taken
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder already exists")

# Def for deleting folder
def deleteFolder(connectionSocket):
    # Recving directory of folder to delete
    dirToDelete = connectionSocket.recv(4096).decode()
    # Case where directory exists
    if os.path.exists(dirToDelete):
        # Checking if folder is empty; case where folder is empty
        if len(os.listdir(dirToDelete)) == 0:
            # Removes folder, sends client msg that folder was removed
            os.rmdir(dirToDelete)
            connectionSocket.send("auth".encode())
        # Case where folder is not empty
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("Folder not empty".encode())
    # Case where directory does not exist
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder not found".encode())

# Def for deleting files
def deleteFile(connectionSocket):
    # Directory of file to delete
    fileToDelete = connectionSocket.recv(4096).decode()
    # Case where file exists
    if os.path.exists(fileToDelete):
        # Deleting file, sending client auth that file was deleted
        os.remove(fileToDelete)
        connectionSocket.send("auth".encode())
    # Case where file directory is invalid
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("File not found".encode())

# Def for uploading file to server/current directory
def upload(connectionSocket):
    # Directory of file
    fileDir = connectionSocket.recv(1024).decode()
    # Total size of file to be uploaded, used to indicate when upload is finished
    totalSize = int(connectionSocket.recv(1024).decode())
    # Total data received, used to compare to totalsize to indicate when upload is finished
    bytesRecvd = 0
    # Opening file object to write to
    fileObj = open(fileDir, 'wb')
    # Receiving data for file and writing to file
    while True:
        message = connectionSocket.recv(4096)
        bytesRecvd = bytesRecvd + len(message)
        fileObj.write(message)
        # Break message; stops waiting for data when data received is equal to or greater than file size
        if bytesRecvd >= totalSize:
            break
    fileObj.close()

# Dictionary used to point commands to defs
commands = {
    "quit":quit,
    "getContents":getContents,
    "folder":folder,
    "download":download,
    "makeFolder":makeFolder,
    "deleteFolder":deleteFolder,
    "deleteFile":deleteFile,
    "upload":upload
}

# Def to run defs according to command sent by client
def runCommand(command, clientSocket):
    try:
        commands[command](clientSocket)
    except KeyError:
        print("Invalid Command")

# Main thread for each client
def clientThread(serverSocket):
    loggedin = False
    # Accepting connection w/ a client
    connectionSocket, addr = serverSocket.accept()
    # Creates a new thread that waits for a different client to connect, as this one is taken
    connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
    connections.start()
    try:
        # Loop waiting for clientside commands
        while True:
            # Commands while not logged in
            if not loggedin:
                # Command from client
                command = connectionSocket.recv(4096).decode()
                if command == "quit":
                    quit(connectionSocket)
                    break
                if command == "login":
                    # Sets boolean as whatever login returns (True if logged in, False otherwise)
                    loggedin = login(connectionSocket)
                # For registering new users
                elif command == "register":
                    register(connectionSocket)
            if loggedin:
                # Command from client
                command = connectionSocket.recv(4096).decode()
                # Runs def corresponding to command in the dictionary
                runCommand(command,connectionSocket)
    except:
        print("Disconnected Client")


# Def for checking for folders
def checkFolders():
    # Checks if user/userfolders exists, creates them if not
    userdir = os.path.abspath(os.curdir) + "\\Users\\"
    userfdir = os.path.abspath(os.curdir) + "\\UserFolders\\"
    if not os.path.exists(userdir):
        os.makedirs(os.path.dirname(userdir))
    if not os.path.exists(userfdir):
        os.makedirs(os.path.dirname(userfdir))


# Checks if UserFolders and Users directories exist
checkFolders()
# Initializes server socket
serverPort = 8088
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(9999)
# Displays server ip to connect to
serverip = socket.gethostbyname(socket.gethostname())

print("Server IP: " + serverip)

# Initialize first thread for initial connection to chatroom
connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
connections.start()

# Available to fetch IP while running by entering getip, potential add-ons for serverside commands
while True:
    command = input()
    if command == "getip":
        print("Server IP: " + serverip)
    else:
        print("Invalid server command")
    continue
