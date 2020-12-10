import socket

host, port = "192.168.1.87", 1234
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def recv(): 
    try:
        client.bind((host, port))
    finally:
        pass
    client.listen(10)
    print "Start Listening..."
    
    while True:
        conn, addr = client.accept()
        print "client with address: ", addr, " is connected."
        data = conn.recv(1024)
        print "Recieved this data: <", data, "> from the client."
            
    client.close()
recv()
