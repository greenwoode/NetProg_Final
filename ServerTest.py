from socket import *

import threading
import os.path
import time


def isQuit(msg):
    if msg == "quit":
        return True
    return False


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


def clientThread(serverSocket):
    loggedIn = False
    user = "none"
    connectionSocket, addr = serverSocket.accept()
    connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
    connections.start()
    while True:
        if not loggedIn:
            command = connectionSocket.recv(4096).decode()
            if isQuit(command):
                break
            if command == "login":
                # Query for username, loops back if username incorrect
                username = connectionSocket.recv(4096).decode()
                directory = (os.path.abspath(os.curdir) + '\\Users\\' + username)
                # User data found
                if os.path.exists(directory):
                    file_object = open(directory, 'rb')
                    # fetching user password to store on variable
                    password = file_object.read(1024).decode()
                    print(password)
                    connectionSocket.send("auth".encode())
                    msg = connectionSocket.recv(4096).decode()
                    # Receiving password
                    if msg == "password":
                        pw = connectionSocket.recv(4096).decode()
                        # verifying password is correct
                        if pw == password:
                            loggedIn = True
                            connectionSocket.send("logged in".encode())
                            user = username
                            print("Logged in")
                            folderDir = (os.path.abspath(os.curdir) + '\\UserFolders\\' + username + '\\')
                            # sending user current directory
                            connectionSocket.send(folderDir.encode())
                            # sending user list of items in directory
                            sendContents(folderDir, connectionSocket)
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
            # For registering new users
            elif command == "register":
                print("In register")
                # receiving username
                username = connectionSocket.recv(4096).decode()
                print("username received")
                print(username)
                directory = (os.path.abspath(os.curdir) + '\\Users\\' + username)
                # If username file exists
                if os.path.exists(directory):
                    connectionSocket.send("ERROR".encode())
                    connectionSocket.send("Username is already taken.".encode())
                # If username is not taken
                else:
                    print("In else")
                    connectionSocket.send("auth".encode())
                    connectionSocket.send("Username is available.".encode())
                    # Takes in desired pw
                    password = connectionSocket.recv(4096).decode()
                    # Writes file with user data
                    fileObj = open(directory, 'wb')
                    fileObj.write(password.encode())
                    # Creates user folder
                    folderDir = (os.path.abspath(os.curdir) + '\\UserFolders\\' + username + '\\')
                    print(folderDir)
                    os.makedirs(os.path.dirname(folderDir))
                    if os.path.exists(directory):
                        connectionSocket.send(
                            "You can now log in with your new ID. Please log in after a minute wiht the login command.".encode())
                        fileObj.flush()
                    else:
                        connectionSocket.send("Unknown Error".encode())
        if loggedIn:
            print("waiting")
            command = connectionSocket.recv(4096).decode()
            if isQuit(command):
                connectionSocket.close()
                print("Disconnected")
                break
            print("Cmd received")
            # Command to get contents of current directory
            if command == "getContents":
                print("in command getcontents")
                folderDir = connectionSocket.recv(4096).decode()
                sendContents(folderDir, connectionSocket)
            # Command to go into folder
            if command == "folder":
                print("in command folder")
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
            # Command for downloading files
            if command == "download":
                filePath = connectionSocket.recv(4096).decode()
                # Checking if file exists
                if os.path.exists(filePath):
                    connectionSocket.send("auth".encode())
                    contentToSend = open(filePath, 'rb')
                    connectionSocket.send(str(os.path.getsize(filePath)).encode())
                    toSend = contentToSend.read(1024)
                    connectionSocket.send(toSend)
                    # Sending file
                    while (toSend):
                        toSend = contentToSend.read(1024)
                        connectionSocket.send(toSend)
                    connectionSocket.send("{done}".encode())
                else:
                    connectionSocket.send("ERROR".encode())
                    connectionSocket.send("File not found".encode())
            # Command to make a folder in current directory
            if command == "makeFolder":
                print("In makeFolder")
                folderDir = connectionSocket.recv(4096).decode()
                if not os.path.exists(folderDir):
                    print("IN if else")
                    connectionSocket.send("auth".encode())
                    os.makedirs(os.path.dirname(folderDir))
                    print("Done!")
                else:
                    connectionSocket.send("ERROR".encode())
                    connectionSocket.send("Folder already exists")
            # Command to delete folder
            if command == "deleteFolder":
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
            # Command to delete file
            if command == "deleteFile":
                fileToDelete = connectionSocket.recv(4096).decode()
                if os.path.exists(fileToDelete):
                    os.remove(fileToDelete)
                    connectionSocket.send("auth".encode())
                else:
                    connectionSocket.send("ERROR".encode())
                    connectionSocket.send("File not found".encode())
            if command == "upload":
                fileDir = connectionSocket.recv(1024).decode()
                totalSize = int(connectionSocket.recv(1024).decode())
                bytesRecvd = 0
                print(fileDir)
                print(totalSize)
                fileObj = open(fileDir, 'wb')
                while True:
                    print("Waiting")
                    message = connectionSocket.recv(4096)
                    print("Recv'd")
                    bytesRecvd = bytesRecvd + len(message)
                    print(len(message))
                    print(bytesRecvd)
                    fileObj.write(message)
                    if bytesRecvd >= totalSize:
                        fileObj.close()
                        print("Done!")
                        break






serverPort = 1592
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(9999)

# Initialize first thread for initial connection to chatroom
connections = threading.Thread(target=clientThread, args=(serverSocket,), daemon=True)
connections.start()

while True:
    continue
