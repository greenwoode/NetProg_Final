from socket import *
import threading
import os
import re
import time
import sys

recievePort = 8088
maxClients = 5

#commands
def test():
    print('oh shit')

def kick(user): ##have two seperate dictionaries; one for commands with args, one for commands without
    try:
        #kick user
        print('kicked ', user)
    except:
        print('failed to kick user ')

def listUsers():
    print('list users here')

commands = {
    'test': test,
    'kick': kick,
    'listusers': listUsers
    }
#end commands

def validateUser(username, passwordHash):
    #return id
    pass

def listenForUsers(users, serverSocket, maxClients):
    connectionSocket, addr = serverSocket.accept()
    if len(users) == maxClients:
        connectionSocket.send('Server Full'.encode())
    else:
        #take username and password
        #vaidate user
        userData = {'id': userId, 'name': userName, 'socket': connectionSocket}
        users.append(userData)
        


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', recievePort))
serverSocket.listen(maxClients)

users = list()
listening = threading.Thread(target=listenForUsers, args=(users, serverSocket, maxClients), daemon=True)

while True:
    commandIn = input()
    command = commandIn[:commandIn.find(' ')]
    args = commandIn[len(command) + 1:]

    if args is '':
        command = commandIn[:len(commandIn)]

    if command == 'quit':
        print('Closing...')
        #for user in users:
            #user.send('Server Closed'.encode());
        sys.exit(1)

    if args is '':
        if command in commands:
            commands[command]()
        else:
            print('unrecognized command')
    else:
        if command in commands:
            commands[command](args)
        else:
            print('unrecognized command')

