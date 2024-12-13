from mttkinter import mtTkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket
import errno
import sys
import select
from threading import Thread
import random
import datetime
import pickle

colors = {}
colorlist = ['black','red','green','black','cyan','magenta']

class window:
    def __init__(self,title):
        window.thr = True
        window._receive = Thread(target=self.receiving)

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry('160x130')
        self.root.configure(bg='#DF4747')

        self.frame = tk.Frame(self.root,height=100,width=100,bg='#DF4747')
        self.frame.pack(expand='yes')
        tk.Label(self.frame,text='username: ',bg='#DF4747',font=('Comic Sans', 12,'bold')).pack(side=tk.TOP,anchor=tk.CENTER,expand=1)

        self.userEntry = tk.Entry(self.frame)
        self.userEntry.pack(side=tk.TOP,anchor=tk.CENTER,expand=1)
        self.userEntry.bind('<Return>',self.login)

        tk.Button(self.frame,text='Submit',command=self.login,bg='#696666',fg='black',font=('Comic Sans',8)).pack(side=tk.TOP,anchor=tk.CENTER,expand=1,pady=10,ipadx=5)

        self.root.update()


    def room(self):
        self.frame.destroy()
        self.roomframe = tk.Frame(self.root,height=100,width=100,bg='#DF4747')

        self.listboxroom = tk.Listbox(self.roomframe)


        while True:
            try:
                self.len_listroom = int(window.client_socket.recv(window.HEADERSIZE).decode('utf-8'))
                self.listroom = pickle.loads(window.client_socket.recv(self.len_listroom))
                break
            except IOError:
                continue

        for i in self.listroom:
            self.listboxroom.insert('end',i)

        self.listboxroom.pack(side='top',anchor='center',expand=1)
        self.roomframe.pack(expand=1)

        self.listboxroom.bind('<Return>',lambda e: self.startchat(self.listroom[self.listboxroom.curselection()[0]]))


    def startchat(self,room_name):
        window.client_socket.send(f'{len(room_name):<{self.HEADERSIZE}}{room_name}'.encode('utf-8'))

        self.root.destroy()
        window._receive.start()
        self.app = window2(f'Chat >> {self.my_username.decode("utf-8")} : {room_name}')
        
    def login(self,event=None):
        if self.userEntry.get() != '':
            from clientsocket import client_socket, HEADERSIZE
            window.client_socket = client_socket
            window.HEADERSIZE = HEADERSIZE

            window.my_username = self.userEntry.get().encode('utf-8')
            self.username_header = f'{len(self.my_username):<{self.HEADERSIZE}}'.encode('utf-8')

            self.client_socket.send(self.username_header + self.my_username)

            self.room()

        else:
            pass

    def newmsg(self,msg):
        self.app.newmsg(msg)

    def receiving(self):
        while window.thr:
            try:
                while True:
                    username_header = self.client_socket.recv(self.HEADERSIZE)
                    if not len(username_header):
                        print('Connection closed by server')
                        sys.exit()
                    username_length = int(username_header.decode('utf-8'))
                    window.username = self.client_socket.recv(username_length).decode('utf-8')
                    if not window.username in colors:
                        color = random.choice(colorlist)
                        colors[window.username] = color
                        colorlist.remove(color)

                    message_header = self.client_socket.recv(self.HEADERSIZE)
                    message_length = int(message_header.decode('utf-8'))
                    message = self.client_socket.recv(message_length).decode('utf-8')

                    self.app.newmsg(f'{self.username} > {message}')

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit()
                continue

            except Exception as e:
                print('General error', str(e))
                sys.exit()


