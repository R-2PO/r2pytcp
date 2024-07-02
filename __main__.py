from r2pytcp import *

class Handler (HTTPHandler):
    def __init__ (self, client_socket):
        super().__init__(client_socket)
        self.close()

if __name__ == "__main__":
    server = TCPServer(("0.0.0.0", 3500), Handler, allow_reuse_port=True)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
