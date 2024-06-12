#non admin client code 
import socket
import threading
import getpass

# Get user name and create a client socket
name = input("Enter your name (Enter Your Password below): ")

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
                if new_msg == 'BAN':
                    print('CONNECTION FAILED: USER IS BANNED')
                    client.close()
                    st_th = True
                elif new_msg == 'PASS':
                    # Server requests password for existing users
                    password = getpass.getpass("Enter your password: ")
                    client.send(password.encode('ascii'))
                    response = client.recv(1024).decode('ascii')
                    if response == 'REFUSE':
                        print("CONNECTION FAILED: ENTER CORRECT PASSWORD")
                        st_th = True
                    elif response == 'NEW_PASS':
                        # Server requests a new password for new users
                        new_pw = getpass.getpass("Enter a new password: ")
                        client.send(new_pw.encode('ascii'))
                        print("Password set successfully!")
                    else:
                        print_help()
            else:
                print(msg)
        except:
            print("Error!")
            client.close()
            break

# Function to send messages to the server
def write():
    while True:
        global st_th
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
        elif msg.startswith('/quit'):
            # Send quit command to the server and terminate the thread
            client.send('/quit'.encode('ascii'))
            st_th = True
            break
        elif msg.startswith('/help'):
            # Print help information
            print_help()
        else:
             # Send regular messages to the server
            msg = '{}: {}'.format(name, msg)
            client.send(msg.encode('ascii'))

# Function to print help information
def print_help():
    print("To private message type /private client name: message ex:- /private John: Hi John! How are you?")
    print("To Quit /quit command")

# Create and start threads for receiving and sending messages
receive_thread = threading.Thread(target=recve)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
