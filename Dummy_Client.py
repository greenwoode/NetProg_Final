from socket import *
import re
import sys

def test():
    print('oh shit')

def quit():
    print('Closing...')
    #for user in users:
        #user.send('Server Closed'.encode());
    sys.exit(1)

commands = {
    'test': test,
    'quit': quit
    }

while True:
    commandIn = input()
    command = commandIn[:commandIn.find(' ')]
    args = commandIn[len(command) + 1:]

    if args is '':
        command = commandIn[:len(commandIn)]
    print(command + '!')

    if command == 'quit':
        print('command is \'quit\'')
        sys.exit(1)

    try:
        commands[command]()
    except:
        print('nope')