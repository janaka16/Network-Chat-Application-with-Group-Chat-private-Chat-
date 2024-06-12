# Server code

import socket
import threading

# Server configuration
host = '127.1.1.1'
port = 60000

# Create a socket for the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists to store connected clients, their names, and passwords
clients = []
names = []
passwords = {}

# Function to broadcast messages to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Function to handle private messages between clients
def handle_private_message(sender, receiver, message):
    sender_index = names.index(sender)
    receiver_index = names.index(receiver)
    receiver_client = clients[receiver_index]
    sender_name = names[sender_index]

    private_msg = f'(Private) {sender_name}: {message}'
    receiver_client.send(private_msg.encode('ascii'))

# Function to handle individual clients
def handle(client):
    while True:
        try:
            txt = message = client.recv(1024)
            if txt.decode('ascii').startswith('/private'):
                private_msg = txt.decode('ascii')[9:]
                receiver, private_message = private_msg.split(':', 1)
                handle_private_message(sender=names[clients.index(client)], receiver=receiver, message=private_message)
            elif txt.decode('ascii').startswith('KICK'):
                # Kick user command for admin
                if names[clients.index(client)] == 'admin':
                    name_to_kick = txt.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command refused!!!'.encode('ascii'))
            elif txt.decode('ascii').startswith('BAN'):
                # Ban user command for admin
                if names[clients.index(client)] == 'admin':
                    name_to_ban = txt.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!!')
                else:
                    client.send('Command refused!!!'.encode('ascii'))
            elif txt.decode('ascii').startswith('/quit'):
                # Handle client disconnection
                name = names[clients.index(client)]
                broadcast(f'{name} left the chat!'.encode('ascii'))
                index = clients.index(client)
                clients.remove(client)
                names.remove(name)
                client.close()
                break  
            else:
                broadcast(message)
                # Handle socket errors and client disconnection
        except socket.error:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                name = names[index]
                broadcast(f'{name} left the chat!'.encode('ascii'))
                names.remove(name)
                break
# Function to accept new connections
def recve():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Initial communication with the client
        client.send('NICK'.encode('ascii'))
        # Receive client name
        name = client.recv(1024).decode('ascii')
        try:
            with open('bans.txt', 'r') as f:
                bans = f.readlines()

            if name + '\n' in bans:
                client.send('BAN'.encode('ascii'))
                client.close()
                continue
        except (FileNotFoundError, PermissionError):
            # Create or handle errors when opening 'bans.txt'
            with open('bans.txt', 'a'):
                pass
            print("Warning: 'bans.txt' not found or permission error. An empty file has been created.")

        # Admin login with hardcoded password
        if name == 'admin':
            client.send('PASS'.encode('ascii'))
            pw_attempt = client.recv(1024).decode('ascii')

            if pw_attempt != 'adminpassword':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue
        # Existing user login with password
        if name in passwords:
            client.send('PASS'.encode('ascii'))
            pw_attempt = client.recv(1024).decode('ascii')

            if pw_attempt != passwords[name]:
                client.send('REFUSE'.encode('ascii'))
                print(f"Password incorrect for {name}. Connection refused.")
                client.close()
                continue
        else:
            # New user registration with password
            client.send('NEW_PASS'.encode('ascii'))
            new_pw = client.recv(1024).decode('ascii')
            passwords[name] = new_pw
            with open('passwords.txt', 'a') as f:
                f.write(f'{name}:{new_pw}\n')

        # Add the client to the list of connected clients
        names.append(name)
        clients.append(client)

        print(f'Name of client is {name}!')
        broadcast(f'{name} joined the chat!'.encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Create a new thread to handle the client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Function to kick a user from the server
def kick_user(name):
    if name in names:
        name_index = names.index(name)
        clients_to_kick = clients[name_index]
        clients.remove(clients_to_kick)
        clients_to_kick.send('You were kicked out of the server'.encode('ascii'))
        clients_to_kick.close()
        names.remove(name)
        broadcast(f'{name} kicked out of the server!'.encode('ascii'))

# Start the server
print("Server is working")
recve()
