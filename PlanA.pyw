from tkinter import *
from tkinter import filedialog
import tkinter


#check to see if there are inputs in username and password entry when they click register
def checkRegisterInputs():
    if ((not usernameEntry.get()) and (not passwordEntry.get())) or (not usernameEntry.get()) or (not passwordEntry.get()):
        registerMessage.destroy()
        loginErrorMessage.grid_forget()
        registerErrorMessage.grid(row=1, columnspan=6, sticky='S')
    else:
        repositoryWindow()

#check to see if there are inputs in username and password entry when they click login
def checkLoginInputs():
    if ((not usernameEntry.get()) and (not passwordEntry.get())) or (not usernameEntry.get()) or (not passwordEntry.get()):
        registerMessage.destroy()
        registerErrorMessage.grid_forget()
        loginErrorMessage.grid(row=1, columnspan=6, sticky='S')
    else:
        repositoryWindow()

#open Desktop, display selected file
def displayFile():
    repository.filename = filedialog.askopenfilename(initialdir="/Desktop", title="Select A File", filetypes=(("all files","*.*"),))
    labelFileName = Label(repository, text=repository.filename).pack()
    fileImageLabel = Label(image=labelFileName).pack()

#display repository window
def repositoryWindow():
    global repository
    login.destroy()
    repository = Tk()
    repository.geometry('1000x500')
    message = 'asdasd'
    Label(repository, text=message).pack()
    openFileButton = Button(repository, text="Open File", command=displayFile).pack()

#login window
login = Tk() 

#starts out at 600x100 and is resizable
login.geometry('600x100')

registerMessage = Label(login, text='If you are a first time user, please enter a username and password and click register.')

username = Label(login,text='Username')
password = Label(login,text='Password')

#error messages
registerErrorMessage = Label(login, text='Please enter a username and password.')
loginErrorMessage = Label(login, text='Username and password does not match.')

usernameEntry = Entry(login)
passwordEntry = Entry(login, show='*')

loginButton = Button(login, text="Login", command=checkLoginInputs)
registerButton = Button(login, text="Register", command=checkRegisterInputs)

registerMessage.grid(row=1, columnspan=6, sticky='S')

username.grid(row=2, column=1)
usernameEntry.grid(row=2, column=2)
password.grid(row=3, column=1)
passwordEntry.grid(row=3, column=2)
loginButton.grid(row=4, column = 2, sticky='W')
registerButton.grid(row=4, column = 2, sticky='E')

login.grid_rowconfigure(0, weight=1)
login.grid_rowconfigure(5, weight=1)
login.grid_columnconfigure(0, weight=1)
login.grid_columnconfigure(5, weight=1)

mainloop()
