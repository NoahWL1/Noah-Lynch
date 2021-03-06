from threading import Thread
import time
import socket


class Server:

    def __init__(self, name):
        self.serverName = name
        self.shouldRun = True
        self.clients = []
    
    def initialize(self):
        print("Server " + self.serverName + " starting...")
        connectionListenerThread = Thread(target=self.ConnectionListener, args=())
        connectionListenerThread.start()  # Start connection listener in its own thread
        
        time.sleep(0.5)  # Allow connection listener to start
        
        while self.shouldRun:  # Main server loop
            # print('outer')
            for client in self.clients:
                messages = client.read()
                if messages != None:
                    for message in messages:
                        self.handleMessage(message, client)
            time.sleep(0.001)
        
        for client in self.clients:
            client.close()
            
    def handleMessage(self, message, client):
        messageType = message[message.find('!type') + 5 : message.find('!/type')]  # Get message type
        # print('Type:', messageType)
        if messageType == 'PLAYERPOSITION':
            self.sendToAll(message, client.name)  # Pass on the player position to all clients
        elif messageType == 'CLIENTNAME':
            client.name = message[message.find('!name') + 5 : message.find('!/name')]
        elif messageType == 'SPAWNBULLET':
            self.sendToAll(message, client.name)  # Pass on bullet to all clients
        elif messageType == 'DAMAGE':
            print('received damage from', client.name, '... sending to rest of clients...')
            self.sendToAll(message, client.name)
            
    def getClientFromName(self, name):
        for client in self.clients:
            if client.name == name:
                return client
        return None
        
    def sendToAll(self, message, ignore):
        if ignore == None:
            ignore = ''
        for c in self.clients:
            if c.name != ignore:
                c.sendMessage(message)
        
    def ConnectionListener(self):
        serverSocket = socket.socket()
        serverSocket.bind(('', 2396))
        serverSocket.listen(5)
        
        while self.shouldRun:
            print("Waiting for clients")
            clientConnection, addressInfo = serverSocket.accept()
            print("Connection requested")
            cHandler = ClientHandler(self, clientConnection)
            cHandler.start()
            self.clients.append(cHandler)
            print('successfully added client to the server')
            
    def close(self):
        print('Closing server')
        self.shouldRun = False
        for ch in self.clients:
            ch.close()
            
    # GUI commands
    def startGame(self):
        print('Starting game...')
        message = '!typeSTARTGAME!/type !end'
        self.sendToAll(message, None)


class ClientHandler:

    def __init__(self, server, clientConnection):
        Thread.__init__(self)
        self.theServer = server
        self.shouldRun = True
        self.connection = clientConnection
        self.name = 'Name Not Yet Received'
        
    def start(self):
        self.listener = ClientListener(self, self.connection)
        self.writer = ClientWriter(self, self.connection)
        self.listener.start()
        self.writer.start()
        
    def read(self):
        m = []
        for message in self.listener.receivedMessages:
            m.append(message)
        self.listener.receivedMessages = []
        return m
    
    def sendMessage(self, message):
        self.writer.sendMessage(message)
        
    def close(self):
        self.shouldRun = False
        self.connection.close()

    
class ClientListener(Thread):

    def __init__(self, handler, connection):
        Thread.__init__(self)
        self.theHandler = handler
        self.receivedMessages = []
        self.connection = connection
        print("Client listener created")
        
    def run(self):
        while self.theHandler.shouldRun:
            buffer = ''  # TODO: Implement the buffer correctly
            # print('clientlistener')
            received = self.connection.recv(256)
            buffer += received.decode('utf-8')
            if buffer != '':
                self.receivedMessages.append(buffer[0:buffer.find("!end")])
                # print('b', buffer[0:buffer.find("!end")])
                # print('b2', buffer)
            time.sleep(0.001)

        
class ClientWriter(Thread):

    def __init__(self, handler, connection):
        Thread.__init__(self)
        self.theHandler = handler
        self.connection = connection
        self.messages = []
        self.hasMessages = False
        print("Client writer created")
        
    def run(self):
        while self.theHandler.shouldRun:
            # print('clientwriter')
            if len(self.messages) > 0:
                # print("Writing message: " + self.messages[0])
                self.connection.sendall(self.messages[0].encode("utf-8"))
                del self.messages[0]
            time.sleep(0.001)
                
    def sendMessage(self, message):
        self.messages.append(message)
