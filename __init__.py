import socket
import time

import sockutils

__all__ = ["TCPServer"]

class TCPServer:
    def __init__ (self, host: tuple, request_handler, **kwargs) -> None:
        """
        Create a TCP server
        
        Arguments:
            -host: server address in a tuple as (address, port)
            -request_handler: a request handler object
        """
        #TODO: Check all the kwargs

        self.host = host
        self.address = host[0]
        self.port = host[1]
        self.handler = request_handler
        self.allow_reuse_port = False

        if "allow_reuse_port" in kwargs:
            assert type(kwargs["allow_reuse_port"])==bool, f"Argument 'allow_reuse_port' should be of type bool, not {type(kwargs['allow_reuse_port'])}"
            self.allow_reuse_port = kwargs["allow_reuse_port"]

        self.is_running = True

    def run (self):
        """
        Start the server
        """
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.serv_sock.bind (self.host)

        self.serv_sock.listen(5)

        while self.is_running:
            #Accept a client
            client_sock, client_host = self.serv_sock.accept()

            #Handle the request
            self.handler(client_sock)
        
            #Close the connection
            client_sock.close()
        
        #Close the socket
        self.serv_sock.close()

    def stop (self):
        self.is_running = False
        self.serv_sock.close ()




class EchoHandler:
    def __init__ (self, client_socket: socket.socket):
        """
        A basic echo handler for a TCPServer
        Prints and sends back any data sent by the client

        Arguments:
            -client_socket: the socket between the server and the client
        """
        data = sockutils.recv_until_end(client_socket)
        client_socket.send(data)
        print(data.decode())



class HTTPHandler:
    def __init__ (self, client_socket: socket.socket):
        """
        A basic HTTP handler for a TCPServer
        You can add any feature you want by adding or changing functions.

        Arguments:
            -client_socket: the socket between the server and the client
        """

        #Get the request line
        self.request_line = b""
        while self.request_line[-2:] != b"\r\n":
            self.request_line += client_socket.recv(1)
        self.request_line = self.request_line[:-2].decode("iso-8859-1")
        self.method, self.path, self.request_version = self.request_line.split(" ", 2)

        #Get the headers
        self.request_headers = {}
        while True:
            header_line = client_socket.recv(2)
            while header_line[-2:] != b"\r\n":
                header_line += client_socket.recv(1)
                
            #Detect the end of the headers
            if header_line == b"\r\n":
                break
            #Decode the header line
            header_line = header_line.decode("iso-8859-1")
            #Store the header
            self.request_headers[header_line.split(": ", 1)[0]] = header_line.split(": ", 1)[1][:-2]




#Example
if __name__ == "__main__":
    server = TCPServer(("0.0.0.0", 3500), HTTPHandler, allow_reuse_port=True)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
