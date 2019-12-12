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

# def that closes the connection w/ serve and ends program
def quit(clientSocket):
    clientSocket.send("quit".encode())
    clientSocket.close()
    exit(1)


# For printing contents of directory; Used when expecting a list of strings from server
def printcontents(clientSocket):
    length = int(clientSocket.recv(1024).decode())
    while length != 0:
        msg = clientSocket.recv(4096).decode()
        print(msg)
        length = length - 1


# For logging in
def login(clientSocket):
    print("Enter username:")
    username[0] = input()
    # Sends server command login w/ the username input
    clientSocket.send("login".encode())
    clientSocket.send(username[0].encode())
    # Reply from server; tells us if username was validated or not
    reply = clientSocket.recv(4096).decode()
    # Valid Username Case
    if reply == "auth":
        print("Enter password:")
        pw = input()
        # Lets server know the next packet is a pw for the previous username sent
        clientSocket.send("password".encode())
        clientSocket.send(pw.encode())
        # Reply from server; tells us if pw matched username or not
        reply = clientSocket.recv(4096).decode()
        # Valid pw case
        if reply == "logged in":
            # Sets logged in boolean as true for the main while loop
            loggedIn[0] = True
            print("Logged in!")
            # Printing and getting current directory
            currentDirectory[0] = clientSocket.recv(4096).decode()
            print("Current directory: " + currentDirectory[0])
            # Printing current directory item list
            print("Items in directory: ")
            printcontents(clientSocket)
        # Invalid PW case
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        # Case for unknown error (Unintended reply format)
        else:
            print("Unknown error: Password Verification")
    # Invalid username case
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    # Case for unknown error (Unintended reply format)
    else:
        print("Unknown error: Username input")

# For registering
def register(clientSocket):
    print("Enter desired username:")
    # Entering username to register with
    username[0] = input()
    # Sends command register to server w/ desired username
    clientSocket.send("register".encode())
    clientSocket.send(username[0].encode())
    # Reply from server indicating username is taken/available
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

# Prints current directory the client is browsing
def getdirectory(clientSocket):
    print(currentDirectory[0])

# Prints the contents of the folder client is currently browsing
def getcontents(clientSocket):
    print(currentDirectory[0])
    # Sends server command and directory to fetch content of
    clientSocket.send("getContents".encode())
    clientSocket.send(currentDirectory[0].encode())
    printcontents(clientSocket)

# Def for navigation into a folder
def folder(clientSocket):
    print("Enter folder to enter:")
    # Input folder name
    folder = input()
    # Sends server folder command + directory to navigate into
    clientSocket.send("folder".encode())
    clientSocket.send((currentDirectory[0] + folder + "\\").encode())
    # Reply from folder: server exists, or does not exist
    reply = clientSocket.recv(4096).decode()
    # Case for Folder exists
    if reply == "auth":
        # Prints out current directory
        print("Current Directory: " + currentDirectory[0] + folder + "\\")
        # Updates current directory
        currentDirectory[0] = currentDirectory[0] + folder + "\\"
        # Prints out contents in new directory
        printcontents(clientSocket)
    # Case for Folder does not exist
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    # Case for unknown error (Unintended reply format)
    else:
        print("Unknown error, folder")

# Def for download command
def download(clientSocket):
    print("Enter file to download:")
    # Input file name
    file = input()
    # Sends download command + the directory of the file to be downloaded to server
    clientSocket.send("download".encode())
    clientSocket.send((currentDirectory[0] + file).encode())
    # Reply should be if file exists or not
    reply = clientSocket.recv(4096).decode()
    # Case for File exists
    if reply == "auth":
        # Opens file object to write to in downloads folder
        fileobj = open((os.path.abspath(os.curdir) + '\\Downloads\\' + file), 'wb')
        # Size of downloading file, used to check if download completed or not
        filesize = int(clientSocket.recv(1024))
        # Received bytes, checked with file size to know when download finishes
        bytesrecvd = 0
        print("Downloading...\n")
        # While loop to keep recving data of file
        while True:
            message = clientSocket.recv(1024)
            # Updates bytes received to account for latest packet
            bytesrecvd = bytesrecvd + len(message)
            fileobj.write(message)
            # Break condition: Bytes received is equal to or greater than file size
            if (bytesrecvd >= filesize):
                break
        print("Download complete!")
        fileobj.close()
    # Case for File does not exist
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    # Case for unknown error (Unintended reply format)
    else:
        print("Unknown error, download")

# Def for making a folder in current directory
def makefolder(clientSocket):
    print("Enter folder name:")
    # Input folder name
    name = input()
    # Sends server command makeFolder and the directory of the new folder
    clientSocket.send("makeFolder".encode())
    clientSocket.send((currentDirectory[0] + name + "\\").encode())
    # Server reply if directory is available or not
    reply = clientSocket.recv(4096).decode()
    # Directory is empty, folder created
    if reply == "auth":
        print("Folder created")
    # Directory already exists
    elif reply == "ERROR":
        print(clientSocket.recv(4096).decode())
    # Case for unknown error (Unintended reply format)
    else:
        print("Unknown error, makeFolder")

