import socket
import time

__all__ = ["TCPServer"]

class TCPServer:
    def __init__ (self, host: tuple, request_handler) -> None:
        """
        Create a TCP server
        
        Arguments:
            -host: server address in a tuple as (address, port)
            -request_handler: a request handler object
        """

        self.host = host
        self.address = host[0]
        self.port = host[1]
        self.handler = request_handler

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
        self.serv_sork.close ()


if __name__ == "__main__":
    server = TCPServer(("127.0.0.1", 80), None)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
