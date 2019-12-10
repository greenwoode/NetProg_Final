from socket import *
import os
from tkinter import filedialog
import tkinter
import time

currentDirectory = [""]
loggedIn = [False]
directoryList = []
username = [""]
running = True

def quit(clientSocket):
    clientSocket.send("quit".encode())
    clientSocket.close()
    exit(1)
# For printing contents of directory
def printcontents(clientSocket):
    while True:
        msg = clientSocket.recv(4096).decode()
        if msg == "{done}":
            break
        else:
            print(msg)

def login(clientSocket):
    print("Enter username:")
    username[0] = input()
    clientSocket.send("login".encode())
    clientSocket.send(username[0].encode())
    # Reply from server; tells us if username was validated or not
    reply = clientSocket.recv(4096).decode()
    if reply == "auth":
        print("Enter password:")
        pw = input()
        clientSocket.send("password".encode())
        clientSocket.send(pw.encode())
        # Reply from server; tells us if pw matched username or not
        reply = clientSocket.recv(4096).decode()
        if reply == "logged in":
            loggedIn[0] = True
            print("Logged in!")
            # Printing and getting current directory
            currentDirectory[0] = clientSocket.recv(4096).decode()
            print("Current directory: " + currentDirectory[0])
            # Printing current directory item list
            print("Items in directory: ")
            printcontents(clientSocket)
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        else:
            print("Unknown error: Password Verification")
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    else:
        print("Unknown error: Username input")

def register(clientSocket):
    print("Enter desired username:")
    # Entering username to register with
    username[0] = input()
    clientSocket.send("register".encode())
    clientSocket.send(username[0].encode())
    reply = clientSocket.recv(4096).decode()
    # Case where username is taken
    if reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    # Case where username is available
    elif reply == "auth":
        print(clientSocket.recv(4096).decode())
        # Entering desired pw
        print("Enter desired password:")
        password = input()
        clientSocket.send(password.encode())
        print(clientSocket.recv(4096).decode())

def getdirectory(clientSocket):
    print(currentDirectory[0])

def getcontents(clientSocket):
    print(currentDirectory[0])
    clientSocket.send("getContents".encode())
    clientSocket.send(currentDirectory[0].encode())
    printcontents(clientSocket)

def folder(clientSocket):
    print("Enter folder to enter:")
    # Input folder name
    folder = input()
    clientSocket.send("folder".encode())
    clientSocket.send((currentDirectory[0] + folder + "\\").encode())
    reply = clientSocket.recv(4096).decode()
    # Folder exists
    if reply == "auth":
        print("Current Directory: " + currentDirectory[0] + folder + "\\")
        currentDirectory[0] = currentDirectory[0] + folder + "\\"
        printcontents(clientSocket)
    # Folder does not exist
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    else:
        print("Unknown error, folder")

def download(clientSocket):
    print("Enter file to download:")
    # Input file name
    file = input()
    clientSocket.send("download".encode())
    clientSocket.send((currentDirectory[0] + file).encode())
    reply = clientSocket.recv(4096).decode()
    # File exists
    if reply == "auth":
        fileObj = open((os.path.abspath(os.curdir) + '\\Downloads\\' + file), 'wb')
        fileSize = int(clientSocket.recv(1024))
        bytesRecvd = 0
        print("Downloading...\n")
        while True:
            message = clientSocket.recv(1024)
            bytesRecvd = bytesRecvd + len(message)
            fileObj.write(message)
            if (bytesRecvd >= fileSize):
                break
        print("Download complete!")
        fileObj.close()
    # File does not exist
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    else:
        print("Unknown error, download")

def makefolder(clientSocket):
    print("Enter folder name:")
    # Input folder name
    name = input()
    clientSocket.send("makeFolder".encode())
    # send folder location
    clientSocket.send((currentDirectory[0] + name + "\\").encode())
    reply = clientSocket.recv(4096).decode()
    # Directory is empty, folder created
    if reply == "auth":
        print("Folder created")
    # Directory already exists
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    else:
        print("Unknown error, makeFolder")

