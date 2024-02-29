import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import socket

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Welcome to Chat Client')
        self.setFixedSize(250, 100)

        layout = QVBoxLayout()

        self.nameInput = QLineEdit()
        layout.addWidget(self.nameInput)

        connectButton = QPushButton('Enter the Chat')
        # connectButton.setFixedWidth(50)
        connectButton.clicked.connect(self.connect)
        layout.addWidget(connectButton)

        self.setLayout(layout)

    def connect(self):
        name = self.nameInput.text()
        if not name:
            QMessageBox.critical(self, 'Error', 'Name cannot be empty.', QMessageBox.Ok)
            return
        else:
            self.client = ChatClient('10.0.0.234', 8080, name)  # Set as an attribute of WelcomeWindow
            self.client.show()
            self.close() 

class ReceiveThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                self.message_received.emit(message)
            except OSError:  
                break

class ChatClient(QWidget):
    def __init__(self, host, port, name):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.name = name

        self.initUI()
        self.receive_thread = ReceiveThread(self.sock)
        self.receive_thread.message_received.connect(self.displayMessage)
        self.receive_thread.start()
        
        self.sock.sendall(f'username: {name}'.encode('ascii'))  
        self.chatHistory.append(f'Welcome to the chat, {name}!')

    def initUI(self):

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        '''
        Set up the UI for the chat client.
        '''
        self.setWindowTitle('Chat Client')
        self.setFixedSize(600, 400)

        chat_layout = QVBoxLayout()

        self.chatHistory = QTextBrowser()
        self.chatHistory.setReadOnly(True)
        chat_layout.addWidget(self.chatHistory)

        #line edit
        send_message_layout = QHBoxLayout()
        self.messageInput = QLineEdit()
        send_message_layout.addWidget(self.messageInput)

        sendButton = QPushButton('Send')
        sendButton.clicked.connect(self.sendMessage)
        send_message_layout.addWidget(sendButton)

        chat_layout.addLayout(send_message_layout)

        main_layout.addLayout(chat_layout)
        '''
        Set up the UI for the friends list.
        '''
        self.friendsList = QTextBrowser()
        self.friendsList.setReadOnly(True)
        self.friendsList.setFixedWidth(100)
        main_layout.addWidget(self.friendsList)


    def sendMessage(self):
        message = self.messageInput.text()
        if message:
            try:
                self.sock.sendall(f'{self.name}: {message}'.encode('ascii'))
                self.messageInput.clear()
            except BrokenPipeError:
                self.chatHistory.append("Server connection was lost.")

    def displayMessage(self, message):
        parts = message.split(":", 2)
        if len(parts) == 4:
            color, time, username, message = parts
            formatted_message = f'<span style="color:{color};">{time} :: {username} >> {message}</span>'
            print(formatted_message)
            self.chatHistory.append(formatted_message)
        else:
            self.chatHistory.append(message)

    def closeEvent(self, event):
        self.sock.close()
        self.receive_thread.terminate()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    welcome = WelcomeWindow()
    welcome.show()
    sys.exit(app.exec_())
