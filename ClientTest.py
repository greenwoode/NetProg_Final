from socket import *
import threading
import os
from tkinter import *
from tkinter import filedialog
import tkinter
import time

currentDirectory = ""
directoryList = []


# For printing contents of directory
def printContents(clientSocket):
    while True:
        msg = clientSocket.recv(4096).decode()
        if msg == "{done}":
            break
        else:
            print(msg)


serverName = "localhost"
serverPort = 1592
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

print("Hello! Enter login to log in to an existing account.")
print("Enter register to register as a new user.")
print("Enter quit to exit.")
loggedIn = False
while True:
    print("Enter command:")
    command = input()
    if not loggedIn:
        if command == "login":
            print("Enter username:")
            username = input()
            clientSocket.send("login".encode())
            clientSocket.send(username.encode())
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
                    loggedIn = True
                    print("Logged in!")
                    # Printing and getting current directory
                    currentDirectory = clientSocket.recv(4096).decode()
                    print("Current directory: " + currentDirectory)
                    # Printing current directory item list
                    print("Items in directory: ")
                    printContents(clientSocket)
                elif reply == "ERROR":
                    print(clientSocket.recv(4096).decode())
                else:
                    print("Unknown error: Password Verification")
            elif reply == "ERROR":
                print(clientSocket.recv(4096).decode())
            else:
                print("Unknown error: Username input")
        if command == "register":
            print("Enter desired username:")
            # Entering username to register with
            username = input()
            clientSocket.send("register".encode())
            clientSocket.send(username.encode())
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
        if command == "quit":
            clientSocket.send("quit")
            break
    elif loggedIn:
        # Quit command
        if command == "quit":
            clientSocket.send("quit".encode())
            clientSocket.close()
            break
        # Printing current directory
        if command == "getDirectory":
            print(currentDirectory)
        # getContents command for fetching list of items in current directory
        if command == "getContents":
            clientSocket.send("getContents".encode())
            clientSocket.send(currentDirectory.encode())
            printContents(clientSocket)
        # Going into a folder in current directory
        if command == "folder":
            print("Enter folder to enter:")
            # Input folder name
            folder = input()
            clientSocket.send("folder".encode())
            clientSocket.send((currentDirectory + folder + "\\").encode())
            reply = clientSocket.recv(4096).decode()
            # Folder exists
            if reply == "auth":
                print("Current Directory: " + currentDirectory + folder + "\\")
                currentDirectory = currentDirectory + folder + "\\"
                printContents(clientSocket)
            # Folder does not exist
            elif reply == "ERROR":
                print(clientSocket.recv(4096).decode())
            else:
                print("Unknown error, folder")
        # Download command to download a file in current directory
        if command == "download":
            print("Enter file to download:")
            # Input file name
            file = input()
            clientSocket.send("download".encode())
            clientSocket.send((currentDirectory + file).encode())
            reply = clientSocket.recv(4096).decode()
            # File exists
            if reply == "auth":
                fileObj = open((os.path.abspath(os.curdir) + '\\Downloads\\' + file), 'wb')
                while True:
                    message = clientSocket.recv(1024)
                    if (len(message) < 1024):
                        fileObj.close()
                        break
                    print(message.decode())
                    print("Loop??")
                    fileObj.write(message)
                print("Download complete!")
            # File does not exist
            elif reply == "ERROR":
                print(clientSocket.recv(4096).decode())
            else:
                print("Unknown error, download")
        # Command to make folder in current directory
        if command == "makeFolder":
            print("Enter folder name:")
            # Input folder name
            name = input()
            clientSocket.send("makeFolder".encode())
            # send folder location
            clientSocket.send((currentDirectory + name + "\\").encode())
            reply = clientSocket.recv(4096).decode()
            # Directory is empty, folder created
            if reply == "auth":
                print("Folder created! It may take a minute for the contents to update.")
            # Directory already exists
            elif reply == "ERROR":
                print(clientSocket.recv(4096).decode())
            else:
                print("Unknown error, makeFolder")
        # Command to delete existing folder
        if command == "deleteFolder":
            print("Enter folder name to delete:")
            # Input folder name
            name = input()
            print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
            decision = input()
            # Yes to delete
            if decision == "y":
                clientSocket.send("deleteFolder".encode())
                clientSocket.send((currentDirectory + name + "\\").encode())
                reply = clientSocket.recv(4096).decode()
                # Folder exists, deleted
                if reply == "auth":
                    print("Folder deleted")
                # Folder is not empty or not found
                elif reply == "ERROR":
                    print(clientSocket.recv(4096).decode())
                else:
                    print("Unknown Error, deleteFolder")
        # Command to delete existing file
        if command == "deleteFile":
            print("Enter file name to delete:")
            # Input file name
            name = input()
            print("Are you sure you want to delete " + name + "? Type y to delete, anything else to not.")
            decision = input()
            if decision == "y":
                clientSocket.send("deleteFile".encode())
                clientSocket.send((currentDirectory + name).encode())
                reply = clientSocket.recv(4096).decode()
                # File found, deleted file
                if reply == "auth":
                    print("File deleted")
                # File not found
                elif reply == "ERROR":
                    print(clientSocket.recv(4096).decode())
                else:
                    print("Unknown Error, deleteFile")
        if command == "back":
            stop = False
            temp = currentDirectory[:-1]
            while (True):
                if not(username in temp):
                    print("Unauthorized")
                    break
                if (temp[len(temp)-1] is not "\\"):
                    temp = temp[:-1]
                else:
                    currentDirectory = temp
                    print("Current Directory: ")
                    print(currentDirectory)
                    clientSocket.send("getContents".encode())
                    clientSocket.send(currentDirectory.encode())
                    printContents(clientSocket)
                    break
        if command == "upload":
            fileDir = filedialog.askopenfilename(initialdir="/Desktop", title = "Select a File", filetypes = (("all files","*.*"),))
            print(fileDir)
            print(len(fileDir))
            if len(fileDir) != 0:
                clientSocket.send("upload".encode())
                fileName = currentDirectory + os.path.basename(fileDir)
                fileName = fileName.encode()
                print(fileName)
                #clientSocket.send((currentDirectory+fileName).encode('utf-8'))
                clientSocket.send(fileName)
                time.sleep(0.05)
                fileToSend = open(fileDir, 'rb')
                toSend = fileToSend.read(1024)
                clientSocket.send(toSend)
                while (toSend):
                    toSend = fileToSend.read(1024)
                    clientSocket.send(toSend)
                clientSocket.send(fileToSend.read(1024))
                print("Done")
            else:
                print("No files sent\n")