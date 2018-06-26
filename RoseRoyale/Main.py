"""The main module.  This starts the game and client connection or a server."""

import os
import time
import random

from RoseRoyale.Server import Server
from RoseRoyale.ClientConnection import ClientConnection
from RoseRoyale.ServerGUI import ServerGUI
from RoseRoyale import StartScreen

from threading import Thread
import RoseRoyale.Game

myServer = None
serverGUI = None
cc = None
IP = '127.0.0.1'
username = str(random.randint(1, 100))  # Temp - assign a random username


def Main(runServer):  # Main function, starts the entire game
    if runServer:
        setupServer()
        serverGUI.startGUI()
    else:
        #setupServerConnection()
        RoseRoyale.Game.initialize(username, cc)
        
    shutdown()


def setupServerConnection():
    global cc
    global IP
    cc = ClientConnection(username)
    connectionThread = Thread(target=cc.connect, args=(IP,))
    connectionThread.start()


def setupServer():
    # Create a server instance
    global myServer
    global serverGUI
    
    # Start the instantiated server in its own thread
    myServer = Server(username)
    serverThread = Thread(target=myServer.initialize, args=())
    serverThread.start()
    
    # Create server GUI
    serverGUI = ServerGUI(myServer)


def shutdown():
    print('Shutting down')
    if cc != None:
        cc.close()
    
    if myServer != None:
        myServer.close()
        time.sleep(0.5)  # Allow some time for all threads to close cleanly
        os._exit(0)  # Ensure all threads are closed


if __name__ == "__main__":
    Selected = StartScreen.waitOnStart()
    if Selected == None:
        pass
    else:
        Main(Selected)
