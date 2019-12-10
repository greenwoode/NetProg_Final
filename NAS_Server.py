from socket import *

import socket
import threading
import os.path
import time


def quit(connectionSocket):
    connectionSocket.close()

def sendContents(directory, connectionSocket):
    contents = os.listdir(directory)
    if len(contents) == 0:
        connectionSocket.send("Empty".encode())
    else:
        for x in contents:
            print(x)
            connectionSocket.send(x.encode())
            time.sleep(0.01)
    print("sent")
    connectionSocket.send("{done}".encode())

def login(connectionSocket):
    # Query for username, loops back if username incorrect
    username = connectionSocket.recv(4096).decode()
    directory = (os.path.abspath(os.curdir) + '\\Users\\' + username)
    # User data found
    if os.path.exists(directory):
        file_object = open(directory, 'rb')
        # fetching user password to store on variable
        password = file_object.read(1024).decode()
        connectionSocket.send("auth".encode())
        msg = connectionSocket.recv(4096).decode()
        # Receiving password
        if msg == "password":
            pw = connectionSocket.recv(4096).decode()
            # verifying password is correct
            if pw == password:
                connectionSocket.send("logged in".encode())
                user = username
                print(user + "Logged in")
                folderDir = (os.path.abspath(os.curdir) + '\\UserFolders\\' + username + '\\')
                # sending user current directory
                connectionSocket.send(folderDir.encode())
                # sending user list of items in directory
                sendContents(folderDir, connectionSocket)
                return True
            else:
                connectionSocket.send("ERROR".encode())
                connectionSocket.send("Incorrect Password.".encode())
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("Invalid arg".encode())
    # User data not found
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("No such username found.".encode())
    return False

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

def getContents(connectionSocket):
    folderDir = connectionSocket.recv(4096).decode()
    sendContents(folderDir, connectionSocket)

def folder(connectionSocket):
    folderDir = connectionSocket.recv(4096).decode()
    # checking for folder directory's existence
    if os.path.exists(folderDir):
        # Redundant? Folders end with \\, files dont
        if os.path.isdir(folderDir):
            connectionSocket.send("auth".encode())
            sendContents(folderDir, connectionSocket)
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("Item is not a folder".encode())
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder not found".encode())

def download(connectionSocket):
    filePath = connectionSocket.recv(4096).decode()
    # Checking if file exists
    if os.path.exists(filePath):
        connectionSocket.send("auth".encode())
        contentToSend = open(filePath, 'rb')
        connectionSocket.send(str(os.path.getsize(filePath)).encode())
        time.sleep(0.01)
        toSend = contentToSend.read(1024)
        connectionSocket.send(toSend)
        # Sending file
        while (toSend):
            toSend = contentToSend.read(1024)
            connectionSocket.send(toSend)
        contentToSend.close()
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("File not found".encode())

def makeFolder(connectionSocket):
    folderDir = connectionSocket.recv(4096).decode()
    if not os.path.exists(folderDir):
        connectionSocket.send("auth".encode())
        os.makedirs(os.path.dirname(folderDir))
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder already exists")

def deleteFolder(connectionSocket):
    dirToDelete = connectionSocket.recv(4096).decode()
    if os.path.exists(dirToDelete):
        if len(os.listdir(dirToDelete)) == 0:
            os.rmdir(dirToDelete)
            connectionSocket.send("auth".encode())
        else:
            connectionSocket.send("ERROR".encode())
            connectionSocket.send("Folder not empty".encode())
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("Folder not found".encode())

def deleteFile(connectionSocket):
    fileToDelete = connectionSocket.recv(4096).decode()
    if os.path.exists(fileToDelete):
        os.remove(fileToDelete)
        connectionSocket.send("auth".encode())
    else:
        connectionSocket.send("ERROR".encode())
        connectionSocket.send("File not found".encode())

def upload(connectionSocket):
    fileDir = connectionSocket.recv(1024).decode()
    totalSize = int(connectionSocket.recv(1024).decode())
    bytesRecvd = 0
    fileObj = open(fileDir, 'wb')
    while True:
        message = connectionSocket.recv(4096)
        bytesRecvd = bytesRecvd + len(message)
        fileObj.write(message)
        if bytesRecvd >= totalSize:
            break
    fileObj.close()

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

def runCommand(command, clientSocket):
    try:
        commands[command](clientSocket)
    except KeyError:
        print("Invalid Command")

def clientThread(serverSocket):
    loggedIn = False
    connectionSocket, addr = serverSocket.accept()
    connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
    connections.start()
    while True:
        if not loggedIn:
            command = connectionSocket.recv(4096).decode()
            if command == "quit":
                quit(connectionSocket)
                break
            if command == "login":
                loggedIn = login(connectionSocket)
            # For registering new users
            elif command == "register":
                register(connectionSocket)
        if loggedIn:
            command = connectionSocket.recv(4096).decode()
            runCommand(command,connectionSocket)

def checkFolders():
    userdir = os.path.abspath(os.curdir) + "\\Users\\"
    userfdir = os.path.abspath(os.curdir) + "\\UserFolders\\"
    if not os.path.exists(userdir):
        os.makedirs(os.path.dirname(userdir))
    if not os.path.exists(userfdir):
        os.makedirs(os.path.dirname(userfdir))



checkFolders()
serverPort = 8088
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(9999)
serverip = socket.gethostbyname(socket.gethostname())

print("Server IP: " + serverip)

# Initialize first thread for initial connection to chatroom
connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
connections.start()

while True:
    command = input()
    if command == "getip":
        print("Server IP: " + serverip)
    else:
        print("Invalid server command")
    continue