# Def for deleting a folder in current directory
def deletefolder(clientSocket):
    print("Enter folder name to delete:")
    # Input folder name
    name = input()
    print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
    decision = input()
    # Yes to delete
    if decision == "y":
        # Sends server deletefolder command and directory of folder to delete
        clientSocket.send("deleteFolder".encode())
        clientSocket.send((currentDirectory[0] + name + "\\").encode())
        # Reply, if folder was deleted, or there was an error
        reply = clientSocket.recv(4096).decode()
        # Folder exists, deleted
        if reply == "auth":
            print("Folder deleted")
        # Folder is not empty or not found
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        # Case for unknown error (Unintended reply format)
        else:
            print("Unknown Error, deleteFolder")

# Def for deleting a file in current directory
def deletefile(clientSocket):
    print("Enter file name to delete:")
    # Input file name
    name = input()
    print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
    decision = input()
    # Yes to wanting to delete
    if decision == "y":
        # Sends server command deleteFile and directory of the file to delete
        clientSocket.send("deleteFile".encode())
        clientSocket.send((currentDirectory[0] + name).encode())
        # Server reply, file deleted or error
        reply = clientSocket.recv(4096).decode()
        # File found, deleted file
        if reply == "auth":
            print("File deleted")
        # File not found
        elif reply == "ERROR":
            print(clientSocket.recv(4096).decode())
        # Case for unknown error (Unintended reply format)
        else:
            print("Unknown Error, deleteFile")

# Def for navigating backwards
def back(clientSocket):
    temp = (currentDirectory[0])[:-1]
    while (True):
        # Case of trying to navigate out of the top-level folder user has access to
        # Detects username inside directory as the top-level folder's name is the username.
        if not (username[0] in temp):
            print("Unauthorized")
            break
        # Removing the end bit of the directory to "go back" a folder
        if temp[len(temp) - 1] is not "\\":
            temp = temp[:-1]
        # End of removing chars, finished moving back to parent folder
        else:
            # Changes currentdir to new one
            currentDirectory[0] = temp
            # Prints new dir
            print("Current Directory: ")
            print(currentDirectory[0])
            # Sends request to server to print the contents of new directory
            clientSocket.send("getContents".encode())
            clientSocket.send(currentDirectory[0].encode())
            printcontents(clientSocket)
            break

# Def for uploading
def upload(clientSocket):
    # Opens window
    root = tkinter.Tk()
    # Closes tkinter window that pops up by default
    root.withdraw()
    # Opens file explorer to select file to upload from client's computer
    fileDir = filedialog.askopenfilename(initialdir="/Desktop", title="Select a File",
                                         filetypes=(("all files", "*.*"),))
    # Checks for size of file chosen; of none chosen, len == 0, so none of this happens
    if len(fileDir) != 0:
        # Sends server upload command and directory of new file to write to
        clientSocket.send("upload".encode())
        filename = currentDirectory[0] + os.path.basename(fileDir)
        filename = filename.encode()
        clientSocket.send(filename)
        # Waits to make sure filename packet doesn't merge w/ data
        time.sleep(0.05)
        # Opens file object to read from
        filetosend = open(fileDir, 'rb')
        # Reads file size, sends this to let server know when to stop downloading
        filesize = str(os.path.getsize(fileDir))
        clientSocket.send(filesize.encode())
        time.sleep(0.05)
        print("Uploading...\n")
        # Starts sending packets
        tosend = filetosend.read(4096)
        clientSocket.send(tosend)
        while (tosend):
            tosend = filetosend.read(4096)
            clientSocket.send(tosend)
        print("Upload Complete!")
    else:
        print("No files sent\n")

# Def for initializing downloads folder
def checkFolders():
    # Checks if downloads folder exists
    downloaddir = os.path.abspath(os.curdir) + "\\Downloads\\"
    # Creates downloads folder if it does not exist
    if not os.path.exists(downloaddir):
        os.makedirs(os.path.dirname(downloaddir))

# Dictionary used to run commands based on input
commands = {
    "getdirectory": getdirectory,
    "getcontents": getcontents,
    "folder": folder,
    "download": download,
    "makefolder": makefolder,
    "deletefolder": deletefolder,
    "deletefile": deletefile,
    "back": back,
    "upload": upload,
    "quit": quit
}

# Used with dictionary commands to run commands that communicate w/ server
def runcommand(command, clientSocket):
    try:
        commands[command](clientSocket)
    except KeyError:
        print("Invalid Command")

# Boolean to indicate if client made initial connection or not
connected = False
while not connected:
    try:
        # Attempt to connect to IP entered
        serverName = input("Enter server IP: ")
        serverPort = 8088
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        # If valid IP, should continue and set connected to True so it does not loop again
        connected = True
    except:
        # Case for input IP is not a valid server addr, prompts user if they want to try to reconnect
        print("Invalid server address!")
        arg = input("Try to reconnect? y or anything else: ")
        if arg != "y":
            exit(1)
# Checks if downloads folder exists; if not, creates one
checkFolders()

print("Hello! Enter login to log in to an existing account.")
print("Enter register to register as a new user.")
print("Enter quit to exit.")
try:
    # Loop for entering commands to communicate w/ server
    while running:
        print("Enter command:")
        # Commands lowercased so any capital combinations would be valid
        command = input().lower()
        # Commands before logging in to an account
        if not loggedIn[0]:
            if command == "login":
                login(clientSocket)
            elif command == "register":
                register(clientSocket)
            elif command == "quit":
                quit(clientSocket)
            else:
                print("Invalid Command")
        # Commands after logging into an account
        elif loggedIn[0]:
            runcommand(command, clientSocket)
except Exception as e:
    print("Something went wrong!\n")
    print(str(e))
    time.sleep(100)
