import socket

s=socket.socket()       # arguments(IPV4, TCP)
HOST1='192.168.0.55'        # IPV4 address of the server

PORT=7070               # use any port between 4000 and 65000
s.bind((HOST1,PORT))    # assigns the socket with an address
s.listen(5)             # accept no. of incoming connections
while True:
    clientsocket, address = s.accept()          # stores the socket details in 2 variables
    print(f"Connection from {address} has been established")
    clientsocket.send(bytes("Welcome to the server, \nWhat is your name?",'utf-8'))     # encodes a string into bytes and sends it to client
    name=clientsocket.recv(10)          # recieves a packet of 10 bytes from the client ie the name
    name=name.decode('utf-8')           # decodes the bytes into string format
    print("\nConnecting to ",name," . . .")
    count=0                             # while counter
    while True:
        count+=1
        LETTER=clientsocket.recv(1)                                 # recieves an alphabet whose ASCII value is the size of the message
        SIZE=ord(LETTER.decode('utf-8'))                            # ord() returns the ASCII value of a character
        msg=clientsocket.recv(SIZE)                                 # recieving the actual msg
        if count%2000==0:                                           # preventing print in each loop
            print(msg.decode('utf-8'),"\n")
    clientsocket.close()                 