class window2(window):
    def __init__(self,title):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry('800x480')
        self.root.configure(bg='#DF4747')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.fm = tk.Frame(self.root)
        self.fm.configure(bg='#DF4747')

        self.txt = tk.Text(self.fm,state=tk.DISABLED)
        self.txt.grid(row=0,column=1)
        scrollb = ttk.Scrollbar(self.fm,command=self.txt.yview)
        scrollb.grid(row=0,column=2,sticky='nsw')
        self.txt['yscrollcommand'] = scrollb.set

        self.txt.tag_configure('me',foreground='blue')
        self.txt.tag_configure('black',foreground='black')
        self.txt.tag_configure('red',foreground='red')
        self.txt.tag_configure('green',foreground='green')
        self.txt.tag_configure('cyan',foreground='cyan')
        self.txt.tag_configure('magenta',foreground='magenta')
        self.txt.tag_configure('help',foreground='#B61B1B')

        tk.Label(self.fm,text=f'{window.my_username.decode("utf-8")}: ',bg='#DF4747',font=('Comic Sans', 12,'bold')).grid(row=1,column=0)
        self.messageEntry = tk.Entry(self.fm)
        self.messageEntry.grid(row=1,column=1,sticky="new",ipady=3)
        tk.Button(self.fm,text='>>>',command=lambda x: self.send(self.messageEntry.get()),bg='#696666',fg='black',font=('Comic Sans',8)).grid(row=1,column=2)

        self.messageEntry.bind('<Return>',lambda x: self.send(self.messageEntry.get()))
        self.fm.pack(expand=1)
        self.welcome()


    def welcome(self):
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END,f'Connected to chat hosted on ip: {window.client_socket.getsockname()[0]} server')
        self.txt.config(state=tk.DISABLED)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            window.thr = False
            window._receive.join()

    def newmsg(self,msg):
        if window.username != window.my_username.decode('utf-8'):
            self.txt.config(state=tk.NORMAL)
            self.txt.insert(tk.END,'\n'+msg,colors[window.username])
            self.txt.config(state=tk.DISABLED)
        else:
            self.txt.config(state=tk.NORMAL)
            self.txt.insert(tk.END,'\n'+msg,'me')
            self.txt.config(state=tk.DISABLED)

    def createmsg(self,msg,config):
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END,'\n'+msg,config)
        self.txt.config(state=tk.DISABLED)
        self.messageEntry.delete(0, 'end')

    def command(self,msg):
        if msg == '/':
            self.help()
        if msg == '/time':
            self.time(msg)
        if msg[:12] == '/changecolor':
            self.changecolor(msg)
        if msg[:5] == '/calc':
            self.calc(msg)

    def help(self):
        file = open('Commands.txt','r')
        self.createmsg(file.read(),'help')

    def time(self,msg):
        error = 'ERROR: Usage of command is /time'
        try:
            msg.replace(' ')[1]
            self.createmsg(error,'help')
        except:
            msg = datetime.datetime.now().strftime("%H:%M:%S")
            self.send(msg)

    def changecolor(self,msg):
            msg = msg.split(' ')
            error = 'ERROR: Usage of command is /changecolor #RRGGBB'
            try:
                rgb = msg[1]
            except:
                self.createmsg(error,'help')
                return
            if rgb[0] != '#':
                self.createmsg(error,'help')
            else:
                try:
                    rgb = rgb.replace('#','')
                    int(rgb,16)
                    self.txt.tag_configure('me',foreground=f'#{rgb}')
                except:
                    self.createmsg(error,'help')

    def calc(self,msg):
        msg = msg.split(' ')
        error = 'ERROR: Usage of command is /calc (operation)'
        try:
            msg[1]
        except:
            self.createmsg(error,'help')
            return
        try:
            eq = eval(msg[1][1:len(msg[1])-1])
            self.send(eq)
        except:
            self.createmsg(error,'help')



    def send(self,_msg,event=None):
        _msg = str(_msg)
        if _msg != '':
            if _msg[0] == '/':
                self.command(_msg)
                return
            msg = _msg.encode('utf-8')
            self.messageEntry.delete(0, 'end')
            message_header = f'{len(msg):<{window.HEADERSIZE}}'.encode('utf-8')
            window.client_socket.send(message_header + msg)
