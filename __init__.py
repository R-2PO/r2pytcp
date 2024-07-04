import socket
import threading
import time

import r2pytcp.sockutils as sockutils
import r2pytcp.http_protocol as http_protocol

__all__ = ["TCPServer", "ThreadTCPServer", "EchoHandler", "HTTPHandler"]

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

            self.handle_request(client_sock)

        
        #Close the socket
        self.serv_sock.close()

    def handle_request (self, client_sock: socket.socket):
        print("Not threaded")
        self.handler(client_sock)

    def stop (self):
        """
        Stop the server
        """
        self.is_running = False
        self.serv_sock.close ()




class ThreadTCPServer (TCPServer):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_request (self, client_sock: socket.socket):
        print("Threaded")
        thread = threading.Thread(target=self.handler, args=[client_sock])
        thread.daemon = True
        thread.start()



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
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()



class BaseTCPHandler:
    def __init__ (self, client_socket: socket.socket):
        """
        A basic TCP handler, does nothing but has some useful functions

        Arguments:
            -client_socket: the socket between the server and the client
        """
        self.client_socket = client_socket

    def close(self):
        """
        Close the socket with the client
        """
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()




class HTTPHandler:
    def __init__ (self, client_socket: socket.socket):
        """
        A basic HTTP handler for a TCPServer
        You can add any feature you want by adding or changing functions.

        Arguments:
            -client_socket: the socket between the server and the client
        """

        self.client_socket = client_socket

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

        self.headers = {} #Response headers

    def send_response (self, code: int, status_text: int=None, version: str="HTTP/1.1"):
        """
        Send the status line corresponding to the status code, message and protocol version specified
        
        Arguments:
            -code: the HTTP status code to send
            -status_text: the HTTP status text to send, automatically set if is None
            -version: the HTTP protocol version used as a string, defaults to 'HTTP/1.1'
        """
        if not status_text:
            if code in http_protocol.STATUS_TEXTS:
                status_text = http_protocol.STATUS_TEXTS[code]
            else:
                raise ValueError(f"Unknown status code: {code}, please specify a status text")

        self.client_socket.send(f"{version} {code} {status_text}\r\n".encode("iso-8859-1"))

    def send_headers (self):
        """
        Send the headers in self.headers using the TCPServer.
        Should only be used after sending the status line, by using self.send_response or custom code.
        """
        for header in self.headers:
            self.client_socket.send(f"{header}: {self.headers[header]}\r\n".encode("iso-8859-1"))
        self.client_socket.send(b"\r\n") #End the headers section

    def close (self):
        """
        Close the socket
        """
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()
