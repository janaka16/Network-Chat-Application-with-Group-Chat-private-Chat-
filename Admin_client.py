#ADMIN CLIENT CODE

import socket
import threading

# create a client socket
name = 'admin' # Admin's predefined name
pw = input("Enter your password for admin: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.1.1.1', 60000))

# Flag to control thread termination
st_th = False

# Function to receive messages from the server
def recve():
    while True:
        global st_th
        if st_th:
            break

        try:
            msg = client.recv(1024).decode('ascii')
            if msg == 'NICK':
                # Server requests client's name
                client.send(name.encode('ascii'))
                new_msg = client.recv(1024).decode('ascii')
                if new_msg == 'PASS':
                    # Server requests password for the admin
                    client.send(pw.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("CONNECTION FAILED: ENTER CORRECT PASSWORD")
                        st_th = True
                elif new_msg == 'BAN':
                    print('CONNECTION FAILED: USER IS BANNED')
                    client.close()
                    st_th = True

            else:
                print(msg)

        except:
            print("Error!")
            client.close()
            break

# Function to send messages to the server
def write():
    while True:
        if st_th:
            break
        msg = input('')
        if msg.startswith('/private'):
            try:
                _, rest = msg.split(' ', 1)
                receiver, private_message = rest.split(':', 1)
                client.send(f'/private {receiver}:{private_message}'.encode('ascii'))
            except ValueError:
                print("Invalid private message format. Use /private <receiver>:<message>")
        else:
            msg = '{}: {}'.format(name, msg)
            if msg[len(name)+2:].startswith('/'):
                if msg[len(name)+2:].startswith('/kick'): # Admin can kick a user from the server
                    client.send(f'KICK {msg[len(name)+2+6:]}'.encode('ascii'))
                elif msg[len(name)+2:].startswith('/ban'):  # Admin can ban a user from the server
                    client.send(f'BAN {msg[len(name)+2+5:]}'.encode('ascii'))
            else:
                client.send(msg.encode('ascii')) # Send regular messages to the server

# Create and start threads for receiving and sending messages
receive_thread = threading.Thread(target=recve)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