def deletefolder(clientSocket):
    print("Enter folder name to delete:")
    # Input folder name
    name = input()
    print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
    decision = input()
    # Yes to delete
    if decision == "y":
        clientSocket.send("deleteFolder".encode())
        clientSocket.send((currentDirectory[0] + name + "\\").encode())
        reply = clientSocket.recv(4096).decode()
        # Folder exists, deleted
        if reply == "auth":
            print("Folder deleted")
        # Folder is not empty or not found
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        else:
            print("Unknown Error, deleteFolder")

def deletefile(clientSocket):
    print("Enter file name to delete:")
    # Input file name
    name = input()
    print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
    decision = input()
    if decision == "y":
        clientSocket.send("deleteFile".encode())
        clientSocket.send((currentDirectory[0] + name).encode())
        reply = clientSocket.recv(4096).decode()
        # File found, deleted file
        if reply == "auth":
            print("File deleted")
        # File not found
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        else:
            print("Unknown Error, deleteFile")

def back(clientSocket):
    stop = False
    temp = (currentDirectory[0])[:-1]
    while (True):
        if not (username[0] in temp):
            print("Unauthorized")
            break
        if (temp[len(temp) - 1] is not "\\"):
            temp = temp[:-1]
        else:
            currentDirectory[0] = temp
            print("Current Directory: ")
            print(currentDirectory[0])
            clientSocket.send("getContents".encode())
            clientSocket.send(currentDirectory[0].encode())
            printcontents(clientSocket)
            break

def upload(clientSocket):
    root = tkinter.Tk()
    root.withdraw()
    fileDir = filedialog.askopenfilename(initialdir="/Desktop", title="Select a File",
                                         filetypes=(("all files", "*.*"),))
    if len(fileDir) != 0:
        clientSocket.send("upload".encode())
        fileName = currentDirectory[0] + os.path.basename(fileDir)
        fileName = fileName.encode()
        clientSocket.send(fileName)
        time.sleep(0.05)
        fileToSend = open(fileDir, 'rb')
        fileSize = str(os.path.getsize(fileDir))
        clientSocket.send(fileSize.encode())
        time.sleep(0.05)
        print("Uploading...\n")
        toSend = fileToSend.read(4096)
        clientSocket.send(toSend)
        while (toSend):
            time.sleep(0.025)
            toSend = fileToSend.read(4096)
            clientSocket.send(toSend)
        print("Upload Complete!")
    else:
        print("No files sent\n")

def checkFolders():
    downloaddir = os.path.abspath(os.curdir) + "\\Downloads\\"
    userdir = os.path.abspath(os.curdir) + "\\Users\\"
    userfdir = os.path.abspath(os.curdir) + "\\UserFolders\\"
    if not os.path.exists(downloaddir):
        os.makedirs(os.path.dirname(downloaddir))
    if not os.path.exists(userdir):
        os.makedirs(os.path.dirname(userdir))
    if not os.path.exists(userfdir):
        os.makedirs(os.path.dirname(userfdir))

commands = {
    "getdirectory" : getdirectory,
    "getcontents" : getcontents,
    "folder" : folder,
    "download" : download,
    "makefolder": makefolder,
    "deletefolder": deletefolder,
    "deletefile": deletefile,
    "back": back,
    "upload": upload,
    "quit" : quit
}


def runcommand(command, clientSocket):
    try:
        commands[command](clientSocket)
    except KeyError:
        print("Invalid Command")

connected = False
while (not connected):
    try:
        serverName = input("Enter server IP: ")
        serverPort = 8088
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        connected = True
    except:
        print("Invalid server address!")
        arg = input("Try to reconnect? y or anything else: ")
        if arg != "y":
            exit(1)
checkFolders()



print("Hello! Enter login to log in to an existing account.")
print("Enter register to register as a new user.")
print("Enter quit to exit.")

while running:
    print("Enter command:")
    command = input().lower()
    if not loggedIn[0]:
        if command == "login":
            login(clientSocket)
        if command == "register":
            register(clientSocket)
        if command == "quit":
            quit(clientSocket)
    elif loggedIn[0]:
        runcommand(command, clientSocket)