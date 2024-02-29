# -*- coding: utf-8 -*-
"""
Created on Wed May  3 08:26:12 2023

@author: e436482
"""

import socket
import os
import argparse
import threading
import random
import datetime as dt



class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        self.username = None  


    def run(self):
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print('Listening at', sock.getsockname())
        
        while True:

            # new connection
            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {} '.format(sc.getpeername(), sc.getsockname()))
    
            # new thread
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()
    
            # thread to active connections
            self.connections.append(server_socket)
            print('Ready to receive messages from', sockname)
           
    def broadcast(self, message, source):
        for connection in self.connections:
            #send to all connected clients 
            if connection.sockname != source:
                connection.send(message)

    def broadcast_user_list(self):
        user_list = []
        for connection in self.connections:
            user_list.append(connection.username)
            connection.send(f":{','.join(user_list)}")

class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        self.username = None  
        self.color = self.generate_random_color()

    def generate_random_color(self):
        # Generate a random color code in hexadecimal (e.g., #FF5733)
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def run(self):
        # Assuming the first message from the client is their username
        self.username = self.sc.recv(1024).decode('ascii')
        self.server.broadcast_user_list()

        while True:
            message = self.sc.recv(1024).decode('ascii')
            if message:
                print('{} :: {!r}'.format(self.username, message))
                self.server.broadcast(message, self.username)
            else:
                # Client has closed the socket, exit the thread
                print('{} has closed the connection'.format(self.username))
                self.sc.close()
                server.connections.remove(self)
                return

    def send(self, message):
        time = dt.datetime.now().strftime('%H:%M:%S')
        message_with_color_and_time = f"{self.color}:{time}:{self.username}:{message}"  # Prepend color to message
        
        print(message_with_color_and_time)
        self.sc.sendall(message_with_color_and_time.encode('ascii'))

def exit(server):

    while True:
        ipt = input('')
        if ipt == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)
    
if __name__ == '__main__':
    
    # parser = argparse.ArgumentParser(description='Chatroom Server')
    # parser.add_argument('host', help='Interface the server listens at')
    # parser.add_argument('-p', metavar='PORT', type=int, default=8080,
    #                     help='TCP port (default 8080)')
    # args = parser.parse_args()

    # Create and start server thread
    host = '10.0.0.234'
    port = 8080
    server = Server(host, port)
    server.start()

    exit = threading.Thread(target = exit, args = (server,))
    exit.start()