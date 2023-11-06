import socket

def recv_until_end (sock: socket.socket) -> bytes:
    """
    Same as socket.recv, but reads until nothing else is sent

    Arguments:
        -sock: the socket to read data from

    Returns:
        The received data
    """
    data = b""
    new_data = b"aaaaaaaaaa"  #Length of 10 to start the loop
    while len(new_data) == 10:
        new_data = sock.recv(10)
        data += new_data
    return data
