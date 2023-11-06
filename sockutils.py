import socket

def recv_until_end (sock: socket.socket) -> bytes:
    data = b""
    new_data = b"aaaaaaaaaa"  #Length of 10 to start the loop
    while len(new_data) == 10:
        new_data = sock.recv(10)
        data += new_data
    return data
